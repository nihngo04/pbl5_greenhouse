import torch
from PIL import Image
import numpy as np
from typing import List
from app.models.detection import AIResult
import os

# Đường dẫn đến model (sẽ được cập nhật sau)
MODEL_PATH = os.getenv("AI_MODEL_PATH", "path/to/your/model.pt")

def analyze_image(image_path: str) -> List[AIResult]:
    """
    Analyze image using AI model
    Returns list of detected issues (diseases/pests)
    """
    try:
        # TODO: Implement actual AI model integration
        # This is a mock implementation
        return [
            AIResult(
                leaf_index=1,
                predicted_class="Leaf Blight",
                confidence=0.92,
                type="disease",
                severity="high"
            ),
            AIResult(
                leaf_index=2,
                predicted_class="Aphids",
                confidence=0.85,
                type="pest",
                severity="medium"
            )
        ]
    except Exception as e:
        print(f"Error analyzing image: {str(e)}")
        return []

def determine_severity(confidence: float) -> str:
    """Determine severity based on confidence score"""
    if confidence > 0.8:
        return "high"
    elif confidence > 0.5:
        return "medium"
    return "low"
