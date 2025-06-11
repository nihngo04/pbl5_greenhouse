#!/usr/bin/env python3
"""Check database structure for device_configs table"""

import psycopg2
import traceback

try:
    conn = psycopg2.connect(
        host='localhost',
        database='greenhouse',
        user='postgres',
        password='admin123'
    )
    cur = conn.cursor()
    
    # Check if device_configs table exists and its structure
    cur.execute("""
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'device_configs' 
        ORDER BY ordinal_position;
    """)
    
    columns = cur.fetchall()
    if columns:
        print('Device Configs Table Structure:')
        for col in columns:
            print(f'  {col[0]}: {col[1]} ({col[2]})')
    else:
        print('Device configs table not found')
    
    # Check existing data
    cur.execute('SELECT device_id, mode, schedule_type FROM device_configs LIMIT 3')
    rows = cur.fetchall()
    print('\nExisting data:')
    for row in rows:
        print(f'  {row}')
        
    cur.close()
    conn.close()
    
except Exception as e:
    print('Database Error:', e)
    traceback.print_exc()
