from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import numpy as np
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from pathlib import Path
import io
from typing import List, Optional

# 导入甲骨文知识库
from oracle_knowledge import (
    analyze_ambiguous_character,
    generate_explanation,
    ORACLE_RADICALS,
    DIVINATION_CONTEXTS,
    guess_meaning_from_context
)

app = FastAPI(title="甲骨文AI识别系统", version="3.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_DIR = Path(__file__).parent / "model"
DATA_PATH = Path(__file__).parent.parent / "data"
CONFIDENCE_THRESHOLD = 0.5  # 低于此值视为未知/污染字

# 默认字源故事 (备用)
DEFAULT_STORIES = {
    "日": "象形字，甲骨文像太阳之形。本义为太阳，引申为白天、日子。",
    "月": "象形字，甲骨文像弯月之形。本义为月亮，引申为月份。",
    "山": "象形字，甲骨文像三座山峰并立之形。本义为山峰、山岭。",
    "水": "象形字，甲骨文像水流弯曲之形，中间是水，两边是水花。本义为水流，泛指水。",
    "火": "象形字，甲骨文像火焰向上燃烧之形。本义为火焰、燃烧。",
    "木": "象形字，甲骨文像树木之形，上为枝，下为根。本义为树木。",
    "人": "象形字，甲骨文像侧面站立的人形。本义为人类。",
    "口": "象形字，甲骨文像嘴巴张开之形。本义为嘴巴，引申为说话。",
    "雨": "象形字，甲骨文像天空落下雨滴之形。本义为下雨。",
    "卜": "象形字，甲骨文中像占卜时甲骨上出现的裂纹。本义为占卜。",
    "王": "象形字，甲骨文像斧钺之形，象征王权。本义为君王。",
    "大": "象形字，甲骨文像人正面站立张臂之形。本义为大。",
    "小": "指事字，甲骨文用三小点表示细小。本义为小。",
    "牛": "象形字，甲骨文像牛头正面之形，两角向上弯曲。本义为牛。",
    "羊": "象形字，甲骨文像羊头正面之形，两角向下弯曲。本义为羊。",
    "田": "象形字，甲骨文像井田划分之形。本义为田地，也指田猎。",
    "土": "象形字，甲骨文像地上土堆之形。本义为土地。",
    "鼎": "象形字，甲骨文像鼎器之形，三足两耳。本义为鼎，古代礼器。",
    "酉": "象形字，甲骨文像酒尊之形。本义为酒器，假借为地支酉。",
    "弓": "象形字，甲骨文像弓张之形。本义为弓。",
    "矢": "象形字，甲骨文像箭之形，有镞、杆、羽。本义为箭。",
    "戈": "象形字，甲骨文像戈之形，长柄横刃。本义为兵器。",
    "车": "象形字，甲骨文像车之形，有轮、轴、辕。本义为车。",
    "舟": "象形字，甲骨文像小船之形。本义为船。",
    "子": "象形字，甲骨文像婴儿之形，头大身小。本义为孩子。",
    "女": "象形字，甲骨文像女子跪坐双手交叉之形。本义为女性。",
    "母": "象形字，甲骨文在女字上加两点表示乳房。本义为母亲。",
    "目": "象形字，甲骨文像眼睛之形。本义为眼睛，引申为看。",
    "耳": "象形字，甲骨文像耳朵之形。本义为耳朵。",
    "自": "象形字，甲骨文像鼻子之形。本义为鼻子，假借为自己。",
    "止": "象形字，甲骨文像脚印之形。本义为脚，引申为停止。",
    "足": "象形字，甲骨文像脚之形。本义为脚。",
    "彳": "象形字，甲骨文像路口之形，与行走有关。",
    "辶": "会意字，与行走、道路有关。",
}

# 图像预处理
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])
])

from torchvision.models import resnet18

class OracleResNet(nn.Module):
    """基于ResNet18的甲骨文识别模型"""
    
    def __init__(self, num_classes=20):
        super().__init__()
        self.model = resnet18()
        num_features = self.model.fc.in_features
        self.model.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, num_classes)
        )
    
    def forward(self, x):
        return self.model(x)

# 全局变量
model = None
class_to_idx = {}
idx_to_class = {}
confidence_threshold = CONFIDENCE_THRESHOLD

