import os
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
from app.config import Config
from app.models.image import ImageMetadata
from app.utils import StorageError, ensure_directory_exists
from app.services.cache_service import cache
from app import db

logger = logging.getLogger(__name__)

def allowed_file(filename):
    """Kiểm tra xem file có đúng định dạng cho phép không"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_image(file, device_id):
    """Lưu file ảnh và tạo metadata
    
    Args:
        file: FileStorage object từ request
        device_id: ID của thiết bị ESP32-CAM
    
    Returns:
        ImageMetadata object nếu thành công
        
    Raises:
        StorageError: Nếu có lỗi khi lưu file hoặc metadata
    """
    try:
        if not file or not allowed_file(file.filename):
            raise ValueError("Invalid file type")
        
        # Tạo tên file an toàn với timestamp
        timestamp = datetime.utcnow()
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        
        # Tạo đường dẫn theo cấu trúc: device_id/YYYY-MM-DD/HHMMSS.ext
        date_folder = timestamp.strftime('%Y-%m-%d')
        time_str = timestamp.strftime('%H%M%S')
        rel_path = os.path.join(device_id, date_folder, f"{time_str}.{file_ext}")
        abs_path = os.path.join(Config.UPLOAD_FOLDER, rel_path)
        
        # Tạo thư mục nếu chưa tồn tại
        try:
            ensure_directory_exists(os.path.dirname(abs_path))
        except Exception as e:
            logger.error(f"Failed to create directory for image: {e}")
            raise StorageError(f"Failed to create directory: {e}")
        
        # Lưu file
        try:
            file.save(abs_path)
        except Exception as e:
            logger.error(f"Failed to save image file: {e}")
            raise StorageError(f"Failed to save image: {e}")
        
        # Tạo và lưu metadata
        try:
            metadata = ImageMetadata(
                device_id=device_id,
                timestamp=timestamp,
                image_path=rel_path,
                file_type=file_ext
            )
            db.session.add(metadata)
            db.session.commit()
            
            logger.info(f"Successfully saved image: {rel_path}")
            return metadata
            
        except Exception as e:
            # Xóa file nếu lưu metadata thất bại
            if os.path.exists(abs_path):
                os.remove(abs_path)
            logger.error(f"Failed to save image metadata: {e}")
            raise StorageError(f"Failed to save image metadata: {e}")
            
    except ValueError as e:
        raise StorageError(str(e))
    except Exception as e:
        logger.error(f"Unexpected error saving image: {e}")
        raise StorageError(f"Unexpected error: {e}")

@cache(ttl=300, key_prefix='images')  # Cache for 5 minutes
def get_images(device_id=None, start_date=None, end_date=None):
    """Lấy danh sách metadata của ảnh theo điều kiện lọc"""
    try:
        query = ImageMetadata.query
        
        if device_id:
            query = query.filter(ImageMetadata.device_id == device_id)
        if start_date:
            query = query.filter(ImageMetadata.timestamp >= start_date)
        if end_date:
            query = query.filter(ImageMetadata.timestamp <= end_date)
        
        return query.order_by(ImageMetadata.timestamp.desc()).all()
        
    except Exception as e:
        logger.error(f"Failed to query images: {e}")
        raise StorageError(f"Failed to query images: {e}")

@cache(ttl=300, key_prefix='image_path')  # Cache for 5 minutes
def get_image_path(image_id):
    """Lấy đường dẫn tuyệt đối đến file ảnh từ ID"""
    try:
        metadata = ImageMetadata.query.get(image_id)
        if metadata:
            abs_path = os.path.join(Config.UPLOAD_FOLDER, metadata.image_path)
            if os.path.exists(abs_path):
                return abs_path
            else:
                logger.warning(f"Image file not found: {abs_path}")
                return None
        return None
        
    except Exception as e:
        logger.error(f"Failed to get image path: {e}")
        raise StorageError(f"Failed to get image path: {e}")

def delete_image(image_id):
    """Xóa ảnh và metadata"""
    try:
        metadata = ImageMetadata.query.get(image_id)
        if metadata:
            # Xóa file
            file_path = os.path.join(Config.UPLOAD_FOLDER, metadata.image_path)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.error(f"Failed to delete image file: {e}")
                    raise StorageError(f"Failed to delete image file: {e}")
            
            # Xóa metadata
            try:
                db.session.delete(metadata)
                db.session.commit()
                logger.info(f"Successfully deleted image: {metadata.image_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete image metadata: {e}")
                raise StorageError(f"Failed to delete image metadata: {e}")
        return False
        
    except Exception as e:
        logger.error(f"Unexpected error deleting image: {e}")
        raise StorageError(f"Unexpected error: {e}")

@cache(ttl=300, key_prefix='device_stats')  # Cache for 5 minutes
def get_device_image_stats(device_id):
    """Get statistics about images for a specific device"""
    try:
        stats = db.session.query(
            db.func.count(ImageMetadata.id).label('total_images'),
            db.func.min(ImageMetadata.timestamp).label('first_image'),
            db.func.max(ImageMetadata.timestamp).label('last_image')
        ).filter(ImageMetadata.device_id == device_id).first()
        
        return {
            'device_id': device_id,
            'total_images': stats.total_images if stats else 0,
            'first_image': stats.first_image.isoformat() if stats and stats.first_image else None,
            'last_image': stats.last_image.isoformat() if stats and stats.last_image else None
        }
    except Exception as e:
        logger.error(f"Failed to get device image stats: {e}")
        raise StorageError(f"Failed to get device image stats: {e}")

@cache(ttl=300, key_prefix='storage_stats')  # Cache for 5 minutes
def get_storage_stats():
    """Get storage statistics for images"""
    try:
        total_size = 0
        for root, dirs, files in os.walk(Config.UPLOAD_FOLDER):
            total_size += sum(os.path.getsize(os.path.join(root, name)) 
                            for name in files)
        
        total_images = ImageMetadata.query.count()
        
        return {
            'total_images': total_images,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }
    except Exception as e:
        logger.error(f"Failed to get storage stats: {e}")
        raise StorageError(f"Failed to get storage stats: {e}")