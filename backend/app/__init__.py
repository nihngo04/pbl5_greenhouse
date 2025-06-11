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
        register_error_handlers(app)        # Initialize MQTT client on-demand (to prevent startup hanging)
        # MQTT will be initialized when first requested
        app.logger.info("MQTT client will be initialized on first use")        # Register blueprints
        from app.api import sensors, images, monitoring, control, devices, dashboard, scheduler, notifications, configurations
        app.register_blueprint(sensors.bp)
        app.register_blueprint(images.bp)
        app.register_blueprint(monitoring.bp)
        app.register_blueprint(control.router)
        app.register_blueprint(devices.bp)
        app.register_blueprint(dashboard.bp)
        app.register_blueprint(scheduler.bp)
        app.register_blueprint(notifications.bp)
        app.register_blueprint(configurations.bp)
        
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
        
        # Initialize Configuration Scheduler
        from app.services.configuration_scheduler import get_configuration_scheduler
        try:
            scheduler = get_configuration_scheduler()
            app.logger.info("Configuration scheduler initialized and ready")
        except Exception as e:
            app.logger.error(f"Failed to initialize configuration scheduler: {e}")
        
        app.logger.info('Application initialized successfully')
    
    return app