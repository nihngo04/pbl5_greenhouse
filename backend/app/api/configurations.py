from flask import Blueprint, jsonify, request
from app.utils.middleware import rate_limit
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

bp = Blueprint('configurations', __name__)

@bp.route('/api/devices/apply-config', methods=['POST'])
@rate_limit
def apply_configuration():
    """Apply a selected configuration to the automated scheduler"""
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No configuration data provided'
            }), 400

        config = data.get('config')
        config_name = data.get('configName', 'Unknown Configuration')
        
        if not config:
            return jsonify({
                'success': False,
                'error': 'Configuration is required'
            }), 400        # Apply configuration to the automated scheduler
        try:
            from app.services.automated_scheduler import get_scheduler
            from app.services.notification_service import get_notification_service
            from app.services.configuration_scheduler import get_configuration_scheduler
            
            # Apply to new intelligent configuration scheduler
            config_scheduler = get_configuration_scheduler()
            
            # Start scheduler if not running
            if not config_scheduler.is_running:
                config_scheduler.start()
                
            # Apply the configuration
            config_scheduler.apply_configuration(config, config_name)
            
            # Also try to apply to existing automated scheduler (backward compatibility)
            try:
                scheduler = get_scheduler()
                
                # Update scheduler configuration with new settings
                scheduler_config = {
                    'pump': {
                        'soil_moisture_threshold': config.get('pump', {}).get('soilMoistureThreshold', 50),
                        'schedules': config.get('pump', {}).get('schedules', []),
                        'check_intervals': config.get('pump', {}).get('checkIntervals', [])
                    },
                    'fan': {
                        'temp_threshold': config.get('fan', {}).get('tempThreshold', 28),
                        'humidity_threshold': config.get('fan', {}).get('humidityThreshold', 85),
                        'duration': config.get('fan', {}).get('duration', 15),
                        'check_interval': config.get('fan', {}).get('checkInterval', 30)
                    },
                    'cover': {
                        'temp_threshold': config.get('cover', {}).get('tempThreshold', 30),
                        'schedules': config.get('cover', {}).get('schedules', [])
                    }
                }            
                # Apply the new configuration
                scheduler.update_configuration(scheduler_config)
                
                # Force immediate configuration check
                scheduler.force_check()
                
            except Exception as old_scheduler_error:
                logger.warning(f"Old scheduler not available: {old_scheduler_error}")
            
            # Add notification
            try:
                notification_service = get_notification_service()
                notification_service.add_scheduler_notification(
                    f"Cấu hình vận hành '{config_name}' đã được áp dụng thành công và đang hoạt động tự động",
                    {
                        'config_name': config_name,
                        'applied_at': datetime.now().isoformat(),
                        'config_applied': True,
                        'scheduler_status': 'active'
                    }
                )
            except Exception as notification_error:
                logger.warning(f"Could not send notification: {notification_error}")
            
            logger.info(f"Configuration '{config_name}' applied successfully to intelligent scheduler")
            
        except Exception as scheduler_error:
            logger.error(f"Error applying configuration to scheduler: {scheduler_error}")
            # Don't fail the request if scheduler update fails
            pass

        return jsonify({
            'success': True,
            'message': f'Configuration "{config_name}" applied successfully',
            'data': {
                'config_name': config_name,
                'applied_at': datetime.now().isoformat()
            }
        })

    except Exception as e:
        logger.error(f"Error applying configuration: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/configurations/presets', methods=['GET'])
@rate_limit
def get_configuration_presets():
    """Get available configuration presets"""
    try:
        # Default configuration presets
        presets = {
            "cay-non": {
                "name": "Giai đoạn cây non",
                "description": "Cấu hình tối ưu cho cây non - tưới nhiều, che nắng cẩn thận",
                "pump": {
                    "soilMoistureThreshold": 60,
                    "schedules": [
                        {"time": "05:00", "duration": 5},
                        {"time": "17:00", "duration": 5}
                    ],
                    "checkIntervals": [
                        {"start": "06:00", "end": "10:00", "interval": 2},
                        {"start": "14:00", "end": "17:00", "interval": 2}
                    ]
                },
                "fan": {
                    "tempThreshold": 28,
                    "humidityThreshold": 85,
                    "duration": 15,
                    "checkInterval": 30
                },
                "cover": {
                    "tempThreshold": 30,
                    "schedules": [
                        {"start": "10:00", "end": "14:00", "position": "closed"},
                        {"start": "06:00", "end": "10:00", "position": "open"},
                        {"start": "14:00", "end": "18:00", "position": "open"},
                        {"start": "18:00", "end": "06:00", "position": "open"}
                    ]
                }
            },
            "cay-truong-thanh": {
                "name": "Giai đoạn cây trưởng thành",
                "description": "Cấu hình cho cây trưởng thành - ít tưới hơn, thông gió tốt",
                "pump": {
                    "soilMoistureThreshold": 60,
                    "schedules": [
                        {"time": "05:00", "duration": 10}
                    ],
                    "checkIntervals": [
                        {"start": "06:00", "end": "10:00", "interval": 2},
                        {"start": "14:00", "end": "17:00", "interval": 2}
                    ]
                },
                "fan": {
                    "tempThreshold": 28,
                    "humidityThreshold": 85,
                    "duration": 15,
                    "checkInterval": 30
                },
                "cover": {
                    "tempThreshold": 30,
                    "schedules": [
                        {"start": "10:00", "end": "14:00", "position": "closed"},
                        {"start": "06:00", "end": "10:00", "position": "open"},
                        {"start": "14:00", "end": "18:00", "position": "open"},
                        {"start": "18:00", "end": "06:00", "position": "open"}
                    ]
                }
            }
        }
        
        return jsonify({
            'success': True,
            'data': presets
        })

    except Exception as e:
        logger.error(f"Error getting configuration presets: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/configurations/scheduler/status', methods=['GET'])
@rate_limit
def get_scheduler_status():
    """Get configuration scheduler status"""
    try:
        from app.services.configuration_scheduler import get_configuration_scheduler
        
        scheduler = get_configuration_scheduler()
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

@bp.route('/api/configurations/scheduler/start', methods=['POST'])
@rate_limit  
def start_scheduler():
    """Start the configuration scheduler"""
    try:
        from app.services.configuration_scheduler import get_configuration_scheduler
        
        scheduler = get_configuration_scheduler()
        
        if scheduler.is_running:
            return jsonify({
                'success': True,
                'message': 'Scheduler is already running'
            })
            
        scheduler.start()
        
        return jsonify({
            'success': True,
            'message': 'Configuration scheduler started successfully'
        })
        
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/configurations/scheduler/stop', methods=['POST'])
@rate_limit
def stop_scheduler():
    """Stop the configuration scheduler"""
    try:
        from app.services.configuration_scheduler import get_configuration_scheduler
        
        scheduler = get_configuration_scheduler()
        
        if not scheduler.is_running:
            return jsonify({
                'success': True,
                'message': 'Scheduler is already stopped'
            })
            
        scheduler.stop()
        
        return jsonify({
            'success': True,
            'message': 'Configuration scheduler stopped successfully'
        })
        
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/configurations/scheduler/force-check', methods=['POST'])
@rate_limit
def force_scheduler_check():
    """Force immediate condition check"""
    try:
        from app.services.configuration_scheduler import get_configuration_scheduler
        
        scheduler = get_configuration_scheduler()
        
        if not scheduler.is_running:
            return jsonify({
                'success': False,
                'error': 'Scheduler is not running'
            }), 400
            
        # Force immediate check by calling the check method directly
        scheduler._check_and_control_devices()
        
        return jsonify({
            'success': True,
            'message': 'Forced condition check completed'
        })
        
    except Exception as e:
        logger.error(f"Error forcing scheduler check: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
