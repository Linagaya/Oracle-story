"""
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
    
    print("\n开始处理HUST-OBC数据集...")
    print(f"数据目录: {HUST_DIR}")
    
    # 清空目标目录
    for d in [TRAIN_DIR, VAL_DIR, TEST_DIR]:
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
    
    # 处理已释读字符
    deciphered_dir = HUST_DIR / "deciphered"
    if deciphered_dir.exists():
        print("\n[INFO] 处理已释读字符...")
        
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
        
        print(f"\n[SUCCESS] 处理完成!")
        print(f"  训练集: {sum(1 for _ in TRAIN_DIR.iterdir())} 个类别")
        print(f"  验证集: {sum(1 for _ in VAL_DIR.iterdir())} 个类别")
        print(f"  测试集: {sum(1 for _ in TEST_DIR.iterdir())} 个类别")
    else:
        print(f"[WARNING] 未找到已释读字符目录: {deciphered_dir}")


if __name__ == "__main__":
    process_dataset()
