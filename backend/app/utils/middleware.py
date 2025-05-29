import time
from functools import wraps
from flask import request, jsonify
import logging
from app.utils import ValidationError

logger = logging.getLogger(__name__)

# Simple in-memory rate limiting store
# In production, consider using Redis
rate_limit_store = {}

def rate_limit(f):
    """Rate limiting decorator
    
    Limits requests to 60 per minute per IP address
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = request.remote_addr
        current = time.time()
        
        # Initialize or clean old requests
        if ip not in rate_limit_store:
            rate_limit_store[ip] = []
        rate_limit_store[ip] = [ts for ts in rate_limit_store[ip] 
                               if current - ts < 60]  # Keep last minute
        
        # Check rate limit
        if len(rate_limit_store[ip]) >= 60:
            logger.warning(f"Rate limit exceeded for IP: {ip}")
            return jsonify({
                'success': False,
                'error': 'Rate limit exceeded. Please try again later.'
            }), 429
        
        # Add request timestamp
        rate_limit_store[ip].append(current)
        
        return f(*args, **kwargs)
    return decorated_function

def validate_query_params(*required_params):
    """Decorator to validate required query parameters
    
    Args:
        *required_params: List of required parameter names
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            missing = []
            for param in required_params:
                if param not in request.args:
                    missing.append(param)
            
            if missing:
                raise ValidationError(
                    f"Missing required query parameters: {', '.join(missing)}"
                )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_json_body(*required_fields):
    """Decorator to validate required JSON body fields
    
    Args:
        *required_fields: List of required field names
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                raise ValidationError("Request must be JSON")
            
            data = request.get_json()
            missing = []
            
            for field in required_fields:
                if field not in data:
                    missing.append(field)
            
            if missing:
                raise ValidationError(
                    f"Missing required fields: {', '.join(missing)}"
                )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def cors_preflight(methods=None):
    """Decorator to handle CORS preflight requests
    
    Args:
        methods: List of allowed HTTP methods
    """
    if methods is None:
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method == 'OPTIONS':
                return jsonify({
                    'success': True,
                    'allowed_methods': methods
                }), 200, {
                    'Access-Control-Allow-Methods': ', '.join(methods),
                    'Access-Control-Allow-Headers': 'Content-Type'
                }
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator