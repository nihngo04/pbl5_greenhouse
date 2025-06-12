"""
AI Handler for Disease Detection
Integrated into Greenhouse Backend
"""

import os
import cv2
import numpy as np
import torch
import torch.nn as nn
from torchvision import models, transforms
from ultralytics import YOLO
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Model paths
MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
MODEL_YOLO_PATH = os.path.join(MODELS_DIR, 'best.pt')
MODEL_RESNET_PATH = os.path.join(MODELS_DIR, 'pbl5_ver4.pth')

# Initialize models
yolo_model = None
resnet_model = None

def initialize_models():
    """Initialize AI models"""
    global yolo_model, resnet_model
    
    try:
        # Load YOLO model
        if os.path.exists(MODEL_YOLO_PATH):
            yolo_model = YOLO(MODEL_YOLO_PATH)
            logger.info("YOLO model loaded successfully")
        else:
            logger.error(f"YOLO model not found at: {MODEL_YOLO_PATH}")
            return False

        # Load ResNet18 model
        num_classes = 5
        resnet_model = models.resnet18(weights=None)
        
        # Freeze early layers
        for param in resnet_model.parameters():
            param.requires_grad = False
        for param in resnet_model.layer2.parameters():
            param.requires_grad = True
        for param in resnet_model.layer3.parameters():
            param.requires_grad = True
        for param in resnet_model.layer4.parameters():
            param.requires_grad = True

        # Custom classifier
        num_ftrs = resnet_model.fc.in_features
        resnet_model.fc = nn.Sequential(
            nn.BatchNorm1d(num_ftrs),
            nn.Dropout(0.5),
            nn.Linear(num_ftrs, 512),
            nn.ReLU(),
            nn.BatchNorm1d(512),
            nn.Dropout(0.4),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(0.4),
            nn.Linear(256, num_classes)
        )

        if os.path.exists(MODEL_RESNET_PATH):
            resnet_model.load_state_dict(torch.load(MODEL_RESNET_PATH, map_location=device))
            resnet_model.eval()
            resnet_model = resnet_model.to(device)
            logger.info("ResNet model loaded successfully")
        else:
            logger.error(f"ResNet model not found at: {MODEL_RESNET_PATH}")
            return False

        return True

    except Exception as e:
        logger.error(f"Error initializing models: {str(e)}")
        return False

# Image preprocessing
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((448, 448)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Class names and priority
class_names = ['Anthracnose', 'Bacterial-Spot', 'Downy-Mildew', 'Healthy-Leaf', 'Pest-Damage']
priority = {
    'Anthracnose': 1,
    'Downy-Mildew': 2,
    'Bacterial-Spot': 3,
    'Pest-Damage': 4,
    'Healthy-Leaf': 5
}

def process_leaf_image(image_path: str) -> List[Dict]:
    """Process image and predict leaf diseases"""
    global yolo_model, resnet_model
    
    # Initialize models if not already loaded
    if yolo_model is None or resnet_model is None:
        if not initialize_models():
            return [{"predicted_class": "Error: Cannot initialize AI models", "confidence": 0.0}]
    
    try:
        # Read and convert image
        img = cv2.imread(image_path)
        if img is None:
            raise Exception(f"Cannot read image at: {image_path}")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w = img.shape[:2]
    except Exception as e:
        logger.error(f"Error reading image: {e}")
        return [{"predicted_class": "Error: Cannot read image", "confidence": 0.0}]

    try:
        # Detect leaves using YOLO
        results = yolo_model.predict(source=img, imgsz=640, conf=0.5)
        boxes = results[0].boxes.xyxy.cpu().numpy()
        confidences = results[0].boxes.conf.cpu().numpy()

        if len(boxes) == 0:
            return [{"predicted_class": "Plant status: No leaves detected", "confidence": 0.0}]

        # Dictionary to count frequency and total confidence for each disease
        disease_scores = {name: {"count": 0, "total_confidence": 0.0, "avg_confidence": 0.0} for name in class_names}
        total_leaves = 0

        # Process each detected leaf
        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = map(int, box)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            
            leaf = img[y1:y2, x1:x2]
            
            # Preprocess and predict
            input_tensor = transform(leaf).unsqueeze(0).to(device)
            with torch.no_grad():
                output = resnet_model(input_tensor)
                probabilities = torch.softmax(output, dim=1)
                pred_class = torch.argmax(output, dim=1).item()
                confidence = float(probabilities[0][pred_class])
            
            disease_name = class_names[pred_class]
            disease_scores[disease_name]["count"] += 1
            disease_scores[disease_name]["total_confidence"] += confidence
            total_leaves += 1

        # Calculate average confidence for each disease
        for disease in disease_scores:
            if disease_scores[disease]["count"] > 0:
                disease_scores[disease]["avg_confidence"] = (
                    disease_scores[disease]["total_confidence"] / disease_scores[disease]["count"]
                )

        # Find the highest priority disease among detected diseases
        detected_diseases = [disease for disease in disease_scores if disease_scores[disease]["count"] > 0]
        if not detected_diseases:
            return [{"predicted_class": "Plant status: No diseases detected", "confidence": 0.0}]

        # Sort by priority and get the highest priority disease
        highest_priority_disease = min(detected_diseases, key=lambda x: priority[x])
        
        # Create detailed result
        result = {
            "predicted_class": f"Plant status: {highest_priority_disease}",
            "confidence": float(disease_scores[highest_priority_disease]["avg_confidence"]),
            "details": f"Detected {disease_scores[highest_priority_disease]['count']} out of {total_leaves} leaves"
        }

        logger.info(f"AI analysis completed: {result['predicted_class']} with confidence {result['confidence']:.2f}")
        return [result]

    except Exception as e:
        logger.error(f"Error in AI processing: {str(e)}")
        return [{"predicted_class": f"AI processing error: {str(e)}", "confidence": 0.0}]
