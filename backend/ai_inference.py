"""
AI推断未知/污染/残缺甲骨文字意

策略:
1. 字形分析: 分析笔画、部首、结构特征
2. 上下文推断: 结合拓片中相邻字的语义
3. 相似字比对: 与已知字形特征库对比
4. 综合推断: 结合以上信息给出最可能的含义

使用方法:
1. 训练好模型后运行
2. 输入: 未知字的图像
3. 输出: 推断含义 + 可信度
"""

import torch
from PIL import Image
import torchvision.transforms as transforms
from pathlib import Path
import json

# 配置
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_DIR = Path(__file__).parent / "model"
MODEL_PATH = MODEL_DIR / "oracle_recognition_full.pth"


class OracleCharacterAnalyzer:
    """甲骨文字形分析器"""
    
    def __init__(self):
        self.model = None
        self.class_to_idx = {}
        self.idx_to_char = {}
        self.confidence_threshold = 0.5
        
        if MODEL_PATH.exists():
            self.load_model()
    
    def load_model(self):
        checkpoint = torch.load(MODEL_PATH, map_location=DEVICE)
        self.class_to_idx = checkpoint['class_to_idx']
        self.idx_to_char = {v: k for k, v in self.class_to_idx.items()}
        self.confidence_threshold = checkpoint.get('confidence_threshold', 0.5)
        
        # 构建字形特征库（用于相似字比对）
        self.build_feature_library()
    
    def build_feature_library(self):
        """构建已知字的特征表示（用于相似性比对）"""
        # 这里可以提取每个类的特征向量
        # 简化版：使用类别映射
        self.char_features = {}
        for char, idx in self.class_to_idx.items():
            self.char_features[char] = idx
    
    def analyze_character(self, image_path):
        """
        分析单个甲骨文字
        
        返回: {
            'status': 'known' | 'unknown' | 'ambiguous',
            'prediction': '预测字符',
            'confidence': 置信度,
            'top_k': top-k预测,
            'inference': AI推断结果 (未知字时)
        }
        """
        image = Image.open(image_path).convert("RGB")
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5], std=[0.5])
        ])
        
        x = transform(image).unsqueeze(0).to(DEVICE)
        
        with torch.no_grad():
            outputs = self.model.model(x)
            probabilities = torch.softmax(outputs, dim=1)
            top5_conf, top5_idx = torch.topk(probabilities, 5, dim=1)
        
        result = {
            'status': 'unknown',
            'prediction': None,
            'confidence': 0.0,
            'top5': [],
            'inference': None
        }
        
        for i in range(5):
            char = self.idx_to_char.get(top5_idx[0][i].item(), '?')
            conf = top5_conf[0][i].item()
            result['top5'].append({
                'char': char,
                'confidence': round(conf * 100, 2)
            })
        
        top_conf = top5_conf[0][0].item()
        top_char = self.idx_to_char.get(top5_idx[0][0].item(), '?')
        
        result['confidence'] = round(top_conf * 100, 2)
        
        if top_conf >= self.confidence_threshold:
            # 高置信度 -> 已知字
            result['status'] = 'known'
            result['prediction'] = top_char
        else:
            # 低置信度 -> 未知/污染/残缺字
            result['status'] = 'unknown'
            result['prediction'] = f"[{top_char}]"
            
            # AI推断
            result['inference'] = self.infer_unknown_character(
                top_char, top_conf, result['top5'], image_path
            )
        
        return result
    
    def infer_unknown_character(self, top_pred, confidence, top5, image_path):
        """
        对未知字进行AI推断
        
        策略:
        1. 分析top-prediction的特征
        2. 比对相似字形
        3. 给出可能的含义范围
        """
        inference = {
            'possible_meanings': [],
            'reasoning': '',
            'similarity_matches': [],
            'confidence_estimate': 0.0
        }
        
        # 1. 基于top-predictions推断
        if len(top5) >= 2:
            # 如果top-2预测相近，可能是形近字
            if top5[0]['confidence'] - top5[1]['confidence'] < 10:
                inference['possible_meanings'].append(
                    f"可能是'{top5[0]['char']}'或'{top5[1]['char']}'的变体"
                )
        
        # 2. 字形相似性分析
        # 这里可以接入更复杂的特征分析
        if top5[0]['confidence'] < 30:
            inference['possible_meanings'].append(
                "字形特征不明显，可能是严重污染或残缺"
            )
        
        # 3. 综合推断
        if not inference['possible_meanings']:
            inference['possible_meanings'].append(
                f"最接近已知字'{top_pred}'，但置信度较低"
            )
        
        inference['reasoning'] = (
            f"模型预测为'{top_pred}'的置信度为{confidence:.1%}，"
            f"低于阈值{self.confidence_threshold:.0%}。"
            f"建议: 1)检查图像质量 2)比对相似字形 3)结合上下文推断"
        )
        
        inference['similarity_matches'] = top5[:3]
        inference['confidence_estimate'] = confidence * 0.5  # 未知字置信度减半
        
        return inference


def main():
    print("=" * 60)
    print("甲骨文AI推断系统")
    print("=" * 60)
    
    if not MODEL_PATH.exists():
        print(f"[错误] 未找到模型: {MODEL_PATH}")
        print("请先运行 full_train.py 训练模型")
        return
    
    analyzer = OracleCharacterAnalyzer()
    print(f"模型加载成功: {MODEL_PATH}")
    print(f"类别数: {len(analyzer.class_to_idx)}")
    print(f"置信度阈值: {analyzer.confidence_threshold}")
    
    # 测试
    sample_dir = Path(__file__).parent.parent / "data" / "sample"
    if sample_dir.exists():
        test_images = list(sample_dir.glob("**/*.png")) + list(sample_dir.glob("**/*.jpg"))
        
        if test_images:
            print(f"\n测试 {len(test_images)} 个样本...")
            for img_path in test_images[:5]:
                print(f"\n分析: {img_path.name}")
                result = analyzer.analyze_character(str(img_path))
                
                print(f"  状态: {result['status']}")
                print(f"  预测: {result['prediction']}")
                print(f"  置信度: {result['confidence']}%")
                print(f"  Top-5:")
                for pred in result['top5']:
                    print(f"    {pred['char']}: {pred['confidence']}%")
                
                if result['inference']:
                    print(f"  AI推断:")
                    print(f"    可能含义: {result['inference']['possible_meanings']}")
                    print(f"    推理: {result['inference']['reasoning']}")
        else:
            print("\n[提示] data/sample/ 目录下没有测试图像")


if __name__ == "__main__":
    main()
