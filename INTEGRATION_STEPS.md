# 🔗 Hướng Dẫn Tích Hợp Python APIs vào Java Project

## 📋 Tổng Quan

Dự án DSS sử dụng kiến trúc **API Gateway** với:
- **Spring Boot** (Port 8080) - API Gateway & Frontend
- **4 Python FastAPI Services** - Backend xử lý AI/ML/Analytics

---

## 🏗️ Kiến Trúc Hệ Thống

```
┌─────────────────────────────────────────────────────┐
│         Spring Boot Gateway (Port 8080)              │
│  - Authentication & Authorization                    │
│  - API Gateway Controller                            │
│  - Thymeleaf Templates                               │
└─────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┬──────────┐
        │                 │                 │          │
        ▼                 ▼                 ▼          ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Admin API   │  │ Inventory API│  │ Marketing API│  │  Sales API   │
│  Port 8001   │  │  Port 8002   │  │  Port 8003   │  │  Port 8004   │
│ Descriptive  │  │ Prescriptive │  │ Prescriptive │  │  Predictive  │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
        │                 │                 │          │
        └─────────────────┴─────────────────┴──────────┘
                          │
                          ▼
                  ┌──────────────┐
                  │   MongoDB    │
                  │    Atlas     │
                  └──────────────┘
```

---

## 🚀 Các Bước Tích Hợp

### **Bước 1: Cài Đặt Python Dependencies**

```bash
# Di chuyển vào thư mục python-apis
cd python-apis

# Cài đặt các thư viện cần thiết
pip install -r requirements.txt
```

**Kiểm tra cài đặt**:
```bash
python -c "import fastapi, uvicorn, pandas, sklearn; print('✅ All packages installed!')"
```

---

### **Bước 2: Kiểm Tra Kết Nối MongoDB**

```bash
cd python-apis
python db_utils.py
```

**Output mong đợi**:
```
✅ MongoDB connection successful!
📦 Available collections: ['DSS', 'customer_rfm', ...]
📊 Sample transaction count: 530000+
```

---

### **Bước 3: Chạy Python APIs**

#### **Option 1: Chạy từng API riêng lẻ**

```bash
# Terminal 1 - Admin API
cd python-apis
python admin_api.py

# Terminal 2 - Inventory API
cd python-apis
python inventory_api.py

# Terminal 3 - Marketing API
cd python-apis
python marketing_api.py

# Terminal 4 - Sales API
cd python-apis
python sales_api.py
```

#### **Option 2: Chạy tất cả cùng lúc (Windows)**

```bash
cd python-apis
run_all.bat
```

#### **Kiểm tra APIs đã chạy**:

Mở browser và truy cập:
- Admin API: http://localhost:8001/docs
- Inventory API: http://localhost:8002/docs
- Marketing API: http://localhost:8003/docs
- Sales API: http://localhost:8004/docs

---

### **Bước 4: Chạy Spring Boot Application**

```bash
# Từ thư mục root của project
./mvnw spring-boot:run

# Hoặc nếu dùng Maven đã cài
mvn spring-boot:run
```

**Kiểm tra Spring Boot**:
- Application: http://localhost:8080
- Health Check: http://localhost:8080/api/gateway/health

---

### **Bước 5: Test Tích Hợp**

#### **Test 1: Health Check tất cả APIs**

```bash
curl http://localhost:8080/api/gateway/health
```

**Response mong đợi**:
```json
{
  "admin": true,
  "inventory": true,
  "marketing": true,
  "sales": true
}
```

#### **Test 2: Gọi Admin API qua Gateway**

```bash
curl -X POST http://localhost:8080/api/gateway/admin/kpis \
  -H "Content-Type: application/json" \
  -d '{}'
```

#### **Test 3: Gọi Inventory API**

```bash
curl -X POST http://localhost:8080/api/gateway/inventory/calculate-risk-score \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "12345",
    "stock_code": "85123A",
    "quantity": 10,
    "unit_price": 2.55,
    "country": "United Kingdom"
  }'
```

---

## 📊 Cách Sử Dụng trong Frontend

### **JavaScript/jQuery Example**

