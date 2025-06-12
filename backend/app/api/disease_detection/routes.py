"""
Disease Detection API Routes
Integrated ESP32 Camera + AI Analysis
"""

from flask import Blueprint, request, jsonify, send_file, send_from_directory
from datetime import datetime
import os
import logging
from typing import Dict, Any

from app.services.camera_service import get_camera_service
from app.services.ai_service.handler import process_leaf_image
from app.services.image_service import save_image
from app.models.detection import DetectionResult, AIResult
from app.utils.middleware import rate_limit
from app import db

logger = logging.getLogger(__name__)

bp = Blueprint('disease_detection', __name__)

# Cấu hình đường dẫn
IMAGES_BASE_DIR = os.path.abspath("data/images")
DOWNLOAD_DIR = os.path.join(IMAGES_BASE_DIR, "download")
PREDICTED_DIR = os.path.join(IMAGES_BASE_DIR, "predicted")

# Tạo thư mục nếu chưa tồn tại
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(PREDICTED_DIR, exist_ok=True)

@bp.route('/api/disease-detection/camera-status', methods=['GET'])
@rate_limit
def check_camera_status():
    """Kiểm tra trạng thái ESP32-CAM"""
    try:
        camera_service = get_camera_service()
        status = camera_service.check_camera_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error checking camera status: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error checking camera: {str(e)}'
        }), 500

