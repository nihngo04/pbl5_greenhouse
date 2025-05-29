import multiprocessing
import os

# Server socket
bind = '0.0.0.0:5000'
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Process naming
proc_name = 'greenhouse'
pythonpath = '.'

# Logging
accesslog = os.path.join('logs', 'gunicorn.access.log')
errorlog = os.path.join('logs', 'gunicorn.error.log')
loglevel = 'info'

# Process management
daemon = False
pidfile = 'greenhouse.pid'

# SSL (uncomment for HTTPS)
# keyfile = 'ssl/private.key'
# certfile = 'ssl/cert.pem'

# Server mechanics
user = None
group = None
tmp_upload_dir = None

# Thread/Worker behavior
preload_app = True
reload = False  # Set to True for development
spew = False
check_config = False