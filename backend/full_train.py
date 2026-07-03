"""
完整训练脚本 - 使用全部HUST-OBC类别 + 未知字推断准备

特性:
1. 训练全部1588个已释读类别
2. 使用置信度阈值检测未知/污染字
3. 输出top-k预测用于AI推断

使用方法:
1. 确保HUST-OBC数据集在 data/raw/HUST-OBC/
2. 运行: python full_train.py
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import torchvision.transforms as transforms
from torchvision.models import resnet18, ResNet18_Weights, resnet50, ResNet50_Weights
from pathlib import Path
import json
import random
from tqdm import tqdm
import os

# 配置
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
MODEL_DIR = Path(__file__).parent / "model"
HUST_DIR = RAW_DIR / "HUST-OBC"

# 超参数
BATCH_SIZE = 32  # 降低以适配显存
EPOCHS = 30
LEARNING_RATE = 0.001
NUM_WORKERS = 0 if os.name == 'nt' else 4
CONFIDENCE_THRESHOLD = 0.5  # 低于此阈值视为未知/污染字

# 图像变换 (增强以应对污染/残缺)
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomRotation(15),
    transforms.RandomAffine(0, translate=(0.1, 0.1)),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.RandomErasing(p=0.1),  # 模拟残缺
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])
])

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])
])


class HUSTDataset(Dataset):
    """HUST-OBC数据集"""
    
    def __init__(self, data_dir, transform=None, max_classes=None):
        self.data_dir = Path(data_dir)
        self.transform = transform
        self.samples = []
        self.class_to_idx = {}
        
        if not self.data_dir.exists():
            print(f"[警告] 数据集目录不存在: {self.data_dir}")
            return
        
        # 扫描类别
        classes = sorted([d.name for d in self.data_dir.iterdir() if d.is_dir()])
        if max_classes:
            classes = classes[:max_classes]
        self.class_to_idx = {cls_name: i for i, cls_name in enumerate(classes)}
        
        print(f"[信息] 数据集: {len(self.class_to_idx)} 个类别")
        
        # 收集样本
        for cls_name, cls_idx in self.class_to_idx.items():
            cls_dir = self.data_dir / cls_name
            if not cls_dir.exists():
                continue
            
            for img_path in cls_dir.glob("*.*"):
                if img_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp']:
                    self.samples.append((str(img_path), cls_idx))
        
        print(f"[信息] 总样本数: {len(self.samples)}")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        
        from PIL import Image
        image = Image.open(img_path).convert("RGB")
        
        if self.transform:
            image = self.transform(image)
        
        return image, label


class OracleResNet(nn.Module):
    """基于ResNet50的甲骨文识别模型（更强的特征提取能力）"""
    
    def __init__(self, num_classes, pretrained=True, weights_path=None):
        super().__init__()
        
        if pretrained:
            if weights_path and Path(weights_path).exists():
                print(f"[加载本地权重] {weights_path}")
                self.model = resnet50()
                state_dict = torch.load(weights_path, map_location='cpu')
                self.model.load_state_dict(state_dict)
            else:
                print("[使用] ResNet50 ImageNet预训练权重")
                weights = ResNet50_Weights.DEFAULT
                self.model = resnet50(weights=weights)
        else:
            self.model = resnet50()
        
        # 修改最后的全连接层
        num_features = self.model.fc.in_features
        self.model.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, num_classes)
        )
    
    def forward(self, x):
        return self.model(x)
    
    def predict_with_confidence(self, x):
        """返回预测结果+置信度+top-k预测"""
        with torch.no_grad():
            outputs = self.model(x)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
            
            # Top-5预测
            top5_conf, top5_idx = torch.topk(probabilities, 5, dim=1)
            
        return {
            'predicted': predicted.item(),
            'confidence': confidence.item(),
            'top5': [
                {'class': idx.item(), 'confidence': conf.item()}
                for idx, conf in zip(top5_idx[0], top5_conf[0])
            ],
            'is_unknown': confidence.item() < CONFIDENCE_THRESHOLD
        }


def train_one_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    progress_bar = tqdm(dataloader, desc="训练", leave=False)
    
    for images, labels in progress_bar:
        images, labels = images.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()
        
        progress_bar.set_postfix({
            'loss': f'{loss.item():.4f}',
            'acc': f'{correct/total:.4f}'
        })
    
    avg_loss = running_loss / total
    accuracy = correct / total
    return avg_loss, accuracy


def validate(model, dataloader, criterion, device):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for images, labels in tqdm(dataloader, desc="验证", leave=False):
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
    
    avg_loss = running_loss / total
    accuracy = correct / total
    return avg_loss, accuracy


def main():
    print("=" * 60)
    print("甲骨文识别 - 全类别训练 + 未知字推断准备")
    print("=" * 60)
    print(f"\n使用设备: {DEVICE}")
    print(f"置信度阈值: {CONFIDENCE_THRESHOLD} (低于此值视为未知字)")
    
    # 检查数据集
    train_dir = HUST_DIR / "deciphered"
    if not train_dir.exists():
        print(f"[错误] 未找到HUST-OBC数据集: {train_dir}")
        print("\n请先下载数据集:")
        print("  1. 从 https://www.modelscope.cn/datasets/wpj2003/HUST-OBC")
        print("  2. 解压到 data/raw/HUST-OBC/")
        return
    
    # 使用全部类别
    available_classes = len([d for d in train_dir.iterdir() if d.is_dir()])
    print(f"\n使用全部 {available_classes} 个已释读类别...")
    train_dataset = HUSTDataset(train_dir, transform=train_transform)
    
    if len(train_dataset) == 0:
        print("[错误] 训练集为空")
        return
    
    # 划分训练/验证集
    train_size = int(0.8 * len(train_dataset))
    val_size = len(train_dataset) - train_size
    train_subset, val_subset = torch.utils.data.random_split(train_dataset, [train_size, val_size])
    
    print(f"训练集: {len(train_subset)} 样本")
    print(f"验证集: {len(val_subset)} 样本")
    
    # 创建数据加载器
    train_loader = DataLoader(train_subset, batch_size=BATCH_SIZE, shuffle=True, num_workers=NUM_WORKERS)
    val_loader = DataLoader(val_subset, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS)
    
    # 创建模型
    num_classes = len(train_dataset.class_to_idx)
    model = OracleResNet(num_classes=num_classes, pretrained=True).to(DEVICE)
    
    print(f"\n模型: ResNet50 (ImageNet预训练)")
    print(f"分类数: {num_classes}")
    print(f"参数量: {sum(p.numel() for p in model.parameters()):,}")
    
    # 损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=5, factor=0.5)
    
    # 训练循环
    best_acc = 0.0
    
    for epoch in range(EPOCHS):
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, DEVICE)
        val_loss, val_acc = validate(model, val_loader, criterion, DEVICE)
        
        scheduler.step(val_loss)
        
        print(f"\nEpoch [{epoch+1}/{EPOCHS}]")
        print(f"  训练 Loss: {train_loss:.4f} | 训练准确率: {train_acc:.4f}")
        print(f"  验证 Loss: {val_loss:.4f} | 验证准确率: {val_acc:.4f}")
        
        # 保存最佳模型
        if val_acc > best_acc:
            best_acc = val_acc
            checkpoint = {
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'accuracy': val_acc,
                'class_to_idx': train_dataset.class_to_idx,
                'confidence_threshold': CONFIDENCE_THRESHOLD,
            }
            torch.save(checkpoint, MODEL_DIR / "oracle_recognition_full.pth")
            print(f"  ✓ 保存最佳模型 (验证准确率: {val_acc:.4f})")
        
        print("-" * 50)
    
    print(f"\n训练完成！最佳验证准确率: {best_acc:.4f}")
    print(f"模型已保存到: {MODEL_DIR / 'oracle_recognition_full.pth'}")
    print(f"\n置信度阈值: {CONFIDENCE_THRESHOLD}")
    print("  - 预测置信度 >= 阈值: 认为是已知字")
    print("  - 预测置信度 < 阈值: 认为是未知/污染/残缺字，需要AI推断")


if __name__ == "__main__":
    main()
