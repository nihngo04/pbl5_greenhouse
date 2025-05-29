import os
from flask import Blueprint, request, jsonify, send_file, abort
from datetime import datetime
from app.services.image_service import (
    save_image, get_images, get_image_path, delete_image,
    get_device_image_stats, get_storage_stats
)
from app.utils.middleware import rate_limit
from app.utils import ValidationError, StorageError
from app.services.cache_service import get_cache_stats, clear_cache

bp = Blueprint('images', __name__)

@bp.route('/api/images/upload', methods=['POST'])
@rate_limit
def upload_image():
    """API endpoint để nhận ảnh từ ESP32-CAM"""
    if 'image' not in request.files:
        raise ValidationError('No image file provided')
    
    image = request.files['image']
    device_id = request.form.get('device_id')
    
    if not device_id:
        raise ValidationError('Device ID is required')
    
    try:
        metadata = save_image(image, device_id)
        return jsonify({
            'success': True,
            'data': metadata.to_dict()
        })
    except (ValidationError, StorageError) as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to save image'
        }), 500

@bp.route('/api/images', methods=['GET'])
@rate_limit
def list_images():
    """API endpoint để lấy danh sách ảnh
    
    Query params:
        device_id: ID của thiết bị (optional)
        start_date: Ngày bắt đầu (YYYY-MM-DD)
        end_date: Ngày kết thúc (YYYY-MM-DD)
    """
    device_id = request.args.get('device_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Parse dates if provided
    start_dt = None
    end_dt = None
    try:
        if start_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        raise ValidationError('Invalid date format. Use YYYY-MM-DD')
    
    try:
        images = get_images(device_id, start_dt, end_dt)
        return jsonify({
            'success': True,
            'data': [img.to_dict() for img in images]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve images'
        }), 500

@bp.route('/api/images/<int:image_id>', methods=['GET'])
@rate_limit
def get_image(image_id):
    """API endpoint để lấy file ảnh"""
    try:
        image_path = get_image_path(image_id)
        if not image_path or not os.path.exists(image_path):
            abort(404)
        
        return send_file(image_path)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve image'
        }), 500

@bp.route('/api/images/<int:image_id>', methods=['DELETE'])
@rate_limit
def remove_image(image_id):
    """API endpoint để xóa ảnh"""
    try:
        if delete_image(image_id):
            return jsonify({
                'success': True,
                'message': 'Image deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Image not found'
            }), 404
    except StorageError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to delete image'
        }), 500

@bp.route('/api/images/stats/device/<device_id>', methods=['GET'])
@rate_limit
def device_stats(device_id):
    """API endpoint để lấy thống kê ảnh theo thiết bị"""
    try:
        stats = get_device_image_stats(device_id)
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/images/stats/storage', methods=['GET'])
@rate_limit
def storage_stats():
    """API endpoint để lấy thống kê lưu trữ"""
    try:
        stats = get_storage_stats()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/images/cache/stats', methods=['GET'])
@rate_limit
def cache_stats():
    """API endpoint để lấy thống kê cache"""
    try:
        stats = get_cache_stats()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/images/cache/clear', methods=['POST'])
@rate_limit
def clear_image_cache():
    """API endpoint để xóa cache"""
    try:
        clear_cache('images')  # Clear only image-related cache
        return jsonify({
            'success': True,
            'message': 'Cache cleared successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500