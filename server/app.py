"""
甲骨文识别服务器 - Flask API
接收图片，返回识别结果
"""
import os
import json
import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from model import FastOracleCNN, load_model

app = Flask(__name__, static_folder='../frontend')
CORS(app)

# 配置
MODEL_PATH = '/root/oracle-model/model.pth'
DEVICE = torch.device('cpu')
IMG_SIZE = 64
TOP_K = 5

# 图像预处理
transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.Grayscale(num_output_channels=1),
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

# 全局模型变量
model = None
classes_map = {}

def load_model_file():
    global model, classes_map
    if os.path.exists(MODEL_PATH):
        try:
            model, classes_map = load_model(MODEL_PATH, DEVICE)
            print(f"Model loaded: {len(classes_map)} classes")
            return True
        except Exception as e:
            print(f"Failed to load model: {e}")
            return False
    else:
        print(f"Model file not found: {MODEL_PATH}")
        return False

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'oracle_scroll.html')

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'ok',
        'model_loaded': model is not None,
        'num_classes': len(classes_map),
        'device': str(DEVICE)
    })

@app.route('/api/recognize', methods=['POST'])
def recognize():
    if model is None:
        return jsonify({'success': False, 'error': 'Model not loaded'}), 503

    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image uploaded'}), 400

    try:
        file = request.files['image']
        img = Image.open(file.stream).convert('RGB')
        input_tensor = transform(img).unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            output = model(input_tensor)
            probs = F.softmax(output, dim=1)[0]
            top_probs, top_indices = probs.topk(TOP_K)

        results = []
        for i in range(TOP_K):
            idx = str(top_indices[i].item())
            confidence = top_probs[i].item()
            char_id = classes_map.get(idx, idx)
            results.append({
                'character': char_id,
                'confidence': round(confidence, 4),
                'class_index': int(idx)
            })

        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/classes')
def get_classes():
    return jsonify({'classes': classes_map, 'count': len(classes_map)})

if __name__ == '__main__':
    load_model_file()
    app.run(host='0.0.0.0', port=8080, debug=False)
