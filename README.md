# 🌱 GreenMind - Hệ Thống Nhà Kính Thông Minh

<div align="center">

![GreenMind Logo](https://via.placeholder.com/200x80/10B981/ffffff?text=GreenMind)

**Trí tuệ xanh cho nền nông nghiệp bền vững**

[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/your-repo/greenhouse)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Node.js](https://img.shields.io/badge/node.js-v18+-brightgreen.svg)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)](https://python.org/)
[![AI Powered](https://img.shields.io/badge/AI-Powered-ff6b6b.svg)](README_DISEASE_DETECTION.md)

</div>

---

## 📚 Mục Lục

- [🌱 Giới Thiệu](#-giới-thiệu)
- [🚀 Cài Đặt Nhanh](#-cài-đặt-nhanh)
- [📖 Tài Liệu Chi Tiết](#-tài-liệu-chi-tiết)
- [🎯 Tính Năng Chính](#-tính-năng-chính)
- [🏗️ Kiến Trúc Hệ Thống](#️-kiến-trúc-hệ-thống)
- [🔧 Cấu Hình IP](#-cấu-hình-ip)
- [🛠️ Công Nghệ Sử Dụng](#️-công-nghệ-sử-dụng)
- [📱 Demo Screenshots](#-demo-screenshots)
- [🤝 Đóng Góp](#-đóng-góp)
- [📞 Hỗ Trợ](#-hỗ-trợ)
- [📄 License](#-license)

---

## 🌱 Giới Thiệu

**GreenMind** là hệ thống quản lý nhà kính thông minh tiên tiến, tích hợp IoT, AI và machine learning để tự động hóa việc giám sát và điều khiển môi trường trồng trọt. Hệ thống mang đến nền nông nghiệp thông minh với khả năng phát hiện bệnh tật trên cây trồng và tối ưu hóa điều kiện môi trường tự động.

### 🎯 Mục Tiêu
- Tăng năng suất và chất lượng cây trồng
- Giảm thiểu chi phí vận hành
- Tự động hóa quy trình chăm sóc
- Phát hiện sớm bệnh tật và sâu hại
- Tối ưu hóa sử dụng tài nguyên

---

## 🚀 Cài Đặt Nhanh

### Yêu Cầu Hệ Thống
- **Node.js** v18+
- **Python** v3.8+
- **PostgreSQL** v13+
- **Git**

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/your-username/greenhouse.git
cd greenhouse

# 2. Setup Backend
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
python init_db.py

# 3. Setup Frontend
cd ../frontend
npm install
npm run dev

# 4. Start Backend
cd ../backend
python run.py
```

### Truy Cập Ứng Dụng
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Disease Detection**: http://localhost:3000/disease-detection

---

## 📖 Tài Liệu Chi Tiết

| Tài Liệu | Mô Tả | Link |
|----------|--------|------|
| 📋 **Hướng Dẫn Cài Đặt** | Chi tiết cài đặt và cấu hình IP | [README_INSTALLATION.md](README_INSTALLATION.md) |
| 🏠 **Giới Thiệu Ứng Dụng** | Tổng quan về hệ thống và lợi ích | [README_INTRODUCTION.md](README_INTRODUCTION.md) |
| 📊 **Dashboard** | Trang tổng quan và điều khiển | [README_DASHBOARD.md](README_DASHBOARD.md) |
| 📈 **Trực Quan Dữ Liệu** | Biểu đồ và phân tích xu hướng | [README_VISUALIZATION.md](README_VISUALIZATION.md) |
| 🧠 **Nhận Diện Sâu Bệnh** | AI phát hiện bệnh trên cây trồng | [README_DISEASE_DETECTION.md](README_DISEASE_DETECTION.md) |
| ⚙️ **Quản Lý Thông Tin** | Cấu hình hệ thống và thiết bị | [README_MANAGEMENT.md](README_MANAGEMENT.md) |

---

## 🎯 Tính Năng Chính

<table>
<tr>
<td width="50%">

### 📊 **Dashboard Thông Minh**
- Giám sát thời gian thực 24/7
- Biểu đồ gauge hiện đại
- Điều khiển thiết bị từ xa
- Cảnh báo tự động

### 📈 **Phân Tích Dữ Liệu**
- Biểu đồ xu hướng tương tác
- Thống kê theo khoảng thời gian
- Phát hiện bất thường
- Báo cáo chi tiết

</td>
<td width="50%">

### 🧠 **AI Nhận Diện Bệnh**
- YOLO v8 + ResNet architecture
- Độ chính xác 92%
- 5 loại bệnh phổ biến
- Khuyến nghị điều trị

### ⚙️ **Quản Lý Hệ Thống**
- Cấu hình thiết bị linh hoạt
- Alert rules thông minh
- Import/Export settings
- Multi-profile support

</td>
</tr>
</table>

---

## 🏗️ Kiến Trúc Hệ Thống

```
┌─────────────────────────────────────────────────────────────────┐
│                        WEB INTERFACE                            │
│                      (Next.js + React)                         │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP/REST API
┌─────────────────────▼───────────────────────────────────────────┐
│                    BACKEND SERVICES                            │
│                     (Flask + Python)                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│  │   API       │ │    MQTT     │ │   AI/ML     │ │ Database  │ │
│  │  Gateway    │ │   Client    │ │  Services   │ │  Manager  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │ MQTT Protocol
┌─────────────────────▼───────────────────────────────────────────┐
│                      IOT LAYER                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│  │ Raspberry   │ │   ESP32     │ │   Sensors   │ │  Devices  │ │
│  │     Pi      │ │   Camera    │ │   (DHT22)   │ │  Control  │ │
│  │ (MQTT Hub)  │ │             │ │             │ │           │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow
1. **Sensors** → Thu thập dữ liệu môi trường
2. **ESP32/RPi** → Xử lý và gửi qua MQTT
3. **Backend** → Nhận dữ liệu, xử lý AI, lưu database
4. **Frontend** → Hiển thị dashboard và điều khiển
5. **User** → Tương tác và ra lệnh điều khiển

---

## 🔧 Cấu Hình IP

### ⚠️ Các IP Cần Thay Đổi

| Component | Default IP | File Location | Mô Tả |
|-----------|------------|---------------|-------|
| **MQTT Broker** | `192.168.141.250` | `backend/app/config.py` | Raspberry Pi MQTT |
| **ESP32-CAM** | `192.168.141.171` | `backend/app/services/camera_service.py` | Camera module |
| **AI Service** | `192.168.141.250` | `AI/api_pbl5/esp/app.py` | AI processing |

### 🔍 Kiểm Tra Mạng Hiện Tại

```bash
# Windows
ipconfig

# Linux/macOS  
ifconfig

# Ví dụ mạng: 192.168.1.x
# Gateway: 192.168.1.1
# Cập nhật IP theo mạng của bạn
```

### 📝 Cách Cập Nhật IP

1. **Backend Config**:
```python
# backend/app/config.py
MQTT_BROKER = '192.168.1.100'  # ← IP Raspberry Pi của bạn
```

2. **ESP32-CAM**:
```python
# backend/app/services/camera_service.py
ESP32_CAMERA_URL = "http://192.168.1.101/capture"  # ← IP ESP32 của bạn
```

3. **ESP32 Code**:
```cpp
// AI/api_pbl5/esp/temp.ino
IPAddress local_IP(192, 168, 1, 101);  // ← IP tĩnh ESP32
```

---

## 🛠️ Công Nghệ Sử Dụng

<table>
<tr>
<td width="33%">

### Frontend
- **Next.js 14** - React Framework
- **TypeScript** - Type Safety
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **Chart.js** - Data Visualization
- **Lucide React** - Icons

</td>
<td width="33%">

### Backend
- **Flask** - Web Framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **Paho MQTT** - IoT Communication
- **Flask-CORS** - API Access

</td>
<td width="33%">

### AI & IoT
- **YOLO v8** - Object Detection
- **ResNet** - Image Classification
- **OpenCV** - Computer Vision
- **ESP32-CAM** - Camera Module
- **Raspberry Pi** - Edge Computing
- **DHT22** - Environmental Sensors

</td>
</tr>
</table>

---

## 📱 Demo Screenshots

<div align="center">

### Dashboard
![Dashboard](https://via.placeholder.com/800x400/10B981/ffffff?text=Dashboard+Screenshot)

### Disease Detection
![Disease Detection](https://via.placeholder.com/800x400/3B82F6/ffffff?text=AI+Disease+Detection)

### Data Visualization
![Data Visualization](https://via.placeholder.com/800x400/8B5CF6/ffffff?text=Data+Visualization)

### Management Panel
![Management](https://via.placeholder.com/800x400/F59E0B/ffffff?text=Management+Panel)

</div>

---

## 🚦 Trạng Thái Dự Án

| Component | Status | Version | Notes |
|-----------|--------|---------|-------|
| 🌐 **Frontend** | ✅ Stable | v1.0.0 | Production ready |
| 🖥️ **Backend** | ✅ Stable | v1.0.0 | Production ready |
| 🧠 **AI Service** | ✅ Complete | v1.0.0 | 92% accuracy |
| 📱 **IoT Integration** | ✅ Working | v1.0.0 | MQTT stable |
| 📊 **Database** | ✅ Optimized | v1.0.0 | PostgreSQL |
| 🔐 **Security** | 🚧 In Progress | v0.9.0 | Authentication WIP |
| 📱 **Mobile App** | 📋 Planned | v0.1.0 | Future release |

---

## 🔥 Quick Features

<div align="center">

| 🎯 **Real-time Monitoring** | 🤖 **AI-Powered Detection** | 📈 **Advanced Analytics** |
|:---:|:---:|:---:|
| Monitor your greenhouse 24/7 with live sensor data | Detect plant diseases with 92% accuracy | Visualize trends and optimize conditions |

| ⚙️ **Smart Automation** | 📱 **Remote Control** | 🚨 **Intelligent Alerts** |
|:---:|:---:|:---:|
| Automated device control based on AI recommendations | Control from anywhere via web interface | Get notified of critical conditions instantly |

</div>

---

## 🤝 Đóng Góp

Chúng tôi hoan nghênh mọi đóng góp! Vui lòng đọc [CONTRIBUTING.md](CONTRIBUTING.md) để biết thêm chi tiết.

### 👥 Team
- **Frontend**: Next.js, TypeScript, UI/UX
- **Backend**: Flask, PostgreSQL, API Design
- **AI/ML**: Computer Vision, Deep Learning
- **IoT**: Hardware Integration, MQTT

### 🌟 Contributing Guidelines
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📞 Hỗ Trợ

### 🆘 Getting Help
- 📖 **Documentation**: Đọc các README files chi tiết
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- 📧 **Email**: support@greenmind.com

### 🔧 Troubleshooting
| Problem | Solution |
|---------|----------|
| Database connection error | Check PostgreSQL service and credentials |
| MQTT connection failed | Verify Raspberry Pi IP and firewall |
| ESP32-CAM not responding | Check power supply and WiFi connection |
| AI model loading error | Ensure model files exist in correct path |

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Trường Đại học Duy Tân** - Academic support
- **PBL5 Team** - Development team
- **Open Source Community** - Libraries and frameworks
- **Agriculture Experts** - Domain knowledge

---

<div align="center">

### 🌱 GreenMind - Trí tuệ xanh cho nền nông nghiệp bền vững

**Made with ❤️ by PBL5 Team**

[⭐ Star this repo](https://github.com/your-repo/greenhouse) | [🐛 Report Bug](https://github.com/your-repo/issues) | [💡 Request Feature](https://github.com/your-repo/issues)

---

*© 2025 GreenMind. All rights reserved.*

</div>