def load_model():
    global model, class_to_idx, idx_to_class, confidence_threshold
    
    # 优先加载全类别模型，其次加载20类模型
    model_paths = [
        MODEL_DIR / "oracle_recognition_full.pth",
        MODEL_DIR / "oracle_recognition_quick.pth",
    ]
    
    for model_path in model_paths:
        if model_path.exists():
            try:
                checkpoint = torch.load(model_path, map_location=DEVICE)
                num_classes = len(checkpoint['class_to_idx'])
                
                class_to_idx = checkpoint.get('class_to_idx', {})
                idx_to_class = {v: k for k, v in class_to_idx.items()}
                confidence_threshold = checkpoint.get('confidence_threshold', CONFIDENCE_THRESHOLD)
                
                model = OracleResNet(num_classes=num_classes).to(DEVICE)
                model.load_state_dict(checkpoint['model_state_dict'])
                model.eval()
                
                print(f"模型加载成功: {model_path.name}")
                print(f"  类别数: {num_classes}")
                print(f"  验证准确率: {checkpoint.get('accuracy', 0):.4f}")
                print(f"  置信度阈值: {confidence_threshold}")
                return
            except Exception as e:
                print(f"加载 {model_path.name} 失败: {e}")
    
    print(f"模型文件不存在，使用模拟识别模式")
    # 使用默认字符表
    default_chars = ["日", "月", "山", "水", "火", "木", "人", "口", "土", "田",
                     "牛", "羊", "马", "犬", "豕", "鹿", "鸟", "鱼", "龟", "龙",
                     "王", "大", "小", "子", "女", "目", "耳", "手", "足", "止",
                     "卜", "贞", "雨", "风", "吉", "祸", "祭", "酒", "戈", "弓",
                     "矢", "车", "舟", "鼎", "酉", "甲", "乙", "丙", "丁", "戊",
                     "己", "庚", "辛", "壬", "癸", "子", "丑", "寅", "卯", "辰",
                     "巳", "午", "未", "申", "酉", "戌", "亥", "一", "二", "三"]
    for i, c in enumerate(default_chars):
        class_to_idx[c] = i
        idx_to_class[i] = c

@app.on_event("startup")
def startup_event():
    load_model()
    DATA_PATH.mkdir(exist_ok=True)


def infer_unknown_character(predicted_char, confidence, top_predictions, nearby_chars=None):
    """
    AI推断未知/污染/难以定义的字
    
    策略:
    1. 基础形近字分析
    2. 使用知识库深度揣摩（部首、语境、合文等）
    3. 区分污染字和难以定义字
    4. 给出大致意思范围
    """
    # 使用知识库进行深度分析
    ambiguous_result = analyze_ambiguous_character(
        predicted_char=predicted_char,
        confidence=confidence,
        top_predictions=[{"char": p["char"], "prob": p["prob"]} for p in top_predictions],
        nearby_chars=nearby_chars
    )
    
    # 转换为API返回格式
    inference = {
        "status": "ambiguous" if confidence >= 0.2 else "polluted",
        "top_prediction": predicted_char,
        "confidence": round(confidence * 100, 2),
        "is_polluted": confidence < 0.35,
        "is_ambiguous": confidence >= 0.2 and confidence < confidence_threshold,
        "possible_meanings": [],
        "rough_meaning": ambiguous_result["rough_meaning"],
        "explanation_text": generate_explanation(ambiguous_result),
        "detailed_analysis": ambiguous_result,
        "reasoning": ambiguous_result["reasoning"],
        "suggestions": ambiguous_result["suggestions"]
    }
    
    # 收集可能的含义
    possible = []
    
    # 形近字变体
    if ambiguous_result["similar_chars"]:
        possible.append(
            f"可能是「{'」「'.join(ambiguous_result['similar_chars'][:3])}」的异体、通假或变体字"
        )
    
    # 部首推断
    if ambiguous_result["radical_analysis"]:
        rad = ambiguous_result["radical_analysis"][0]
        possible.append(f"从字形看含「{rad['name']}」形，与「{rad['meaning']}」相关")
    
    # 语境推断
    if ambiguous_result["context_hints"]:
        ctx = ambiguous_result["context_hints"][0]
        possible.append(f"结合上下文，可能是「{ctx}」类卜辞用字")
    
    # 合文可能
    if ambiguous_result["hewen_possibility"]:
        hw = ambiguous_result["hewen_possibility"][0]
        possible.append(f"不排除合文可能：「{hw['name']}」→「{hw['meaning']}」")
    
    # 污染说明
    if confidence < 0.3:
        possible.append("图像存在较严重污染或残缺，以上分析仅供参考")
    elif confidence < 0.35:
        possible.append("字形有一定程度污损，建议结合更多样本比对")
    else:
        possible.append(f"最接近已知字「{predicted_char}」，但置信度较低")
    
    inference["possible_meanings"] = possible
    
    return inference


