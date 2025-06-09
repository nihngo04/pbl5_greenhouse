import os
import sys

# Force UTF-8 encoding for Windows console
os.environ['PYTHONIOENCODING'] = 'utf-8'

from app import create_app

app = create_app()

if __name__ == '__main__':
    # Disable reloader and use threaded mode for better stability
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False, threaded=True)