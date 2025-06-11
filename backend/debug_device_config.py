#!/usr/bin/env python3
"""Debug the device configuration update issue"""

import psycopg2
import json
import traceback

def debug_device_config_issue():
    """Debug the device config update issue"""
    
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='greenhouse',
            user='postgres',
            password='admin123'
        )
        cur = conn.cursor()
        
        # Check if the device exists in device_states (foreign key constraint)
        print("=== Checking device_states table ===")
        cur.execute("SELECT id, type, name FROM device_states ORDER BY id")
        devices = cur.fetchall()
        print("Existing devices:")
        for device in devices:
            print(f"  {device}")
        
        # Check existing config for pump1
        print("\n=== Current pump1 config ===")
        cur.execute("SELECT * FROM device_configs WHERE device_id = 'pump1'")
        config = cur.fetchone()
        if config:
            print(f"Current config: {config}")
        else:
            print("No config found for pump1")
        
        # Try to manually update the config
        print("\n=== Testing manual config update ===")
        
        test_config = {
            'mode': 'automatic',
            'schedule_type': 'interval',
            'duration_minutes': 5,
            'check_interval_minutes': 30,
            'start_humidity': 40.0,
            'end_humidity': 60.0,
            'active_hours': json.dumps({"morning": ["05:00"], "evening": ["17:00"]}),
            'plant_stage': 'young'
        }
        
        try:
            update_query = """
                UPDATE device_configs
                SET mode = %s,
                    schedule_type = %s,
                    start_humidity = %s,
                    end_humidity = %s,
                    start_temperature = %s,
                    end_temperature = %s,
                    duration_minutes = %s,
                    check_interval_minutes = %s,
                    active_hours = %s::jsonb,
                    plant_stage = %s,
                    last_updated = CURRENT_TIMESTAMP
                WHERE device_id = %s
            """
            
            cur.execute(update_query, (
                test_config['mode'],
                test_config['schedule_type'],
                test_config['start_humidity'],
                test_config['end_humidity'],
                None,  # start_temperature
                None,  # end_temperature
                test_config['duration_minutes'],
                test_config['check_interval_minutes'],
                test_config['active_hours'],
                test_config['plant_stage'],
                'pump1'
            ))
            
            print(f"Rows affected: {cur.rowcount}")
            conn.commit()
            
            if cur.rowcount > 0:
                print("✅ Manual update successful")
                
                # Verify the update
                cur.execute("SELECT mode, schedule_type, active_hours FROM device_configs WHERE device_id = 'pump1'")
                updated_config = cur.fetchone()
                print(f"Updated config: {updated_config}")
            else:
                print("❌ No rows updated - device might not exist")
                
        except Exception as e:
            print(f"❌ Manual update failed: {e}")
            conn.rollback()
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Database connection error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_device_config_issue()
