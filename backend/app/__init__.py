import os
from datetime import datetime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from app.config import Config
from app.utils.error_handlers import register_error_handlers
from app.utils.logging import setup_logging

db = SQLAlchemy()

def create_app(config_class=Config):
    """Application factory pattern để tạo Flask app"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Set up logging first
    setup_logging(app)
    
    # Đảm bảo các thư mục cần thiết tồn tại
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Register error handlers
        register_error_handlers(app)
        
        # Initialize MQTT client
        from app.services.mqtt_client import setup_mqtt_client
        try:
            mqtt_client = setup_mqtt_client()
            app.logger.info("MQTT client initialized successfully")
        except Exception as e:
            app.logger.error(f"Failed to initialize MQTT client: {e}")
        
        # Register blueprints
        from app.api import sensors, images, monitoring
        app.register_blueprint(sensors.bp)
        app.register_blueprint(images.bp)
        app.register_blueprint(monitoring.bp)
        
        @app.route('/health')
        def health_check():
            """Basic health check endpoint"""
            from app.services.cache_service import get_cache_stats
            return jsonify({
                'status': 'healthy',
                'version': '1.0.0',
                'timestamp': datetime.utcnow().isoformat(),
                'cache_status': get_cache_stats()
            })
        
        @app.before_request
        def before_request():
            """Log request information"""
            app.logger.debug(f"Request: {request.method} {request.path}")
        
        @app.after_request
        def after_request(response):
            """Log response information"""
            app.logger.debug(f"Response: {response.status}")
            return response
        
        # Initialize TimescaleDB
        from app.services.timescale import init_timescaledb
        try:
            init_timescaledb()
            app.logger.info("TimescaleDB initialized successfully")
        except Exception as e:
            app.logger.error(f"Failed to initialize TimescaleDB: {e}")
        
        app.logger.info('Application initialized successfully')
    
    return app