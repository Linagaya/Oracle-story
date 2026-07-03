"""
Baseline模型下载脚本
下载预训练模型作为起点，包括:
1. YOLOv8s (单字检测)
2. ResNet50 (甲骨文分类, HUST-OBC官方验证模型, 94.6%准确率)
3. ResNet18 (ImageNet预训练, 备用)
"""

import urllib.request
import os
from pathlib import Path
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

MODEL_DIR = Path(__file__).parent / "model"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODELS = {
    "yolov8s": {
        "url": "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8s.pt",
        "filename": "yolov8s.pt",
        "size": "21.5MB",
        "description": "YOLOv8-Small 目标检测预训练模型，用于甲骨拓片单字分割",
        "fallback_url": "https://huggingface.co/ultralytics/yolov8s/resolve/main/yolov8s.pt"
    },
    "resnet50_hust_obc": {
        "url": "https://figshare.com/ndownloader/files/45372025",
        "filename": "max_val_acc.pth",
        "size": "~100MB",
        "description": "HUST-OBC官方ResNet50验证模型，测试集准确率94.6%",
        "fallback_url": None
    },
    "resnet18_imagenet": {
        "url": "https://download.pytorch.org/models/resnet18-f37072fd.pth",
        "filename": "resnet18-f37072fd.pth",
        "size": "44.7MB",
        "description": "ResNet18 ImageNet预训练模型，可用作迁移学习起点",
        "fallback_url": None
    }
}


def download_model(name, info, force=False):
    """下载单个模型"""
    filepath = MODEL_DIR / info["filename"]
    
    if filepath.exists() and not force:
        print(f"[跳过] {name}: {filepath} (已存在)")
        return True
    
    print(f"\n下载 {name}...")
    print(f"  描述: {info['description']}")
    print(f"  大小: {info['size']}")
    print(f"  目标: {filepath}")
    
    urls = [info["url"]]
    if info.get("fallback_url"):
        urls.append(info["fallback_url"])
    
    for url in urls:
        try:
            print(f"  尝试: {url}")
            urllib.request.urlretrieve(url, filepath)
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"[成功] {name}: {size_mb:.1f}MB")
            return True
        except Exception as e:
            print(f"[失败] {str(e)[:100]}")
            continue
    
    print(f"[错误] {name} 所有下载源均失败")
    return False


def main():
    print("=" * 60)
    print("甲骨文识别 Baseline 模型下载")
    print("=" * 60)
    
    print("\n可用模型:")
    for name, info in MODELS.items():
        exists = (MODEL_DIR / info["filename"]).exists()
        status = "[已下载]" if exists else "[未下载]"
        print(f"  {status} {name}: {info['description']} ({info['size']})")
    
    print("\n" + "-" * 60)
    print("推荐下载顺序:")
    print("  1. resnet18_imagenet (最快，44MB，可立即用于迁移学习)")
    print("  2. yolov8s (目标检测预训练，21MB)")
    print("  3. resnet50_hust_obc (官方模型，94.6%准确率，较大)")
    
    choice = input("\n请选择下载 (1/2/3/all/quit): ").strip().lower()
    
    if choice == "quit":
        return
    
    download_list = []
    if choice in ["1", "all"]:
        download_list.append("resnet18_imagenet")
    if choice in ["2", "all"]:
        download_list.append("yolov8s")
    if choice in ["3", "all"]:
        download_list.append("resnet50_hust_obc")
    
    for name in download_list:
        if name in MODELS:
            download_model(name, MODELS[name])
    
    print("\n" + "=" * 60)
    print("下载完成!")
    print("=" * 60)
    
    # 列出已下载的模型
    downloaded = [f for f in MODEL_DIR.iterdir() if f.suffix in ['.pth', '.pt']]
    if downloaded:
        print("\n已下载的模型:")
        for f in downloaded:
            size_mb = f.stat().st_size / (1024 * 1024)
            print(f"  {f.name}: {size_mb:.1f}MB")
    
    if not any(MODEL_DIR / m["filename"] in downloaded for m in MODELS.values() if "hust" in m[0].lower()):
        print("\n提示: 如需下载HUST-OBC官方ResNet50模型，请手动从以下地址下载:")
        print("  Figshare: https://figshare.com/articles/dataset/HUST-OBC/25311483")
        print("  ModelScope: https://www.modelscope.cn/datasets/wpj2003/HUST-OBC")


if __name__ == "__main__":
    main()
