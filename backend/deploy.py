import os
import sys
import subprocess
import argparse
from datetime import datetime

def setup_directories():
    """Create necessary directories"""
    dirs = ['logs', 'data/images', 'ssl']
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    print("✓ Directories created")

def setup_virtualenv():
    """Create and activate virtual environment"""
    if not os.path.exists('venv'):
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("✓ Virtual environment created")
    
    # Install requirements
    pip_cmd = os.path.join('venv', 'bin' if os.name != 'nt' else 'Scripts', 'pip')
    subprocess.run([pip_cmd, 'install', '-r', 'requirements.txt'], check=True)
    print("✓ Dependencies installed")

    # Ensure gunicorn is installed
    subprocess.run([pip_cmd, 'install', 'gunicorn'], check=True)
    print("✓ Gunicorn installed")

def setup_environment():
    """Create .env file if not exists"""
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(f'''# Generated on {datetime.now().isoformat()}
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY={os.urandom(24).hex()}
DATABASE_URL=postgresql://postgres:admin123@localhost:5432/greenhouse
MQTT_BROKER=localhost
MQTT_PORT=1883
''')
        print("✓ Environment file created")
    else:
        print("! Environment file already exists")

def check_dependencies():
    """Check if all required services are installed"""
    services = {
        'psql': 'PostgreSQL/TimescaleDB',
        'mosquitto': 'Mosquitto MQTT broker'
    }
    
    missing = []
    for service, name in services.items():
        try:
            result = subprocess.run(['where' if os.name == 'nt' else 'which', service], 
                                   capture_output=True, text=True, check=True)
            if not result.stdout.strip():
                missing.append(name)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing.append(name)
    
    if missing:
        print(f"✗ Missing services: {', '.join(missing)}")
        print("  - For TimescaleDB, ensure PostgreSQL is running on port 5432")
        print("  - For Mosquitto, ensure it is installed and running on port 1883")
        return False
    
    print("✓ All required services found")
    return True

def main():
    parser = argparse.ArgumentParser(description='Greenhouse Backend Deployment Tool')
    parser.add_argument('--check', action='store_true', 
                       help='Check dependencies only')
    parser.add_argument('--setup', action='store_true',
                       help='Setup environment')
    args = parser.parse_args()
    
    if args.check:
        check_dependencies()
        return
    
    if args.setup or input("Run full setup? [y/N] ").lower() == 'y':
        print("\nSetting up Greenhouse Backend...")
        setup_directories()
        setup_virtualenv()
        setup_environment()
        check_dependencies()
        print("\nSetup complete!")
        print("""
Next steps:
1. Ensure PostgreSQL/TimescaleDB and Mosquitto are running
2. Create the database: createdb greenhouse
3. Start the application with: 
   venv\\Scripts\\gunicorn -c gunicorn.conf.py run:app (Windows)
   or
   source venv/bin/activate && gunicorn -c gunicorn.conf.py run:app (Linux/macOS)
""")

if __name__ == '__main__':
    main()