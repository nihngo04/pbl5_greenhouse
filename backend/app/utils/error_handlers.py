from flask import jsonify
from app.utils.helpers import GreenhouseError, SensorError, StorageError, ValidationError

def register_error_handlers(app):
    """Register error handlers for the Flask app"""
    
    @app.errorhandler(SensorError)
    def handle_sensor_error(error):
        return jsonify({
            'success': False,
            'error': str(error),
            'error_type': 'sensor_error'
        }), 500

    @app.errorhandler(StorageError)
    def handle_storage_error(error):
        return jsonify({
            'success': False,
            'error': str(error),
            'error_type': 'storage_error'
        }), 500

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return jsonify({
            'success': False,
            'error': str(error),
            'error_type': 'validation_error'
        }), 400

    @app.errorhandler(GreenhouseError)
    def handle_greenhouse_error(error):
        return jsonify({
            'success': False,
            'error': str(error),
            'error_type': 'greenhouse_error'
        }), 500

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            'success': False,
            'error': 'Resource not found',
            'error_type': 'not_found'
        }), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 'Method not allowed',
            'error_type': 'method_not_allowed'
        }), 405

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        return jsonify({
            'success': False,
            'error': str(error),
            'error_type': 'internal_error'
        }), 500