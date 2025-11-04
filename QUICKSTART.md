# 🚀 DSS-v2 - Quick Start Guide

Decision Support System với Spring Boot + Python FastAPI

## ⚡ CÁCH CHẠY NHANH NHẤT (3 BƯỚC)

### 1. Cài Java 17 (nếu chưa có)
```bash
sudo apt update
sudo apt install -y openjdk-17-jdk
java -version  # Verify: phải là version 17
```

### 2. Start Application
```bash
cd /home/ubuntu/DataScience/MyProject/dss-v2
./start.sh
```

**Đợi khoảng 30-60 giây để Spring Boot khởi động.**

### 3. Access Application
Mở browser: **http://localhost:8080**

**Login:**
- Username: `sales`
- Password: `sales123`

---

## 🎯 CÁC TÍNH NĂNG (Sales Manager Dashboard)

Sau khi login, bạn có thể truy cập:

### Main Dashboard
📊 **http://localhost:8080/sales/dashboard**

**7 Features:**
1. ✅ **Product Recommendations** - AI recommendations sử dụng Association Rules
2. ✅ **Cross-sell Insights** - Strategic insights để tăng AOV
3. ✅ **Top Product Bundles** - Frequently bought together analysis
4. ✅ **View Invoices** - Xem danh sách hóa đơn
5. ✅ **Active Deals** - Quản lý deals pipeline (`/sales/deals`)
6. ✅ **Lead Pipeline** - Lead scoring & management (`/sales/leads`)
7. ✅ **Sales Reports** - Analytics & reporting (`/sales/reports`)

---

## 🛑 Dừng Application

```bash
cd /home/ubuntu/DataScience/MyProject/dss-v2
./stop.sh
```

---

## 🧪 Test API Endpoints

```bash
cd /home/ubuntu/DataScience/MyProject/dss-v2

# Test Python API
./test_quick_actions.sh

# Hoặc test thủ công
curl http://localhost:8004/health
curl http://localhost:8004/deals | jq .
curl http://localhost:8004/leads | jq .
curl http://localhost:8004/reports | jq .
```

---

## 📁 Project Structure

```
dss-v2/
├── start.sh                    # ⭐ START APPLICATION
├── stop.sh                     # ⭐ STOP APPLICATION  
├── test_quick_actions.sh       # Test API endpoints
├── SETUP_GUIDE.md              # Chi tiết setup guide
├── QUICK_ACTIONS_IMPLEMENTATION.md  # Documentation
│
├── src/main/                   # Java Spring Boot source
│   ├── java/com/group5/dss/
│   └── resources/
│       ├── application.properties
│       └── templates/          # HTML templates
│           ├── login.html
│           └── dashboard/
│               ├── sales.html      # Main dashboard
│               ├── deals.html      # Active Deals
│               ├── leads.html      # Lead Pipeline
│               └── reports.html    # Sales Reports
│
├── python-apis/                # Python FastAPI
│   ├── sales_manager_api.py    # Sales Manager API (port 8004)
│   ├── requirements.txt
│   └── data/
│       └── data.csv            # Transaction data (541K rows)
│
├── pom.xml                     # Maven config
└── mvnw                        # Maven Wrapper
```

---

## 🔧 Troubleshooting

### Port đã được sử dụng?
```bash
# Kill process trên port 8004
kill -9 $(lsof -ti:8004)

# Kill process trên port 8080
kill -9 $(lsof -ti:8080)

# Hoặc dùng stop script
./stop.sh
```

### Spring Boot không start?
```bash
# Kiểm tra Java version
java -version  # Phải là 17

# Nếu không phải, chọn Java 17
sudo update-alternatives --config java

# Rebuild
./mvnw clean package -DskipTests
```

### Python API lỗi?
```bash
cd python-apis

# Xem logs
tail -f sales_manager.log

# Cài lại dependencies
pip install -r requirements.txt
```

---

## 👥 User Accounts

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | ADMIN |
| sales | sales123 | SALES_MANAGER |
| inventory | inventory123 | INVENTORY_MANAGER |
| marketing | marketing123 | MARKETING_MANAGER |

---

## 🌐 URLs Reference

| Service | URL | Description |
|---------|-----|-------------|
| Login | http://localhost:8080/login | Login page |
| Sales Dashboard | http://localhost:8080/sales/dashboard | Main dashboard |
| Active Deals | http://localhost:8080/sales/deals | Deals management |
| Lead Pipeline | http://localhost:8080/sales/leads | Lead scoring |
| Sales Reports | http://localhost:8080/sales/reports | Analytics |
| Python API Docs | http://localhost:8004/docs | FastAPI Swagger docs |
| API Health | http://localhost:8004/health | Health check |

---

## 📊 Tech Stack

**Backend:**
- ☕ Java 17 + Spring Boot 3.5.7
- 🔐 Spring Security
- 💾 H2 Database (in-memory)
- 🎨 Thymeleaf

**Python API:**
- 🐍 Python 3.x
- ⚡ FastAPI 0.115.5
- 🤖 ML: MLxtend (Apriori algorithm)
- 📊 Pandas + NumPy

---

## 📝 Documentation

- **SETUP_GUIDE.md** - Chi tiết hướng dẫn setup từ đầu
- **QUICK_ACTIONS_IMPLEMENTATION.md** - Chi tiết implementation của 3 Quick Actions
- **SALES_DASHBOARD_API_COMPATIBILITY.md** - Compatibility report
- **SALES_HTML_FUNCTIONALITY_TEST.md** - Test report cho sales.html

---

## 🎯 Quick Commands

```bash
# Start everything
./start.sh

# Stop everything
./stop.sh

# Test APIs
./test_quick_actions.sh

# Rebuild Java
./mvnw clean package -DskipTests

# Run Spring Boot only
./mvnw spring-boot:run

# Run Python API only
cd python-apis && python3 sales_manager_api.py

# Check Java version
java -version

# Check running services
lsof -i:8004  # Python API
lsof -i:8080  # Spring Boot
```

---

## ✅ Checklist Setup

- [ ] Java 17 installed: `java -version`
- [ ] Project built: `./mvnw clean package -DskipTests`
- [ ] Python deps installed: `pip install -r python-apis/requirements.txt`
- [ ] Start app: `./start.sh`
- [ ] Access: http://localhost:8080
- [ ] Login: sales/sales123
- [ ] Test all 7 features

---

**Happy Coding! 🚀**

*For detailed setup instructions, see `SETUP_GUIDE.md`*
