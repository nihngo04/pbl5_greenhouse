"""
Image processing utilities for disease detection
"""
import cv2
import os
import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple

def create_predicted_image(original_image_path: str, ai_results: List[Dict], save_dir: str) -> str:
    """
    Tạo ảnh predicted với annotations từ kết quả AI
    
    Args:
        original_image_path: Đường dẫn ảnh gốc
        ai_results: Kết quả từ AI service
        save_dir: Thư mục lưu ảnh predicted
        
    Returns:
        Đường dẫn ảnh predicted đã tạo
    """
    try:
        # Đọc ảnh gốc
        image = cv2.imread(original_image_path)
        if image is None:
            raise Exception(f"Cannot read image: {original_image_path}")
        
        # Tạo tên file predicted
        original_filename = os.path.basename(original_image_path)
        name_without_ext = os.path.splitext(original_filename)[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        predicted_filename = f"{name_without_ext}_predicted_{timestamp}.jpg"
        predicted_path = os.path.join(save_dir, predicted_filename)
        
        # Vẽ annotations lên ảnh
        annotated_image = draw_annotations(image, ai_results)
        
        # Lưu ảnh predicted
        os.makedirs(save_dir, exist_ok=True)
        cv2.imwrite(predicted_path, annotated_image)
        
        return predicted_path
        
    except Exception as e:
        print(f"Error creating predicted image: {e}")
        return None

def draw_annotations(image: np.ndarray, ai_results: List[Dict]) -> np.ndarray:
    """
    Vẽ annotations lên ảnh dựa trên kết quả AI
    
    Args:
        image: Ảnh gốc (numpy array)
        ai_results: Kết quả AI với thông tin detection
        
    Returns:
        Ảnh đã được annotated
    """
    annotated = image.copy()
    height, width = annotated.shape[:2]
    
    # Colors cho các loại detection
    colors = {
        'disease': (0, 0, 255),    # Đỏ cho bệnh
        'pest': (0, 165, 255),     # Cam cho sâu bệnh  
        'healthy': (0, 255, 0),    # Xanh cho khỏe mạnh
        'unknown': (128, 128, 128) # Xám cho không xác định
    }
    
    # Font settings
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    thickness = 2
    
    for i, result in enumerate(ai_results):
        # Lấy thông tin từ kết quả
        predicted_class = result.get('predicted_class', 'Unknown')
        confidence = result.get('confidence', 0.0)
        detection_type = result.get('type', 'unknown')
        
        # Chọn màu theo loại detection
        color = colors.get(detection_type, colors['unknown'])
        
        # Tạo label text
        label = f"{predicted_class} ({confidence:.1%})"
        
        # Tính vị trí để vẽ (chia ảnh thành grid để hiển thị multiple detections)
        rows = int(np.ceil(np.sqrt(len(ai_results))))
        cols = int(np.ceil(len(ai_results) / rows))
        
        row = i // cols
        col = i % cols
        
        # Vị trí bounding box cho từng detection
        box_width = width // cols
        box_height = height // rows
        
        x1 = col * box_width + 10
        y1 = row * box_height + 30
        x2 = (col + 1) * box_width - 10
        y2 = (row + 1) * box_height - 10
        
        # Vẽ bounding box
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        
        # Vẽ label background
        label_size = cv2.getTextSize(label, font, font_scale, thickness)[0]
        cv2.rectangle(annotated, 
                     (x1, y1 - label_size[1] - 10), 
                     (x1 + label_size[0], y1), 
                     color, -1)
        
        # Vẽ label text
        cv2.putText(annotated, label, (x1, y1 - 5), 
                   font, font_scale, (255, 255, 255), thickness)
        
        # Thêm số thứ tự
        cv2.putText(annotated, f"#{i+1}", (x1 + 5, y1 + 25), 
                   font, font_scale, color, thickness)
    
    # Thêm summary text ở góc trên
    summary_text = f"Detected {len(ai_results)} item(s)"
    cv2.putText(annotated, summary_text, (10, 25), 
               font, 0.7, (255, 255, 255), 2)
    cv2.putText(annotated, summary_text, (10, 25), 
               font, 0.7, (0, 0, 0), 1)
    
    # Thêm timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(annotated, timestamp, (10, height - 10), 
               font, 0.5, (255, 255, 255), 2)
    cv2.putText(annotated, timestamp, (10, height - 10), 
               font, 0.5, (0, 0, 0), 1)
    
    return annotated

def draw_leaf_detections(image: np.ndarray, detections: List[Dict]) -> np.ndarray:
    """
    Vẽ detection boxes cho từng lá được phát hiện
    
    Args:
        image: Ảnh gốc
        detections: List các detection với bounding boxes
        
    Returns:
        Ảnh với leaf detection boxes
    """
    annotated = image.copy()
    
    for i, detection in enumerate(detections):
        # Giả sử detection có format {'box': [x1, y1, x2, y2], 'class': ..., 'confidence': ...}
        if 'box' in detection:
            x1, y1, x2, y2 = detection['box']
            confidence = detection.get('confidence', 0.0)
            class_name = detection.get('class', 'Leaf')
            
            # Vẽ bounding box
            cv2.rectangle(annotated, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            
            # Vẽ label
            label = f"Leaf {i+1}: {class_name} ({confidence:.2f})"
            cv2.putText(annotated, label, (int(x1), int(y1) - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    return annotated
