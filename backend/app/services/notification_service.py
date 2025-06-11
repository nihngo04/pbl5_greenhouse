"""
Simple notification service for the greenhouse system
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"

@dataclass
class Notification:
    id: str
    type: NotificationType
    title: str
    message: str
    timestamp: datetime
    read: bool = False
    data: Optional[Dict] = None

class NotificationService:
    """Simple in-memory notification service"""
    
    def __init__(self):
        self.notifications: List[Notification] = []
        self.max_notifications = 100
    
    def add_notification(self, 
                        notification_type: NotificationType,
                        title: str,
                        message: str,
                        data: Optional[Dict] = None) -> str:
        """Add a new notification"""
        
        notification_id = f"notif_{int(datetime.now().timestamp())}"
        
        notification = Notification(
            id=notification_id,
            type=notification_type,
            title=title,
            message=message,
            timestamp=datetime.now(),
            data=data
        )
        
        self.notifications.insert(0, notification)  # Add to beginning
          # Keep only the most recent notifications
        if len(self.notifications) > self.max_notifications:
            self.notifications = self.notifications[:self.max_notifications]
        
        logger.info(f"Notification added: {title}")
        return notification_id
    
    def get_notifications(self, unread_only: bool = False) -> List[Dict]:
        """Get notifications"""
        notifications = self.notifications
        
        if unread_only:
            notifications = [n for n in notifications if not n.read]
        
        # Convert to dict and handle enum serialization
        result = []
        for n in notifications:
            notification_dict = asdict(n)
            # Convert enum to string value
            notification_dict['type'] = n.type.value
            # Convert datetime to ISO string
            notification_dict['timestamp'] = n.timestamp.isoformat()
            result.append(notification_dict)
        
        return result
    
    def mark_as_read(self, notification_id: str) -> bool:
        """Mark a notification as read"""
        for notification in self.notifications:
            if notification.id == notification_id:
                notification.read = True
                return True
        return False
    
    def mark_all_as_read(self) -> int:
        """Mark all notifications as read"""
        count = 0
        for notification in self.notifications:
            if not notification.read:
                notification.read = True
                count += 1
        return count
    
    def clear_notifications(self) -> int:
        """Clear all notifications"""
        count = len(self.notifications)
        self.notifications.clear()
        return count
    
    def add_conflict_notification(self, device_type: str, conflict_details: Dict):
        """Add a conflict-specific notification"""
        self.add_notification(
            NotificationType.WARNING,
            f"Xung đột cấu hình {device_type}",
            f"Phát hiện xung đột trong cấu hình thiết bị {device_type}. "
            f"Vui lòng kiểm tra và điều chỉnh cài đặt.",
            {
                'device_type': device_type,
                'conflict_details': conflict_details,
                'action_required': True
            }
        )
    
    def add_scheduler_notification(self, message: str, data: Optional[Dict] = None):
        """Add a scheduler-related notification"""
        self.add_notification(
            NotificationType.INFO,
            "Cập nhật hệ thống tự động",
            message,
            data
        )
    
    def add_device_notification(self, device_type: str, message: str, success: bool = True):
        """Add a device control notification"""
        notification_type = NotificationType.SUCCESS if success else NotificationType.ERROR
        self.add_notification(
            notification_type,
            f"Điều khiển {device_type}",
            message,
            {'device_type': device_type}
        )

# Global notification service instance
notification_service = NotificationService()

def get_notification_service() -> NotificationService:
    """Get the global notification service instance"""
    return notification_service
