import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from app.config import Config

def generate_test_data():
    """Generate test sensor data for visualization"""
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    
    # Generate data for the past 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    current = start_date
    
    # Base values and fluctuation ranges
    sensors = {
        'temperature': {'base': 25, 'range': 5},  # 20-30°C
        'humidity': {'base': 70, 'range': 10},    # 60-80%
        'soil_moisture': {'base': 50, 'range': 20},  # 30-70%
        'light_intensity': {'base': 5000, 'range': 3000}  # 2000-8000 lux
    }
    
    test_data = []
    while current <= end_date:
        # Generate hourly data
        hour = current.hour
        
        # Adjust base values based on time of day
        for sensor_type, config in sensors.items():
            base = config['base']
            range_val = config['range']
            
            # Add time-based variations
            if sensor_type == 'temperature':
                # Higher during day, lower at night
                if 6 <= hour < 18:
                    base += 2
                else:
                    base -= 2
            elif sensor_type == 'humidity':
                # Higher at night and early morning
                if hour < 6 or hour >= 18:
                    base += 5
            elif sensor_type == 'light_intensity':
                # Simulate daylight
                if hour < 6 or hour >= 18:
                    base = 0
                    range_val = 100
                elif 10 <= hour < 14:
                    base = 7000
                    range_val = 1000
            
            # Add random variation
            value = base + random.uniform(-range_val/2, range_val/2)
            
            # Ensure values stay within reasonable ranges
            if sensor_type == 'humidity' or sensor_type == 'soil_moisture':
                value = max(0, min(100, value))
            elif sensor_type == 'light_intensity':
                value = max(0, value)
            
            test_data.append({
                'time': current,
                'device_id': 'test_device',
                'sensor_type': sensor_type,
                'value': round(value, 2)
            })
        
        current += timedelta(hours=1)
    
    try:
        # Use SQLAlchemy 2.0 style transaction management
        with engine.begin() as conn:
            # Clear existing test data
            conn.execute(text("DELETE FROM sensor_data WHERE device_id = 'test_device';"))
            
            # Insert new test data in batches
            batch_size = 1000
            for i in range(0, len(test_data), batch_size):
                batch = test_data[i:i + batch_size]
                conn.execute(
                    text("""
                        INSERT INTO sensor_data (time, device_id, sensor_type, value)
                        VALUES (:time, :device_id, :sensor_type, :value);
                    """),
                    batch
                )
                
            print(f"Generated {len(test_data)} test data points")
            
    except Exception as e:
        print(f"Error generating test data: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Generating test data...")
    success = generate_test_data()
    print("Test data generation:", "successful" if success else "failed")