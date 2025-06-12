# Hướng Dẫn Cài Đặt GreenMind

## 📋 Yêu Cầu Hệ Thống

### Phần Cứng
- **Máy tính/Laptop**: Windows 10+, macOS 10.15+, hoặc Ubuntu 18.04+
- **RAM**: Tối thiểu 8GB (khuyến nghị 16GB)
- **Ổ cứng**: 10GB dung lượng trống
- **Kết nối mạng**: WiFi hoặc Ethernet

### Phần Mềm
- **Node.js**: Version 18+ ([Download](https://nodejs.org/))
- **Python**: Version 3.8+ ([Download](https://python.org/))
- **PostgreSQL**: Version 13+ ([Download](https://postgresql.org/))
- **Git**: ([Download](https://git-scm.com/))

## 🚀 Hướng Dẫn Cài Đặt

### Bước 1: Clone Repository

```bash
# Clone project từ GitHub
git clone https://github.com/your-username/greenhouse.git
cd greenhouse
```

### Bước 2: Cài Đặt PostgreSQL

1. **Tải và cài đặt PostgreSQL** từ trang chủ
2. **Tạo database:**
```sql
-- Mở PostgreSQL command line
psql -U postgres

-- Tạo database
CREATE DATABASE greenhouse;

-- Tạo user (tùy chọn)
CREATE USER greenhouse_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE greenhouse TO greenhouse_user;
```

### Bước 3: Cấu Hình Backend

```bash
# Di chuyển vào thư mục backend
cd backend

# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### Bước 4: Cấu Hình Database

```bash
# Chạy migration để tạo tables
python init_db.py

# Hoặc sử dụng Flask commands
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Bước 5: Cài Đặt Frontend

```bash
# Di chuyển vào thư mục frontend
cd ../frontend

# Cài đặt dependencies
npm install
# hoặc
pnpm install
```

## ⚙️ Cấu Hình Địa Chỉ IP

### 🔧 Cấu Hình Backend

Chỉnh sửa file `backend/app/config.py`:

```python
class Config:
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost:5432/greenhouse'
    
    # MQTT Configuration - QUAN TRỌNG: Thay đổi IP này
    MQTT_BROKER = '192.168.141.250'  # ← Thay bằng IP Raspberry Pi của bạn 
    MQTT_PORT = 1883
    MQTT_USERNAME = None  # Nếu có authentication
    MQTT_PASSWORD = None  # Nếu có authentication
```

### 📡 Cấu Hình MQTT Broker (Raspberry Pi)

**IP mặc định cần thay đổi: `192.168.141.250`**

1. **Kiểm tra IP của Raspberry Pi:**
```bash
# Trên Raspberry Pi
ip addr show
# hoặc
ifconfig
```

2. **Cài đặt MQTT Broker trên Raspberry Pi:**
```bash
# Cài đặt Mosquitto
sudo apt update
sudo apt install mosquitto mosquitto-clients

# Khởi động service
sudo systemctl start mosquitto
sudo systemctl enable mosquitto
```

3. **Cấu hình Mosquitto** (tùy chọn):
```bash
# Chỉnh sửa config
sudo nano /etc/mosquitto/mosquitto.conf

# Thêm các dòng:
listener 1883
allow_anonymous true
persistence true
persistence_location /var/lib/mosquitto/
```

### 📷 Cấu Hình ESP32-CAM

**IP mặc định cần thay đổi: `192.168.141.171`**

Chỉnh sửa trong các file:

1. **Backend - Camera Service**:
```python
# File: backend/app/services/camera_service.py
ESP32_CAMERA_URL = "http://192.168.141.171/capture"  # ← Thay IP ESP32-CAM
```

2. **AI Service**:
```python
# File: AI/api_pbl5/esp/app.py
ESP32_WEBCAM_URL = "http://192.168.141.171/capture?quality=10&resolution=UXGA"
```

3. **ESP32 Code**:
```cpp
// File: AI/api_pbl5/esp/temp.ino
IPAddress local_IP(192, 168, 141, 171);  // ← Thay IP tĩnh ESP32
IPAddress gateway(192, 168, 141, 1);     // ← Gateway router
IPAddress subnet(255, 255, 255, 0);
```

### 🌐 Cấu Hình Địa Chỉ IP Mạng

**Các IP cần cấu hình theo mạng của bạn:**

```bash
# Kiểm tra mạng hiện tại
ipconfig    # Windows
ifconfig    # macOS/Linux

# Ví dụ mạng: 192.168.1.x
Gateway: 192.168.1.1
Raspberry Pi: 192.168.1.100
ESP32-CAM: 192.168.1.101
Laptop: 192.168.1.102
```

## 🔨 Chạy Ứng Dụng

### 1. Khởi Động Backend

```bash
cd backend

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Chạy Flask server
python run.py

# Server sẽ chạy tại: http://localhost:5000
```

### 2. Khởi Động Frontend

```bash
# Mở terminal mới
cd frontend

# Chạy development server
npm run dev
# hoặc
pnpm dev

# Frontend sẽ chạy tại: http://localhost:3000
```

### 3. Khởi Động AI Service (Tùy chọn)

```bash
cd AI/api_pbl5/esp

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy AI service
python app.py

# AI service chạy tại: http://localhost:5000
```

## 🔍 Kiểm Tra Kết Nối

### Test MQTT Connection

```bash
# Trên máy tính, test publish
mosquitto_pub -h 192.168.141.250 -t test/topic -m "Hello MQTT"

# Test subscribe
mosquitto_sub -h 192.168.141.250 -t test/topic
```

### Test Camera Connection

```bash
# Kiểm tra ESP32-CAM
curl http://192.168.141.171/capture

# Hoặc mở trong browser
http://192.168.141.171
```

### Test Database Connection

```python
# Test script
from app import create_app
from app.models import db

app = create_app()
with app.app_context():
    try:
        db.create_all()
        print("✅ Database connected successfully!")
    except Exception as e:
        print(f"❌ Database error: {e}")
```

## 🐛 Troubleshooting

### Lỗi Thường Gặp

1. **Database Connection Error**:
   - Kiểm tra PostgreSQL có đang chạy
   - Xác nhận username/password trong config
   - Kiểm tra database name đã tồn tại

2. **MQTT Connection Failed**:
   - Ping IP Raspberry Pi: `ping 192.168.141.250`
   - Kiểm tra firewall
   - Xác nhận Mosquitto service đang chạy

3. **ESP32-CAM Not Responding**:
   - Kiểm tra nguồn điện ESP32
   - Ping IP camera: `ping 192.168.141.171`
   - Reset ESP32 và kiểm tra WiFi

4. **Frontend API Errors**:
   - Kiểm tra backend có đang chạy tại port 5000
   - Xem console logs trong browser
   - Kiểm tra CORS configuration

### Log Files

```bash
# Backend logs
tail -f backend/logs/app.log

# MQTT logs
tail -f backend/logs/mqtt.log

# Frontend logs (browser console)
F12 -> Console tab
```

## 📞 Hỗ Trợ

Nếu gặp khó khăn trong việc cài đặt:

1. Kiểm tra [Issues](https://github.com/your-repo/issues) trên GitHub
2. Đọc documentation chi tiết trong từng thư mục
3. Liên hệ team phát triển

---

**Chúc bạn cài đặt thành công! 🎉**
