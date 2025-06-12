import torch
from PIL import Image
import numpy as np
from typing import List
import os
from ..models.detection import AIResult

# Load model AI (sẽ được cập nhật với model thực tế sau)
MODEL_PATH = os.getenv("AI_MODEL_PATH", "path/to/your/model.pt")

async def analyze_image(image_path: str) -> List[AIResult]:
    """
    Phân tích ảnh sử dụng AI model
    Returns danh sách các vấn đề phát hiện được (bệnh/sâu)
    """
    try:
        # TODO: Implement actual AI model integration
        # Đây là implementation tạm thời
        return [
            AIResult(
                leaf_index=1,
                predicted_class="Bệnh đốm lá",
                confidence=0.92,
                type="disease",
                severity="high"
            ),
            AIResult(
                leaf_index=2,
                predicted_class="Rệp xanh",
                confidence=0.85,
                type="pest",
                severity="medium"
            )
        ]
    except Exception as e:
        print(f"Error analyzing image: {str(e)}")
        return []

def determine_severity(confidence: float) -> str:
    """Xác định mức độ nghiêm trọng dựa trên độ tin cậy"""
    if confidence > 0.8:
        return "high"
    elif confidence > 0.5:
        return "medium"
    return "low"
