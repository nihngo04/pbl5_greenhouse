#!/usr/bin/env python3
"""
Script để thêm test data vào database cho Disease Detection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.detection_history import DetectionHistory, DetectionStatistics
from datetime import datetime, date, timedelta
import json
import random

def create_sample_detection_history():
    """Tạo sample detection history data"""
    print("🔄 Creating sample detection history...")
    
    # Sample AI results
    sample_results = [
        {
            "leaf_index": 1,
            "predicted_class": "Healthy-Leaf",
            "confidence": 0.95,
            "type": "healthy",
            "severity": "low"
        },
        {
            "leaf_index": 1,
            "predicted_class": "Anthracnose",
            "confidence": 0.87,
            "type": "disease",
            "severity": "high"
        },
        {
            "leaf_index": 1,
            "predicted_class": "Bacterial-Spot",
            "confidence": 0.72,
            "type": "disease",
            "severity": "medium"
        },
        {
            "leaf_index": 1,
            "predicted_class": "Downy-Mildew",
            "confidence": 0.68,
            "type": "disease",
            "severity": "medium"
        },
        {
            "leaf_index": 1,
            "predicted_class": "Pest-Damage",
            "confidence": 0.91,
            "type": "pest",
            "severity": "high"
        }
    ]
    
    # Tạo detection history cho 7 ngày qua
    for i in range(7):
        detection_date = datetime.now() - timedelta(days=i)
        
        # Tạo 2-5 detections mỗi ngày
        num_detections = random.randint(2, 5)
        
        for j in range(num_detections):
            # Random chọn result type
            ai_result = random.choice(sample_results)
            
            # Random method
            method = random.choice(['automatic', 'manual'])
            camera_status = 'online' if method == 'automatic' else 'offline'
            
            # Tạo timestamp random trong ngày
            detection_time = detection_date.replace(
                hour=random.randint(6, 18),
                minute=random.randint(0, 59),
                second=random.randint(0, 59)
            )
            
            detection = DetectionHistory(
                timestamp=detection_time,
                original_image_path=f"/data/images/test_{detection_time.strftime('%Y%m%d_%H%M%S')}.jpg",
                detection_method=method,
                camera_status=camera_status,
                ai_results=[ai_result]  # This will trigger the setter
            )
            
            db.session.add(detection)
    
    try:
        db.session.commit()
        print("✅ Sample detection history created successfully!")
    except Exception as e:
        print(f"❌ Error creating detection history: {e}")
        db.session.rollback()

def create_sample_statistics():
    """Tạo sample statistics data"""
    print("🔄 Creating sample statistics...")
    
    # Tạo statistics cho 7 ngày qua
    for i in range(7):
        stat_date = date.today() - timedelta(days=i)
        
        # Random data với xu hướng realistic
        total = random.randint(2, 8)
        automatic = random.randint(1, total)
        manual = total - automatic
        diseases = random.randint(0, total//2)
        healthy = total - diseases
        
        # Severity distribution
        high_sev = random.randint(0, diseases)
        medium_sev = random.randint(0, diseases - high_sev)
        low_sev = diseases - high_sev - medium_sev
        
        statistic = DetectionStatistics(
            date=stat_date,
            total_detections=total,
            automatic_detections=automatic,
            manual_detections=manual,
            diseases_detected=diseases,
            healthy_detections=healthy,
            high_severity_count=high_sev,
            medium_severity_count=medium_sev,
            low_severity_count=low_sev,
            camera_online_count=automatic,
            camera_offline_count=manual,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.session.add(statistic)
    
    try:
        db.session.commit()
        print("✅ Sample statistics created successfully!")
    except Exception as e:
        print(f"❌ Error creating statistics: {e}")
        db.session.rollback()

def clear_existing_data():
    """Clear existing test data"""
    print("🗑️  Clearing existing detection data...")
    
    try:
        # Delete in correct order due to potential foreign keys
        DetectionStatistics.query.delete()
        DetectionHistory.query.delete()
        db.session.commit()
        print("✅ Existing data cleared!")
    except Exception as e:
        print(f"❌ Error clearing data: {e}")
        db.session.rollback()

def show_data_summary():
    """Show summary of created data"""
    print("\n📊 Data Summary:")
    print("=" * 40)
    
    # Detection History
    total_detections = DetectionHistory.query.count()
    automatic_count = DetectionHistory.query.filter_by(detection_method='automatic').count()
    manual_count = DetectionHistory.query.filter_by(detection_method='manual').count()
    disease_count = DetectionHistory.query.filter_by(disease_detected=True).count()
    
    print(f"Detection History:")
    print(f"  Total detections: {total_detections}")
    print(f"  Automatic: {automatic_count}")
    print(f"  Manual: {manual_count}")
    print(f"  With diseases: {disease_count}")
    
    # Statistics
    stats_count = DetectionStatistics.query.count()
    print(f"\nDaily Statistics:")
    print(f"  Days with data: {stats_count}")
    
    # Recent detections
    recent = DetectionHistory.query.order_by(DetectionHistory.timestamp.desc()).limit(3).all()
    print(f"\nMost Recent Detections:")
    for detection in recent:
        print(f"  {detection.timestamp.strftime('%Y-%m-%d %H:%M')} - {detection.predicted_class} ({detection.detection_method})")

def main():
    """Main function"""
    print("🚀 Disease Detection Database Setup")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Ask user if they want to clear existing data
        if DetectionHistory.query.count() > 0 or DetectionStatistics.query.count() > 0:
            response = input("📝 Existing data found. Clear it? (y/N): ").strip().lower()
            if response == 'y':
                clear_existing_data()
        
        # Create sample data
        create_sample_detection_history()
        create_sample_statistics()
        
        # Show summary
        show_data_summary()
        
        print("\n🎉 Database setup complete!")
        print("\nℹ️  You can now test the API endpoints:")
        print("  - GET /api/disease-detection/history")
        print("  - GET /api/disease-detection/statistics")
        print("  - GET /api/disease-detection/recent-activity")

if __name__ == "__main__":
    main()