```javascript
// 1. Gọi Admin API - Get KPIs
function loadKPIs() {
    fetch('/api/gateway/admin/kpis', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            exclude_cancelled: true,
            top_n: 10
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const kpis = data.data;
            document.getElementById('totalRevenue').textContent = 
                '$' + kpis.total_revenue.toLocaleString();
            document.getElementById('totalTransactions').textContent = 
                kpis.total_transactions.toLocaleString();
        }
    })
    .catch(error => console.error('Error:', error));
}

// 2. Gọi Inventory API - Calculate Risk Score
function calculateRisk(customerId, stockCode, quantity, unitPrice) {
    fetch('/api/gateway/inventory/calculate-risk-score', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            customer_id: customerId,
            stock_code: stockCode,
            quantity: quantity,
            unit_price: unitPrice,
            country: "United Kingdom"
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const riskInfo = data.data;
            alert(`Risk Score: ${riskInfo.risk_score}\nLevel: ${riskInfo.risk_level}`);
        }
    });
}

// 3. Gọi Marketing API - RFM Segmentation
function runSegmentation() {
    fetch('/api/gateway/marketing/run-segmentation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            n_segments: 3,
            use_existing_rfm: true
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displaySegments(data.data.segments);
        }
    });
}

// 4. Gọi Sales API - Product Recommendations
function getRecommendations(stockCode) {
    fetch('/api/gateway/sales/generate-recommendations', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            stock_code: stockCode,
            confidence_threshold: 0.3,
            top_n: 5,
            min_support: 0.01
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayRecommendations(data.data.recommendations);
        }
    });
}
```

---

## 🔒 Security & Authorization

Các endpoint đã được bảo vệ bởi Spring Security:

| Endpoint | Vai Trò Truy Cập |
|----------|------------------|
| `/api/gateway/admin/*` | ADMIN |
| `/api/gateway/inventory/*` | ADMIN, INVENTORY_MANAGER |
| `/api/gateway/marketing/*` | ADMIN, MARKETING_MANAGER |
| `/api/gateway/sales/*` | ADMIN, SALES_MANAGER |

**Login để test**:
- URL: http://localhost:8080/login
- Accounts được tạo sẵn trong `DataInitializer.java`

---

## 🛠️ Troubleshooting

### **1. Python API không chạy được**

**Lỗi**: `ModuleNotFoundError: No module named 'fastapi'`

**Giải pháp**:
```bash
pip install -r python-apis/requirements.txt
```

---

### **2. MongoDB connection failed**

**Lỗi**: `ServerSelectionTimeoutError`

**Giải pháp**:
- Kiểm tra internet connection
- Kiểm tra MongoDB URI trong `db_utils.py`
- Kiểm tra MongoDB Atlas có cho phép IP của bạn

---

### **3. CORS Error**

**Lỗi**: `Access to fetch at ... has been blocked by CORS policy`

**Giải pháp**: 
- Kiểm tra CORS middleware trong Python APIs
- Đảm bảo `allow_origins` có `http://localhost:8080`

---

### **4. Python API chậm**

**Nguyên nhân**: Dataset lớn (530K+ transactions)

**Giải pháp**:
- Tăng timeout trong `application.properties` (đã set 30000ms)
- Tối ưu query MongoDB
- Cache kết quả nếu cần

---

### **5. Port đã được sử dụng**

**Lỗi**: `Address already in use: 8001`

**Giải pháp**:
```bash
# Windows - Kill process trên port
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# Hoặc đổi port trong Python file
uvicorn.run(app, host="0.0.0.0", port=8005)  # Đổi port
```

---

## 📈 Performance Tips

1. **Giới hạn dữ liệu**: Sử dụng filters để giảm số lượng transactions xử lý
2. **Pagination**: Implement pagination cho results lớn
3. **Caching**: Cache kết quả RFM, segmentation
4. **Async Processing**: Sử dụng async/await trong Python
5. **Database Indexing**: Tạo index cho MongoDB collections

---

## 📚 Tài Liệu Tham Khảo

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Python APIs README**: `python-apis/README.md`
- **API Test Results**: `python-apis/TEST_RESULTS.md`
- **Integration Guide**: `FASTAPI_INTEGRATION_GUIDE.md`

---

## ✅ Checklist Hoàn Thành

- [ ] Cài đặt Python dependencies
- [ ] Kiểm tra MongoDB connection
- [ ] Chạy được 4 Python APIs
- [ ] Chạy được Spring Boot
- [ ] Health check thành công
- [ ] Test được ít nhất 1 endpoint của mỗi API
- [ ] Frontend có thể gọi được APIs qua gateway

---

## 🎯 Next Steps

1. **Tạo Dashboard UI** - Hiển thị KPIs, charts từ Admin API
2. **Risk Management UI** - Interface cho Inventory Manager
3. **Customer Segmentation UI** - Hiển thị RFM segments
4. **Recommendation Engine UI** - Show product recommendations
5. **Deploy to Production** - Docker, Kubernetes, Cloud

Chúc bạn tích hợp thành công! 🚀
