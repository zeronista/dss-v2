# DSS-v2 Setup Guide - Từ Đầu (Clean Install)
*Hướng dẫn cài đặt đầy đủ cho Ubuntu/Linux*

## 📋 Yêu Cầu Hệ Thống

- **Java**: 17 (hiện tại bạn có Java 11)
- **Maven**: Không cần cài (dùng Maven Wrapper có sẵn)
- **Python**: 3.x (đã có)
- **Port**: 8004 (Python API), 8080 (Spring Boot)

---

## 🚀 HƯỚNG DẪN SETUP NHANH (RECOMMENDED)

### Bước 1: Cài Java 17

```bash
# Update package list
sudo apt update

# Cài OpenJDK 17
sudo apt install -y openjdk-17-jdk openjdk-17-jre

# Kiểm tra version
java -version
# Kết quả mong đợi: openjdk version "17.x.x"
```

#### Nếu có nhiều Java version, chọn Java 17:
```bash
# Xem danh sách các Java đã cài
sudo update-alternatives --config java

# Chọn số tương ứng với Java 17
# Ví dụ: nhấn 2 nếu Java 17 là option số 2
```

#### Set JAVA_HOME (optional nhưng recommended):
```bash
# Thêm vào ~/.bashrc
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> ~/.bashrc
echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.bashrc

# Reload
source ~/.bashrc

# Verify
echo $JAVA_HOME
```

---

### Bước 2: Setup Python API Dependencies

```bash
cd /home/ubuntu/DataScience/MyProject/dss-v2/python-apis

# Cài các package cần thiết (nếu chưa có)
pip install fastapi uvicorn pandas numpy mlxtend python-multipart

# Hoặc dùng requirements.txt
pip install -r requirements.txt
```

---

### Bước 3: Start Python API (Sales Manager)

```bash
cd /home/ubuntu/DataScience/MyProject/dss-v2/python-apis

# Start trong background
nohup python3 sales_manager_api.py > sales_manager.log 2>&1 &

# Kiểm tra status
curl http://localhost:8004/health

# Xem log nếu có lỗi
tail -f sales_manager.log
```

**Kết quả mong đợi**:
```json
{
  "status": "healthy",
  "service": "sales_manager",
  "version": "2.0.0",
  "port": 8004,
  "data_source": "CSV",
  "total_transactions": 50000
}
```

---

### Bước 4: Build Java Project

```bash
cd /home/ubuntu/DataScience/MyProject/dss-v2

# Cấp quyền execute cho Maven Wrapper
chmod +x mvnw

# Build project (bỏ qua tests)
./mvnw clean package -DskipTests

# Nếu build thành công, bạn sẽ thấy:
# [INFO] BUILD SUCCESS
```

**Nếu gặp lỗi "release version 17 not supported"**:
- Kiểm tra lại Java version: `java -version` phải là 17
- Set JAVA_HOME đúng đường dẫn Java 17

---

### Bước 5: Start Spring Boot Application

```bash
cd /home/ubuntu/DataScience/MyProject/dss-v2

# Option 1: Chạy trực tiếp bằng Maven
./mvnw spring-boot:run

# Option 2: Chạy từ JAR file đã build
java -jar target/dss-0.0.1-SNAPSHOT.jar

# Option 3: Chạy trong background
nohup ./mvnw spring-boot:run > app.log 2>&1 &
```

**Kết quả mong đợi**:
```
Started DssApplication in X.XXX seconds
Tomcat started on port 8080
```

---

### Bước 6: Access Application

1. **Mở browser**: `http://localhost:8080`

2. **Login credentials** (check file DataInitializer.java):
   - **Admin**: username: `admin`, password: `admin123`
   - **Sales Manager**: username: `sales`, password: `sales123`
   - **Inventory Manager**: username: `inventory`, password: `inventory123`
   - **Marketing Manager**: username: `marketing`, password: `marketing123`

3. **Sales Dashboard URLs**:
   - Main Dashboard: `http://localhost:8080/sales/dashboard`
   - Active Deals: `http://localhost:8080/sales/deals`
   - Lead Pipeline: `http://localhost:8080/sales/leads`
   - Sales Reports: `http://localhost:8080/sales/reports`

---

## 🔧 TROUBLESHOOTING

### Lỗi 1: Port 8004 đã được sử dụng

```bash
# Tìm process đang dùng port 8004
lsof -ti:8004

# Kill process
kill -9 $(lsof -ti:8004)

# Start lại Python API
cd /home/ubuntu/DataScience/MyProject/dss-v2/python-apis
python3 sales_manager_api.py
```

### Lỗi 2: Port 8080 đã được sử dụng

```bash
# Tìm process đang dùng port 8080
lsof -ti:8080

# Kill process
kill -9 $(lsof -ti:8080)

# Start lại Spring Boot
cd /home/ubuntu/DataScience/MyProject/dss-v2
./mvnw spring-boot:run
```

### Lỗi 3: Java version không đúng

```bash
# Kiểm tra Java version
java -version

# Nếu không phải Java 17, chuyển đổi:
sudo update-alternatives --config java
# Chọn Java 17

# Hoặc cài Java 17:
sudo apt install -y openjdk-17-jdk
```

### Lỗi 4: Maven build failed

```bash
# Clean cache và rebuild
./mvnw clean
./mvnw package -DskipTests -X  # -X for debug output

# Nếu vẫn lỗi, kiểm tra JAVA_HOME
echo $JAVA_HOME
# Phải trỏ tới Java 17
```

### Lỗi 5: Python dependencies thiếu

