"""
Camera Service for ESP32-CAM Integration
Handles image capture from ESP32-CAM devices
"""

import os
import requests
from datetime import datetime
from typing import Optional, Dict, Any
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class ESP32CameraService:
    def __init__(self, camera_ip: str = "192.168.141.171", 
                 default_quality: int = 10, 
                 default_resolution: str = "UXGA"):
        """
        Initialize ESP32 Camera Service
        
        Args:
            camera_ip: IP address của ESP32-CAM
            default_quality: Chất lượng ảnh mặc định (10-63, thấp hơn = chất lượng cao hơn)
            default_resolution: Resolution mặc định
        """
        self.camera_ip = camera_ip
        self.default_quality = default_quality
        self.default_resolution = default_resolution
        self.base_url = f"http://{camera_ip}"
        
        # Tạo session với retry logic
        self.session = self._create_session_with_retries()
    
    def _create_session_with_retries(self):
        """Tạo session với retry logic"""
        session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[408, 409, 429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    def check_camera_status(self) -> Dict[str, Any]:
        """Kiểm tra trạng thái camera"""
        try:
            capture_url = f"{self.base_url}/capture?quality={self.default_quality}&resolution={self.default_resolution}"
            response = self.session.get(capture_url, timeout=(2, 5))
            
            if response.status_code == 200:
                return {
                    'status': 'online',
                    'message': 'ESP32 camera is accessible',
                    'ip': self.camera_ip
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Camera returned status code: {response.status_code}',
                    'ip': self.camera_ip
                }
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            logger.warning(f"ESP32 camera not accessible: {str(e)}")
            return {
                'status': 'offline',
                'message': 'ESP32 camera is not accessible',
                'ip': self.camera_ip
            }
        except Exception as e:
            logger.error(f"Error checking camera status: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error checking camera: {str(e)}',
                'ip': self.camera_ip
            }
    
    def capture_image(self, save_path: str, 
                     resolution: Optional[str] = None, 
                     quality: Optional[int] = None) -> Dict[str, Any]:
        """
        Chụp ảnh từ ESP32-CAM và lưu vào đường dẫn chỉ định
        
        Args:
            save_path: Đường dẫn lưu ảnh
            resolution: Resolution (UXGA, SXGA, XGA, SVGA, VGA, CIF)
            quality: Chất lượng ảnh (10-63)
            
        Returns:
            Dict chứa thông tin kết quả
        """
        resolution = resolution or self.default_resolution
        quality = quality or self.default_quality
        
        try:
            # Tạo thư mục nếu chưa tồn tại
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Tạo URL capture
            capture_url = f"{self.base_url}/capture?resolution={resolution}&quality={quality}"
            
            logger.info(f"Capturing image from ESP32-CAM: {capture_url}")
            response = self.session.get(capture_url, timeout=10)
            
            if response.status_code == 200:
                # Lưu ảnh
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content)
                
                logger.info(f"Image captured successfully: {save_path} ({file_size} bytes)")
                
                return {
                    'status': 'success',
                    'message': 'Image captured and saved successfully',
                    'file_path': save_path,
                    'file_size': file_size,
                    'resolution': resolution,
                    'quality': quality,
                    'camera_ip': self.camera_ip
                }
            else:
                error_msg = f"Failed to capture image: HTTP {response.status_code}"
                logger.error(error_msg)
                return {
                    'status': 'error',
                    'message': error_msg
                }
                
        except requests.exceptions.Timeout:
            error_msg = "ESP32 camera connection timed out"
            logger.error(error_msg)
            return {
                'status': 'error',
                'message': error_msg
            }
        except requests.exceptions.ConnectionError:
            error_msg = "Cannot connect to ESP32 camera"
            logger.error(error_msg)
            return {
                'status': 'error',
                'message': error_msg
            }
        except Exception as e:
            error_msg = f"Error capturing image: {str(e)}"
            logger.error(error_msg)
            return {
                'status': 'error',
                'message': error_msg
            }
    
    def generate_filename(self, prefix: str = "esp32cam", extension: str = "jpg") -> str:
        """Tạo tên file với timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{extension}"

# Singleton instance
_camera_service = None

def get_camera_service() -> ESP32CameraService:
    """Get singleton camera service instance"""
    global _camera_service
    if _camera_service is None:
        _camera_service = ESP32CameraService()
    return _camera_service