@app.post("/predict")
async def predict(file: UploadFile = File(...), context: Optional[str] = Form(None)):
    """
    甲骨文单字识别接口
    - 高置信度: 返回已知字
    - 低置信度: 标记为未知/难以定义 + AI深度揣摩
    
    参数:
    - file: 单字图片
    - context: 可选，上下文文字（前后相邻的已识别字，用于语境推断）
    """
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        input_tensor = transform(image).unsqueeze(0).to(DEVICE)
        
        # 解析上下文字符
        nearby_chars = list(context) if context else None
        
        if model is not None:
            with torch.no_grad():
                output = model(input_tensor)
                probabilities = torch.softmax(output, dim=1)
                
                # Top-5预测
                top5_prob, top5_idx = torch.topk(probabilities, min(5, len(idx_to_class)), dim=1)
                
                top_predictions = []
                for i in range(min(5, len(idx_to_class))):
                    char = idx_to_class.get(top5_idx[0][i].item(), "?")
                    prob = top5_prob[0][i].item()
                    top_predictions.append({
                        "char": char,
                        "prob": round(prob * 100, 2)
                    })
                
                predicted_idx = top5_idx[0][0].item()
                confidence = top5_prob[0][0].item()
                predicted_char = idx_to_class.get(predicted_idx, "未知")
                
                # 判断是否已知字
                if confidence >= confidence_threshold:
                    # 已知字
                    story = DEFAULT_STORIES.get(predicted_char, 
                                ORACLE_RADICALS.get(predicted_char, {}).get("meaning", "暂无字源故事"))
                    result = {
                        "success": True,
                        "character": predicted_char,
                        "confidence": round(confidence * 100, 2),
                        "story": story,
                        "is_unknown": False,
                        "is_ambiguous": False,
                        "is_polluted": False,
                        "all_predictions": top_predictions,
                        "inference": None
                    }
                else:
                    # 未知/污染/难以定义 -> AI深度揣摩
                    inference = infer_unknown_character(
                        predicted_char, confidence, top_predictions, nearby_chars
                    )
                    result = {
                        "success": True,
                        "character": f"[?{predicted_char}?]",
                        "display_character": predicted_char,
                        "confidence": round(confidence * 100, 2),
                        "is_unknown": True,
                        "is_ambiguous": inference["is_ambiguous"],
                        "is_polluted": inference["is_polluted"],
                        "all_predictions": top_predictions,
                        "inference": inference
                    }
        else:
            # 模拟模式
            # 随机选择置信度以演示不同情况
            confidence = np.random.uniform(0.15, 0.6)
            chars = list(idx_to_class.values()) if idx_to_class else ["日", "月", "山", "水", "火"]
            predicted_char = np.random.choice(chars)
            
            top_predictions = []
            selected = np.random.choice(chars, size=min(5, len(chars)), replace=False)
            total = 0
            for i, c in enumerate(selected):
                p = confidence if i == 0 else np.random.uniform(0.02, confidence * 0.8)
                total += p
                top_predictions.append({"char": c, "prob": round(p * 100, 2)})
            
            # 归一化
            if total > 0:
                for p in top_predictions:
                    p["prob"] = round(p["prob"] / total * 100, 2)
            top_predictions[0]["prob"] = round(confidence * 100, 2)
            
            if confidence >= confidence_threshold:
                story = DEFAULT_STORIES.get(predicted_char, "暂无字源故事")
                result = {
                    "success": True,
                    "character": predicted_char,
                    "confidence": round(confidence * 100, 2),
                    "story": story,
                    "is_unknown": False,
                    "is_ambiguous": False,
                    "is_polluted": False,
                    "all_predictions": top_predictions,
                    "inference": None
                }
            else:
                inference = infer_unknown_character(
                    predicted_char, confidence, top_predictions, nearby_chars
                )
                result = {
                    "success": True,
                    "character": f"[?{predicted_char}?]",
                    "display_character": predicted_char,
                    "confidence": round(confidence * 100, 2),
                    "is_unknown": True,
                    "is_ambiguous": inference["is_ambiguous"],
                    "is_polluted": inference["is_polluted"],
                    "all_predictions": top_predictions,
                    "inference": inference
                }
        
        return JSONResponse(content=result)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


