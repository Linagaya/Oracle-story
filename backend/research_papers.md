# 甲骨文AI识别 - 论文方法参考

## 核心论文列表

### 1. HUST-OBC 数据集 (2024)
- **论文**: An open dataset for oracle bone script recognition and decipherment
- **作者**: Pengjie Wang, Kaile Zhang, Yuliang Liu, et al.
- **发表**: Scientific Data, 2024
- **链接**: https://arxiv.org/abs/2401.15365
- **数据集**: https://github.com/Pengjie-W/HUST-OBC
- **要点**:
  - 77,064张已释读图像，1,588个类别
  - 62,989张未释读图像，9,411个类别
  - 使用ResNet50进行基线测试
  - 提供了完整的分类benchmark

### 2. MobileViT 甲骨文识别 (2025)
- **论文**: 基于 MobileViT 的甲骨文智能识别系统
- **方法**: MobileViT-S 主干网络
- **数据集**: 871个字符类别，约26,000张图片
- **准确率**: Top-1 80.22% (30 epochs)
- **关键技术**:
  - Mixup / CutMix 数据混合
  - 随机背景合成
  - 标签平滑
  - 长尾类保护机制

### 3. FM-MobileViT 拓片识别 (2025)
- **论文**: 基于FM-MobileViT网络的拓片甲骨文字识别
- **作者**: 李子含, 屈乐达, 刘思源 (沈阳理工大学)
- **发表**: 计算机应用研究, 2025
- **要点**:
  - 针对甲骨拓片的特殊优化
  - 处理噪声和背景干扰

### 4. OracleAgent 多模态推理 (2025)
- **论文**: ORACLEAGENT: A MULTIMODAL REASONING AGENT FOR ORACLE BONE SCRIPT RESEARCH
- **链接**: https://arxiv.org/pdf/2510.26114v1
- **要点**:
  - 首个甲骨文研究多模态推理Agent
  - 知识库构建
  - 模型工具链
  - 任务导向规划

### 5. 复旦大模型破译 (2025)
- **论文**: Specializing Large Models for Oracle Bone Script Interpretation
- **团队**: 复旦大学
- **方法**:
  - 基于Qwen2.5-VL-7B
  - 部首-象形双重匹配机制
  - 渐进式训练策略
- **数据集**: PD-OBS (47,157个汉字)
- **SOTA**: HUST-OBC和EV-OBC基准

### 6. OB-Radix 组件标注数据集 (2026)
- **论文**: Specializing Large Models for Oracle Bone Script Interpretation via Component-Grounded Multimodal Knowledge Augmentation
- **发表**: ACL 2026
- **数据集**: 1,022字符图像，1,853个细粒度组件图像

## 推荐方法 (适合比赛快速实现)

### 方案A: ResNet50 基线 (推荐新手)
```
优点:
- 实现简单，PyTorch官方支持
- HUST-OBC论文提供完整代码
- 可作为baseline快速验证

实现步骤:
1. 下载HUST-OBC数据集
2. 使用torchvision.models.resnet50
3. 修改最后全连接层为分类数
4. 训练20-30 epochs
5. 预期准确率: 70-75%
```

### 方案B: MobileViT-S (推荐进阶)
```
优点:
- 轻量级，推理速度快
- Top-1准确率80.22%
- 适合部署到Web服务

实现步骤:
1. pip install timm
2. 使用timm.create_model('mobilevit_s')
3. 添加数据增强(Mixup/CutMix)
4. 训练30 epochs
5. 预期准确率: 78-82%
```

### 方案C: 预训练迁移学习 (推荐快速出Demo)
```
优点:
- 利用ImageNet预训练权重
- 小样本也能取得好效果
- 适合比赛快速验证

实现步骤:
1. 使用ResNet18/34预训练模型
2. 冻结前几层，只训练分类头
3. 逐步解冻微调
4. 10-15 epochs即可
5. 预期准确率: 75-80%
```

## 数据增强策略

### 针对甲骨文的特殊增强
```python
# 1. 几何变换
- 随机旋转 (±15度)
- 随机平移 (±10%)
- 随机缩放 (0.9-1.1)

# 2. 噪声处理
- 高斯噪声 (模拟拓片噪声)
- 随机遮挡 (模拟残缺)
- 对比度调整

# 3. 高级增强
- Mixup: 混合两张图像
- CutMix: 裁剪粘贴
- RandomErasing: 随机擦除
```

## 训练配置建议

### 基线配置
```python
# 模型
model = resnet18(pretrained=True)
model.fc = nn.Linear(512, num_classes)

# 优化器
optimizer = Adam(lr=1e-3, weight_decay=1e-4)
scheduler = ReduceLROnPlateau(patience=5)

# 训练参数
epochs = 30
batch_size = 32
image_size = 224

# 数据增强
train_transform = Compose([
    RandomRotation(15),
    RandomAffine(0, translate=(0.1, 0.1)),
    ColorJitter(0.2, 0.2, 0.2),
    ToTensor(),
    Normalize([0.5], [0.5])
])
```

## 比赛亮点建议

1. **多模态交互**: 拍照识别 + 字源故事
2. **低资源AI**: 展示小样本下的鲁棒识别
3. **公益传播**: "认领一个甲骨文字"互动
4. **文化价值**: 冷门绝学 + 前沿AI的叙事

## 资源链接汇总

- HUST-OBC数据集: https://github.com/Pengjie-W/HUST-OBC
- 甲骨文大数据平台: http://www.yinqiwenyuan.com/
- AI Agent "殷契星智": 腾讯 + 安阳师范学院联合开发
- MobileViT实现: https://github.com/apple/ml-mobilevit
- timm模型库: https://github.com/huggingface/pytorch-image-models