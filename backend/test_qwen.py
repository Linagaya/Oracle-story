"""
测试Qwen2.5-VL-7B是否能在本地8GB显存上运行
使用4-bit量化降低显存占用到约6GB
"""

import torch
from pathlib import Path

print("=" * 60)
print("检查本地运行Qwen2.5-VL-7B的可行性")
print("=" * 60)

# 检查GPU
if torch.cuda.is_available():
    gpu_name = torch.cuda.get_device_name(0)
    vram_gb = round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 1)
    print(f"\nGPU: {gpu_name}")
    print(f"显存: {vram_gb}GB")
    
    if vram_gb >= 6:
        print("\n[结论] 8GB显存可以用4-bit量化运行Qwen2.5-VL-7B")
        print("\n运行命令:")
        print("  pip install transformers accelerate bitsandbytes")
        print("  python test_qwen.py")
    else:
        print(f"\n[警告] {vram_gb}GB显存不足，至少需要6GB（4-bit量化）")
else:
    print("\n[警告] 未检测到CUDA，无法运行大模型")

print("\n" + "-" * 60)
print("显存占用估算:")
print("  FP16精度:  ~14GB (需要RTX 3090)")
print("  8-bit量化: ~10GB (需要RTX 3080)")  
print("  4-bit量化: ~6GB  (你的RTX 4060 8GB可以)")
print("\n替代方案:")
print("  - 使用Qwen2.5-VL-3B (约4GB显存)")
print("  - 使用云端API (阿里云百炼)")
print("  - 使用Ollama本地部署 (自动量化)")