@app.post("/predict_full")
async def predict_full(
    file: UploadFile = File(...),
    ordered_chars: Optional[str] = Form(None)
):
    """
    拓片全文识别接口（整图）
    
    参数:
    - file: 整张拓片图片
    - ordered_chars: 可选，用户已确认的按顺序排列的字符（用于上下文分析）
    
    返回:
    - 全文内容 + 逐字分析
    """
    # 注：完整的全文识别需要YOLOv8检测模型，这里返回接口定义和模拟结果
    # 实际使用时需要集成单字检测功能
    
    return JSONResponse(content={
        "success": True,
        "message": "全文识别接口（需要YOLOv8检测模型，当前为演示模式）",
        "note": "建议使用单字识别接口配合前端进行逐字识别，可利用context参数提供上下文",
        "tip": "上传拓片后，建议：1) 先分割单字 2) 逐字识别 3) 将已识别的相邻字传入context参数进行语境推断",
        "full_text_example": "癸卯卜，[?日?]贞：今日雨？",
        "characters_example": [
            {"char": "癸", "confidence": 92, "status": "known"},
            {"char": "卯", "confidence": 88, "status": "known"},
            {"char": "卜", "confidence": 95, "status": "known"},
            {"char": "[?鼎?]", "confidence": 42, "status": "ambiguous", 
             "inference": {"rough_meaning": "字形与「鼎」「贞」「贝」相近，结合语境属祭祀类卜辞..."}},
            {"char": "贞", "confidence": 85, "status": "known"},
            {"char": "今", "confidence": 78, "status": "known"},
            {"char": "日", "confidence": 91, "status": "known"},
            {"char": "雨", "confidence": 87, "status": "known"},
        ]
    })


@app.get("/knowledge")
async def get_knowledge():
    """获取甲骨文知识库摘要"""
    return JSONResponse(content={
        "success": True,
        "knowledge": {
            "total_radicals": len(ORACLE_RADICALS),
            "categories": list(set(r["category"] for r in ORACLE_RADICALS.values())),
            "context_types": list(DIVINATION_CONTEXTS.keys()),
            "sample_radicals": [
                {"char": k, "meaning": v["meaning"], "category": v["category"]}
                for k, v in list(ORACLE_RADICALS.items())[:30]
            ]
        }
    })


@app.get("/analyze_ambiguous_demo")
async def analyze_ambiguous_demo():
    """演示难以定义字符的揣摩分析"""
    # 模拟一个难以定义的字
    test_top_preds = [
        {"char": "日", "prob": 25.3},
        {"char": "口", "prob": 18.7},
        {"char": "曰", "prob": 12.1},
        {"char": "白", "prob": 8.5},
        {"char": "田", "prob": 6.2},
    ]
    
    result = analyze_ambiguous_character(
        predicted_char="日",
        confidence=0.25,
        top_predictions=test_top_preds,
        nearby_chars=["癸", "卯", "卜", "贞", "雨"]
    )
    
    return JSONResponse(content={
        "success": True,
        "demo_type": "难以定义字符揣摩演示",
        "scenario": "拓片天气卜辞中一个模糊不清的字",
        "analysis": result,
        "explanation": generate_explanation(result)
    })


@app.get("/classes")
async def get_classes():
    """获取所有支持的甲骨文字类别"""
    return JSONResponse(content={
        "success": True,
        "num_classes": len(idx_to_class),
        "classes": [
            {"char": v, "story": DEFAULT_STORIES.get(v, 
                ORACLE_RADICALS.get(v, {}).get("meaning", "暂无字源故事"))}
            for k, v in sorted(idx_to_class.items())
        ]
    })


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return JSONResponse(content={
        "status": "ok",
        "version": "3.0.0",
        "features": [
            "单字识别（ResNet）",
            "污染字检测",
            "难以定义字揣摩分析",
            "部首/形符分析",
            "形近字参考",
            "语境推断",
            "合文识别",
            "甲骨文知识库"
        ],
        "model_loaded": model is not None,
        "device": str(DEVICE),
        "num_classes": len(idx_to_class),
        "confidence_threshold": confidence_threshold
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
