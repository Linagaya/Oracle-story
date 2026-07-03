"""
甲骨文数据集下载和预处理脚本
支持多个公开数据集:
1. HUST-OBC (华中科技大学, 2024) - 77,064张已释读图像 + 62,989张未释读图像
2. OBI-100/OBI-125 - 早期公开数据集
3. Oracle-20k - 2万+甲骨文图像

数据集来源:
- HUST-OBC: https://github.com/Pengjie-W/HUST-OBC
- 论文: https://arxiv.org/pdf/2401.15365
"""

import urllib.request
import zipfile
import os
from pathlib import Path
import json
import ssl

# 禁用SSL验证（某些服务器可能需要）
ssl._create_default_https_context = ssl._create_unverified_context

# 配置
DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
TRAIN_DIR = DATA_DIR / "training" / "train"
VAL_DIR = DATA_DIR / "training" / "val"
TEST_DIR = DATA_DIR / "test"

# 创建目录
for d in [RAW_DIR, TRAIN_DIR, VAL_DIR, TEST_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def download_hust_obc():
    """
    下载HUST-OBC数据集
    论文: An open dataset for oracle bone script recognition and decipherment
    GitHub: https://github.com/Pengjie-W/HUST-OBC
    """
    print("\n" + "="*60)
    print("HUST-OBC 数据集下载")
    print("="*60)
    
    urls = {
        "github": "https://github.com/Pengjie-W/HUST-OBC",
        "paper": "https://arxiv.org/abs/2401.15365",
    }
    
    print("\n数据集信息:")
    print("  - 已释读字符: 77,064张图像, 1,588个类别")
    print("  - 未释读字符: 62,989张图像, 9,411个类别")
    print("  - 总计: 140,053张图像")
    print("\n下载方式:")
    print("  方式1: 从GitHub下载")
    print(f"    {urls['github']}")
    print("  方式2: 从论文附件下载")
    print(f"    {urls['paper']}")
    print("\n[注意] 由于数据集较大(579MB),建议手动下载后放入 data/raw/ 目录")
    
    # 创建说明文件
    readme = RAW_DIR / "HUST-OBC_README.txt"
    readme.write_text(f"""
HUST-OBC 数据集下载说明
========================

数据集: HUST-OBC (Oracle Bone Character Dataset)
论文: An open dataset for oracle bone script recognition and decipherment
作者: Pengjie Wang, Kaile Zhang, Yuliang Liu, et al.
发表: Scientific Data, 2024

下载链接:
1. GitHub: {urls['github']}
2. 论文: {urls['paper']}
3. PubMed: https://pubmed.ncbi.nlm.nih.gov/39242622/

数据集大小: ~579MB (HUST-OBC.zip)

使用步骤:
1. 从上述链接下载 HUST-OBC.zip
2. 将zip文件放入当前目录 (data/raw/)
3. 运行: python process_hust_obc.py

数据集结构:
HUST-OBC/
├── deciphered/          # 已释读字符
│   ├── class_001/       # 每个类别一个文件夹
│   │   ├── img001.png
│   │   └── ...
│   └── ...
└── undeciphered/        # 未释读字符
    ├── class_001/
    └── ...
""")
    
    print(f"\n说明文件已保存到: {readme}")
    return urls


def download_sample_data():
    """下载示例甲骨文图像用于测试"""
    print("\n" + "="*60)
    print("下载示例甲骨文图像")
    print("="*60)
    
    # 创建示例目录
    sample_dir = DATA_DIR / "sample"
    sample_dir.mkdir(exist_ok=True)
    
    print("\n📝 示例图像将用于:")
    print("  - 测试识别API")
    print("  - 演示前端功能")
    print("  - 开发调试")
    
    print("\n⚠️  请准备以下甲骨文字形的图像:")
    oracle_chars = ["日", "月", "山", "水", "火", "木", "金", "土", "人", "口"]
    for char in oracle_chars:
        char_dir = sample_dir / char
        char_dir.mkdir(exist_ok=True)
        print(f"  - {char}/  (放入{char}字的拓片图像)")
    
    print(f"\n✅ 示例目录已创建: {sample_dir}")
    print("请将甲骨文拓片图像放入对应文件夹")


def create_process_script():
    """创建数据处理脚本"""
    script = Path(__file__).parent / "process_hust_obc.py"
    content = '''"""
HUST-OBC数据集处理脚本
将下载的HUST-OBC数据集转换为训练格式
"""

import shutil
from pathlib import Path
import random
from tqdm import tqdm

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
HUST_DIR = RAW_DIR / "HUST-OBC"
TRAIN_DIR = DATA_DIR / "training" / "train"
VAL_DIR = DATA_DIR / "training" / "val"
TEST_DIR = DATA_DIR / "test"

# 配置
VAL_SPLIT = 0.15  # 验证集比例
TEST_SPLIT = 0.10  # 测试集比例


def process_dataset():
    """处理HUST-OBC数据集"""
    
    if not HUST_DIR.exists():
        print(f"[ERROR] 未找到HUST-OBC数据集: {HUST_DIR}")
        print("请先下载HUST-OBC数据集并放入 data/raw/ 目录")
        return
    
    print("\\n开始处理HUST-OBC数据集...")
    print(f"数据目录: {HUST_DIR}")
    
    # 清空目标目录
    for d in [TRAIN_DIR, VAL_DIR, TEST_DIR]:
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
    
    # 处理已释读字符
    deciphered_dir = HUST_DIR / "deciphered"
    if deciphered_dir.exists():
        print("\\n[INFO] 处理已释读字符...")
        
        for char_dir in tqdm(list(deciphered_dir.iterdir())):
            if not char_dir.is_dir():
                continue
            
            char_name = char_dir.name
            images = list(char_dir.glob("*.png")) + list(char_dir.glob("*.jpg"))
            
            if len(images) == 0:
                continue
            
            # 随机打乱
            random.shuffle(images)
            
            n = len(images)
            n_val = max(1, int(n * VAL_SPLIT))
            n_test = max(1, int(n * TEST_SPLIT))
            n_train = n - n_val - n_test
            
            # 创建目标目录
            train_char_dir = TRAIN_DIR / char_name
            val_char_dir = VAL_DIR / char_name
            test_char_dir = TEST_DIR / char_name
            
            for d in [train_char_dir, val_char_dir, test_char_dir]:
                d.mkdir(parents=True, exist_ok=True)
            
            # 分配数据
            for i, img in enumerate(images):
                if i < n_train:
                    shutil.copy(img, train_char_dir / img.name)
                elif i < n_train + n_val:
                    shutil.copy(img, val_char_dir / img.name)
                else:
                    shutil.copy(img, test_char_dir / img.name)
        
        print(f"\\n[SUCCESS] 处理完成!")
        print(f"  训练集: {sum(1 for _ in TRAIN_DIR.iterdir())} 个类别")
        print(f"  验证集: {sum(1 for _ in VAL_DIR.iterdir())} 个类别")
        print(f"  测试集: {sum(1 for _ in TEST_DIR.iterdir())} 个类别")
    else:
        print(f"[WARNING] 未找到已释读字符目录: {deciphered_dir}")


if __name__ == "__main__":
    process_dataset()
'''
    script.write_text(content, encoding='utf-8')
    
    print(f"\n数据处理脚本已创建: {script}")


def main():
    print("="*60)
    print("甲骨文数据集下载工具")
    print("="*60)
    
    # 1. 下载HUST-OBC数据集信息
    download_hust_obc()
    
    # 2. 创建示例数据目录
    download_sample_data()
    
    # 3. 创建数据处理脚本
    create_process_script()
    
    print("\n" + "="*60)
    print("后续步骤")
    print("="*60)
    print("""
1. 手动下载HUST-OBC数据集:
   - GitHub: https://github.com/Pengjie-W/HUST-OBC
   - 论文: https://arxiv.org/abs/2401.15365

2. 将下载的HUST-OBC.zip放入 data/raw/ 目录

3. 解压数据集:
   cd data/raw
   unzip HUST-OBC.zip

4. 运行数据处理脚本:
   cd backend
   python process_hust_obc.py

5. 开始训练:
   python train.py
""")


if __name__ == "__main__":
    main()