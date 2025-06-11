from flask import Blueprint, jsonify, request
from app.services.notification_service import get_notification_service
from app.utils.middleware import rate_limit
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('notifications', __name__)

@bp.route('/api/notifications', methods=['GET'])
@rate_limit
def get_notifications():
    """Get all notifications or just unread ones"""
    try:
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        notification_service = get_notification_service()
        notifications = notification_service.get_notifications(unread_only=unread_only)
        
        return jsonify({
            'success': True,
            'data': notifications,
            'count': len(notifications)
        })
        
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/notifications/<notification_id>/read', methods=['POST'])
@rate_limit
def mark_notification_read(notification_id):
    """Mark a specific notification as read"""
    try:
        notification_service = get_notification_service()
        success = notification_service.mark_as_read(notification_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Notification marked as read'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Notification not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/notifications/read-all', methods=['POST'])
@rate_limit
def mark_all_notifications_read():
    """Mark all notifications as read"""
    try:
        notification_service = get_notification_service()
        count = notification_service.mark_all_as_read()
        
        return jsonify({
            'success': True,
            'message': f'{count} notifications marked as read'
        })
        
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/notifications/clear', methods=['DELETE'])
@rate_limit
def clear_notifications():
    """Clear all notifications"""
    try:
        notification_service = get_notification_service()
        count = notification_service.clear_notifications()
        
        return jsonify({
            'success': True,
            'message': f'{count} notifications cleared'
        })
        
    except Exception as e:
        logger.error(f"Error clearing notifications: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/notifications/test', methods=['POST'])
@rate_limit 
def add_test_notification():
    """Add a test notification (for development)"""
    try:
        data = request.get_json() or {}
        title = data.get('title', 'Test Notification')
        message = data.get('message', 'This is a test notification')
        
        notification_service = get_notification_service()
        from app.services.notification_service import NotificationType
        
        notification_id = notification_service.add_notification(
            NotificationType.INFO,
            title,
            message
        )
        
        return jsonify({
            'success': True,
            'notification_id': notification_id,
            'message': 'Test notification added'
        })
        
    except Exception as e:
        logger.error(f"Error adding test notification: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