@bp.route('/api/disease-detection/capture-and-analyze', methods=['POST'])
@rate_limit
def capture_and_analyze():
    """Chụp ảnh từ ESP32-CAM và phân tích bằng AI"""
    try:
        # Lấy parameters từ request
        resolution = request.json.get('resolution', 'UXGA') if request.is_json else request.form.get('resolution', 'UXGA')
        quality = request.json.get('quality', 10) if request.is_json else int(request.form.get('quality', 10))
        
        # Khởi tạo camera service
        camera_service = get_camera_service()
        
        # Tạo filename và đường dẫn
        filename = camera_service.generate_filename()
        image_path = os.path.join(DOWNLOAD_DIR, filename)
        
        # Chụp ảnh từ ESP32-CAM
        capture_result = camera_service.capture_image(
            save_path=image_path,
            resolution=resolution,
            quality=quality
        )
        
        if capture_result['status'] != 'success':
            return jsonify(capture_result), 500
          # Phân tích ảnh bằng AI
        try:
            ai_results_raw = process_leaf_image(image_path)
            
            # Chuyển đổi kết quả AI thành format chuẩn
            ai_results = []
            for i, result in enumerate(ai_results_raw):
                ai_result = AIResult(
                    leaf_index=i + 1,                    predicted_class=result.get('predicted_class', 'Unknown'),
                    confidence=result.get('confidence', 0.0),
                    type='disease' if 'bệnh' in result.get('predicted_class', '').lower() else 'pest',
                    severity=_determine_severity(result.get('confidence', 0.0))
                )
                ai_results.append(ai_result)
            
            # Tạo ảnh predicted với annotations
            try:
                logger.info(f"Attempting to create predicted image for: {image_path}")
                from app.services.image_processing import create_predicted_image
                predicted_path = create_predicted_image(
                    image_path, 
                    [result.dict() for result in ai_results], 
                    PREDICTED_DIR
                )
                predicted_filename = os.path.basename(predicted_path) if predicted_path else None
                logger.info(f"Predicted image created: {predicted_path}")
            except Exception as e:
                logger.error(f"Could not create predicted image: {str(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                predicted_filename = None
            
            # Lưu metadata vào database
            try:
                from app.models.detection_history import DetectionHistory
                  # Tạo detection history record
                detection_history = DetectionHistory(
                    original_image_path=image_path,
                    predicted_image_path=predicted_path if predicted_path else None,
                    detection_method='automatic',
                    camera_status=capture_result.get('camera_status', 'online'),
                    ai_results=[result.dict() for result in ai_results]
                )
                
                db.session.add(detection_history)
                db.session.commit()
                
                logger.info(f"Saved detection history with ID: {detection_history.id}")
                
            except Exception as e:
                logger.warning(f"Could not save detection history: {str(e)}")
                # Continue without failing the request
            
            # Lưu image metadata
            try:
                # Copy image to proper location and save metadata
                import shutil
                from werkzeug.datastructures import FileStorage
                
                # Create proper file structure for image service
                target_filename = f"disease_detection_{filename}"
                
                # Create a FileStorage-like object
                with open(image_path, 'rb') as f:
                    file_storage = FileStorage(
                        stream=f,
                        filename=target_filename,
                        content_type='image/jpeg'
                    )
                    
                    metadata = save_image(file_storage, 'esp32cam_disease_detection')
                
            except Exception as e:
                logger.warning(f"Could not save image metadata: {str(e)}")
                metadata = None
              # Tạo response
            detection_result = DetectionResult(
                status="success",
                message="Image captured and analyzed successfully",
                detection_id=int(datetime.now().timestamp()),
                download_url=f"/api/images/download/{filename}",
                predicted_url=f"/api/images/predicted/{predicted_filename}" if predicted_filename else None,
                ai_results=ai_results
            )
            
            logger.info(f"Disease detection completed for {filename}")
            return jsonify(detection_result.dict())
            
        except Exception as ai_error:
            logger.error(f"AI analysis failed: {str(ai_error)}")
            return jsonify({
                'status': 'success',
                'message': 'Image captured but AI analysis failed',
                'detection_id': int(datetime.now().timestamp()),
                'download_url': f"/api/images/download/{filename}",
                'ai_results': [],
                'ai_error': str(ai_error)
            })
        
    except Exception as e:
        logger.error(f"Error in capture-and-analyze: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }), 500

@bp.route('/api/disease-detection/analyze', methods=['POST'])
@rate_limit
def analyze_uploaded_image():
    """Phân tích ảnh đã upload"""
    try:
        if 'image' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No image file provided'
            }), 400
            
        file = request.files['image']
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No image file selected'
            }), 400
        
        # Lưu file tạm thời
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"upload_{timestamp}_{file.filename}"
        image_path = os.path.join(DOWNLOAD_DIR, filename)
        file.save(image_path)
          # Phân tích bằng AI
        try:
            ai_results_raw = process_leaf_image(image_path)
            
            # Chuyển đổi kết quả
            ai_results = []
            for i, result in enumerate(ai_results_raw):
                ai_result = AIResult(
                    leaf_index=i + 1,
                    predicted_class=result.get('predicted_class', 'Unknown'),
                    confidence=result.get('confidence', 0.0),
                    type='disease' if 'bệnh' in result.get('predicted_class', '').lower() else 'pest',
                    severity=_determine_severity(result.get('confidence', 0.0))
                )
                ai_results.append(ai_result)
              # Tạo ảnh predicted với annotations
            try:
                logger.info(f"Attempting to create predicted image for upload: {image_path}")
                from app.services.image_processing import create_predicted_image
                predicted_path = create_predicted_image(
                    image_path, 
                    [result.dict() for result in ai_results], 
                    PREDICTED_DIR
                )
                predicted_filename = os.path.basename(predicted_path) if predicted_path else None
                logger.info(f"Predicted image created for upload: {predicted_path}")
            except Exception as e:
                logger.error(f"Could not create predicted image for upload: {str(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                predicted_filename = None
              # Lưu metadata
            try:
                from app.models.detection_history import DetectionHistory
                  # Tạo detection history record cho manual upload
                detection_history = DetectionHistory(
                    original_image_path=image_path,
                    predicted_image_path=predicted_path if predicted_path else None,
                    detection_method='manual',
                    camera_status='offline',  # Manual upload không dùng camera
                    ai_results=[result.dict() for result in ai_results]
                )
                
                db.session.add(detection_history)
                db.session.commit()
                
                logger.info(f"Saved manual detection history with ID: {detection_history.id}")
                
            except Exception as e:
                logger.warning(f"Could not save detection history: {str(e)}")            # Lưu image metadata
            try:
                metadata = save_image(file, 'manual_upload')
            except Exception as e:
                logger.warning(f"Could not save image metadata: {str(e)}")
                metadata = None
            
            detection_result = DetectionResult(
                status="success",
                message="Image analyzed successfully",
                detection_id=int(datetime.now().timestamp()),
                download_url=f"/api/images/download/{filename}",
                predicted_url=f"/api/images/predicted/{predicted_filename}" if predicted_filename else None,
                ai_results=ai_results
            )
            
            return jsonify(detection_result.dict())
            
        except Exception as ai_error:
            logger.error(f"AI analysis failed: {str(ai_error)}")
            return jsonify({
                'status': 'error',
                'message': f'AI analysis failed: {str(ai_error)}'
            }), 500
        
    except Exception as e:
        logger.error(f"Error in analyze_uploaded_image: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }), 500

@bp.route('/api/disease-detection/history', methods=['GET'])
@rate_limit
def get_detection_history():
    """Lấy lịch sử phát hiện bệnh"""
    try:
        from app.models.detection_history import DetectionHistory
        
        # Lấy parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        method = request.args.get('method')  # 'automatic' hoặc 'manual'
        disease_only = request.args.get('disease_only', 'false').lower() == 'true'
        
        # Tạo query
        query = DetectionHistory.query
        
        # Filter theo method
        if method:
            query = query.filter(DetectionHistory.detection_method == method)
        
        # Filter chỉ hiển thị những detection có bệnh
        if disease_only:
            query = query.filter(DetectionHistory.disease_detected == True)
        
        # Sắp xếp theo thời gian mới nhất
        query = query.order_by(DetectionHistory.timestamp.desc())
        
        # Phân trang
        paginated = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Chuyển đổi thành dictionary
        history_items = [item.to_dict() for item in paginated.items]
        
        return jsonify({
            'status': 'success',
            'history': history_items,
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev
        })
        
    except Exception as e:
        logger.error(f"Error getting detection history: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }), 500

@bp.route('/api/images/download/<filename>', methods=['GET'])
def serve_download_image(filename):
    """Serve images from download directory"""
    try:
        file_path = os.path.join(DOWNLOAD_DIR, filename)
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return jsonify({'error': 'Image not found'}), 404
    except Exception as e:
        logger.error(f"Error serving image {filename}: {str(e)}")
        return jsonify({'error': 'Error serving image'}), 500

@bp.route('/api/images/predicted/<filename>', methods=['GET'])
def serve_predicted_image(filename):
    """Serve images from predicted directory"""
    try:
        file_path = os.path.join(PREDICTED_DIR, filename)
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return jsonify({'error': 'Predicted image not found'}), 404
    except Exception as e:
        logger.error(f"Error serving predicted image {filename}: {str(e)}")
        return jsonify({'error': 'Error serving predicted image'}), 500

@bp.route('/api/disease-detection/statistics', methods=['GET'])
@rate_limit
def get_detection_statistics():
    """Lấy thống kê phát hiện bệnh"""
    try:
        from app.models.detection_history import DetectionStatistics, DetectionHistory
        from datetime import date, timedelta
        from sqlalchemy import func
        
        # Lấy parameters
        days = request.args.get('days', 7, type=int)  # Default 7 ngày
        
        # Tính toán ngày bắt đầu
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        # Lấy thống kê từ bảng DetectionStatistics
        statistics = DetectionStatistics.query.filter(
            DetectionStatistics.date >= start_date,
            DetectionStatistics.date <= end_date
        ).order_by(DetectionStatistics.date.desc()).all()
        
        # Nếu không có dữ liệu trong DetectionStatistics, tạo từ DetectionHistory
        if not statistics:
            # Tạo thống kê từ DetectionHistory
            daily_stats = db.session.query(
                func.date(DetectionHistory.timestamp).label('date'),
                func.count(DetectionHistory.id).label('total_detections'),
                func.sum(func.case([(DetectionHistory.detection_method == 'automatic', 1)], else_=0)).label('automatic'),
                func.sum(func.case([(DetectionHistory.detection_method == 'manual', 1)], else_=0)).label('manual'),
                func.sum(func.case([(DetectionHistory.disease_detected == True, 1)], else_=0)).label('diseases'),
                func.sum(func.case([(DetectionHistory.disease_detected == False, 1)], else_=0)).label('healthy')
            ).filter(
                func.date(DetectionHistory.timestamp) >= start_date,
                func.date(DetectionHistory.timestamp) <= end_date
            ).group_by(func.date(DetectionHistory.timestamp)).all()
            
            # Chuyển đổi thành format response
            stats_data = []
            for stat in daily_stats:
                stats_data.append({
                    'date': stat.date.isoformat(),
                    'total_detections': stat.total_detections or 0,
                    'automatic_detections': stat.automatic or 0,
                    'manual_detections': stat.manual or 0,
                    'diseases_detected': stat.diseases or 0,
                    'healthy_detections': stat.healthy or 0
                })
        else:
            stats_data = [stat.to_dict() for stat in statistics]
        
        # Tính tổng kết
        total_stats = {
            'total_detections': sum(s.get('total_detections', 0) for s in stats_data),
            'total_diseases': sum(s.get('diseases_detected', 0) for s in stats_data),
            'total_healthy': sum(s.get('healthy_detections', 0) for s in stats_data),
            'total_automatic': sum(s.get('automatic_detections', 0) for s in stats_data),
            'total_manual': sum(s.get('manual_detections', 0) for s in stats_data)
        }
        
        return jsonify({
            'status': 'success',
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'daily_statistics': stats_data,
            'summary': total_stats
        })
        
    except Exception as e:
        logger.error(f"Error getting detection statistics: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }), 500

@bp.route('/api/disease-detection/recent-activity', methods=['GET'])
@rate_limit
def get_recent_activity():
    """Lấy hoạt động gần đây"""
    try:
        from app.models.detection_history import DetectionHistory
        
        # Lấy parameters
        limit = request.args.get('limit', 10, type=int)
        
        # Lấy các detection gần đây
        recent_detections = DetectionHistory.query.order_by(
            DetectionHistory.timestamp.desc()
        ).limit(limit).all()
        
        # Chuyển đổi thành format hoạt động
        activities = []
        for detection in recent_detections:
            activity_type = "warning" if detection.disease_detected else "success"
            action = f"Phát hiện {detection.predicted_class}" if detection.predicted_class else "Quét hoàn thành"
            
            activities.append({
                'time': detection.timestamp.strftime("%H:%M"),
                'action': action,
                'type': activity_type,
                'method': detection.detection_method,
                'confidence': detection.confidence_score,
                'severity': detection.severity
            })
        
        return jsonify({
            'status': 'success',
            'activities': activities,
            'count': len(activities)
        })
        
    except Exception as e:
        logger.error(f"Error getting recent activity: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }), 500

@bp.route('/test-upload', methods=['GET'])
def serve_test_page():
    """Serve test upload page"""
    try:
        test_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '..', 'test_upload.html')
        return send_file(test_file)
    except Exception as e:
        return f"Error loading test page: {str(e)}", 500

def _determine_severity(confidence: float) -> str:
    """Xác định mức độ nghiêm trọng dựa trên confidence score"""
    if confidence > 0.8:
        return "high"
    elif confidence > 0.5:
        return "medium"
    return "low"
