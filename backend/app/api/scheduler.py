from flask import Blueprint, jsonify, request
from app.services.automated_scheduler import get_scheduler, start_scheduler, stop_scheduler
from app.utils.middleware import rate_limit
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('scheduler', __name__)

@bp.route('/api/scheduler/status', methods=['GET'])
@rate_limit
def get_scheduler_status():
    """Get current scheduler status"""
    try:
        scheduler = get_scheduler()
        status = scheduler.get_status()
        
        return jsonify({
            'success': True,
            'data': status
        })
        
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/scheduler/start', methods=['POST'])
@rate_limit
def start_scheduler_endpoint():
    """Start the automated scheduler"""
    try:
        start_scheduler()
        
        return jsonify({
            'success': True,
            'message': 'Scheduler started successfully'
        })
        
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/scheduler/stop', methods=['POST'])
@rate_limit
def stop_scheduler_endpoint():
    """Stop the automated scheduler"""
    try:
        stop_scheduler()
        
        return jsonify({
            'success': True,
            'message': 'Scheduler stopped successfully'
        })
        
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/scheduler/override', methods=['POST'])
@rate_limit
def register_manual_override():
    """Register a manual override to prevent scheduler conflicts"""
    try:
        data = request.json
        if not data or 'device_type' not in data:
            return jsonify({
                'success': False,
                'error': 'device_type is required'
            }), 400
        
        device_type = data['device_type']
        if device_type not in ['pump', 'fan', 'cover']:
            return jsonify({
                'success': False,
                'error': 'Invalid device_type. Must be pump, fan, or cover'
            }), 400
        
        scheduler = get_scheduler()
        scheduler.register_manual_override(device_type)
        
        return jsonify({
            'success': True,
            'message': f'Manual override registered for {device_type}'
        })
        
    except Exception as e:
        logger.error(f"Error registering manual override: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/scheduler/reload', methods=['POST'])
@rate_limit
def reload_scheduler_configs():
    """Reload scheduler configurations and force immediate check"""
    try:
        scheduler = get_scheduler()
        scheduler.reload_configurations()
        
        return jsonify({
            'success': True,
            'message': 'Scheduler configurations reloaded successfully'
        })
        
    except Exception as e:
        logger.error(f"Error reloading scheduler configs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/scheduler/force-check', methods=['POST'])
@rate_limit
def force_schedule_check():
    """Force immediate schedule check"""
    try:
        scheduler = get_scheduler()
        scheduler.force_schedule_check()
        
        return jsonify({
            'success': True,
            'message': 'Schedule check executed successfully'
        })
        
    except Exception as e:
        logger.error(f"Error forcing schedule check: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