```bash
cd /home/ubuntu/DataScience/MyProject/dss-v2/python-apis

# Cài lại tất cả dependencies
pip install fastapi==0.115.5 uvicorn==0.34.0 pandas==2.2.3 numpy==2.1.3 mlxtend==0.23.0 python-multipart

# Hoặc
pip install -r requirements.txt --upgrade
```

### Lỗi 6: Database connection error

**Lưu ý**: Project này dùng **H2 in-memory database**, không cần cài database riêng.
- Database tự động khởi tạo khi start Spring Boot
- Data được load từ `DataInitializer.java`

---

## 📊 KIỂM TRA HỆ THỐNG

### Script kiểm tra tự động:

```bash
cd /home/ubuntu/DataScience/MyProject/dss-v2

# Chạy test script
./test_quick_actions.sh
```

**Kết quả mong đợi**:
```
✅ /deals - 20 deals, $262K pipeline
✅ /leads - 30 leads, avg score 7.3
✅ /reports - $1M revenue, 58% growth
```

---

## 🎯 QUICK START COMMANDS (Copy & Paste)

### Terminal 1: Python API
```bash
cd /home/ubuntu/DataScience/MyProject/dss-v2/python-apis
python3 sales_manager_api.py
```

### Terminal 2: Spring Boot App
```bash
cd /home/ubuntu/DataScience/MyProject/dss-v2
./mvnw spring-boot:run
```

### Terminal 3: Test
```bash
# Test Python API
curl http://localhost:8004/health

# Test Spring Boot (sau khi start)
curl http://localhost:8080

# Test full system
cd /home/ubuntu/DataScience/MyProject/dss-v2
./test_quick_actions.sh
```

---

## 📦 DEPENDENCIES SUMMARY

### Java Dependencies (pom.xml):
- Spring Boot 3.5.7
- Spring Security
- Spring Data JPA
- H2 Database (in-memory)
- Thymeleaf
- Lombok

### Python Dependencies (requirements.txt):
- FastAPI 0.115.5
- Uvicorn 0.34.0
- Pandas 2.2.3
- NumPy 2.1.3
- MLxtend 0.23.0
- Python Multipart

---

## 🔐 DEFAULT USERS

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | ADMIN |
| sales | sales123 | SALES_MANAGER |
| inventory | inventory123 | INVENTORY_MANAGER |
| marketing | marketing123 | MARKETING_MANAGER |

---

## 📁 PROJECT STRUCTURE

```
dss-v2/
├── src/
│   ├── main/
│   │   ├── java/com/group5/dss/
│   │   │   ├── DssApplication.java          # Main Spring Boot app
│   │   │   ├── controller/
│   │   │   │   ├── AuthController.java      # Routes for dashboards
│   │   │   │   ├── InvoiceController.java
│   │   │   │   └── ApiGatewayController.java
│   │   │   ├── model/
│   │   │   ├── repository/
│   │   │   ├── service/
│   │   │   └── config/
│   │   └── resources/
│   │       ├── application.properties       # Config file
│   │       └── templates/
│   │           ├── login.html
│   │           └── dashboard/
│   │               ├── sales.html           # Main Sales Dashboard
│   │               ├── deals.html           # Active Deals
│   │               ├── leads.html           # Lead Pipeline
│   │               └── reports.html         # Sales Reports
│   └── test/
├── python-apis/
│   ├── sales_manager_api.py                 # Sales Manager API (port 8004)
│   ├── requirements.txt
│   └── data/
│       └── data.csv                         # Transaction data
├── pom.xml                                  # Maven config
├── mvnw                                     # Maven Wrapper (Linux)
├── mvnw.cmd                                 # Maven Wrapper (Windows)
└── test_quick_actions.sh                   # Test script
```

---

## 🚀 PRODUCTION DEPLOYMENT

### Option 1: JAR file deployment
```bash
# Build JAR
./mvnw clean package -DskipTests

# Run JAR
java -jar target/dss-0.0.1-SNAPSHOT.jar
```

### Option 2: Docker (nếu muốn)
```bash
# Build Docker image
docker build -t dss-app .

# Run container
docker run -p 8080:8080 -p 8004:8004 dss-app
```

---

## 📝 NOTES

1. **Python API** phải chạy trước Spring Boot (để endpoints /deals, /leads, /reports hoạt động)
2. **H2 Database** là in-memory, data sẽ mất khi restart app
3. **Data CSV** có 541K rows, optimized xuống 50K để tránh OOM
4. **Port conflicts**: Đảm bảo ports 8004 và 8080 free
5. **Java 17** là bắt buộc (Spring Boot 3.5.7 yêu cầu Java 17+)

---

## ✅ CHECKLIST SETUP

- [ ] Cài Java 17
- [ ] Verify Java version: `java -version`
- [ ] Set JAVA_HOME (optional)
- [ ] Cài Python dependencies: `pip install -r python-apis/requirements.txt`
- [ ] Start Python API: `python3 python-apis/sales_manager_api.py`
- [ ] Test API: `curl http://localhost:8004/health`
- [ ] Build Java project: `./mvnw clean package -DskipTests`
- [ ] Start Spring Boot: `./mvnw spring-boot:run`
- [ ] Access browser: `http://localhost:8080`
- [ ] Login as sales/sales123
- [ ] Test all 7 features

---

## 🆘 SUPPORT

Nếu gặp vấn đề:

1. Xem logs:
   ```bash
   # Python API logs
   tail -f python-apis/sales_manager.log
   
   # Spring Boot logs
   tail -f app.log  # nếu chạy background
   # hoặc xem trực tiếp trên console
   ```

2. Kiểm tra ports:
   ```bash
   lsof -i:8004  # Python API
   lsof -i:8080  # Spring Boot
   ```

3. Verify Java:
   ```bash
   java -version
   echo $JAVA_HOME
   ```

---

*Happy Coding! 🚀*
