# 🚀 Quick Start Guide - Python APIs Integration

## Tóm Tắt Nhanh

Hệ thống DSS v2 sử dụng **Spring Boot** (Java) làm API Gateway và **4 Python FastAPI services** để xử lý analytics/AI/ML.

---

## 📦 Cài Đặt Nhanh (5 phút)

### 1. Cài Python Dependencies
```bash
cd python-apis
pip install -r requirements.txt
```

### 2. Chạy Tất Cả Python APIs
```bash
# Windows
cd python-apis
run_all.bat

# Hoặc chạy từng cái
python admin_api.py      # Port 8001
python inventory_api.py  # Port 8002
python marketing_api.py  # Port 8003
python sales_api.py      # Port 8004
```

### 3. Chạy Spring Boot
```bash
# Từ root directory
mvnw spring-boot:run
```

### 4. Kiểm Tra
- Spring Boot: http://localhost:8080
- Test Page: http://localhost:8080/api-test
- Health Check: http://localhost:8080/api/gateway/health

---

## 📊 4 Python APIs

| API | Port | Chức Năng | Endpoints Chính |
|-----|------|-----------|-----------------|
| **Admin** | 8001 | Sales Overview, KPIs | `/kpis`, `/monthly-trend`, `/top-countries` |
| **Inventory** | 8002 | Risk Management | `/calculate-risk-score`, `/simulate-policy` |
| **Marketing** | 8003 | Customer Segmentation | `/calculate-rfm`, `/run-segmentation` |
| **Sales** | 8004 | Product Recommendations | `/generate-recommendations`, `/top-bundles` |

---

## 🔌 Cách Gọi API từ Frontend

```javascript
// VD: Gọi Admin API - Get KPIs
fetch('/api/gateway/admin/kpis', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        exclude_cancelled: true,
        top_n: 10
    })
})
.then(response => response.json())
.then(data => {
    console.log('Total Revenue:', data.data.total_revenue);
    console.log('Total Transactions:', data.data.total_transactions);
});

// VD: Gọi Inventory API - Calculate Risk
fetch('/api/gateway/inventory/calculate-risk-score', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        customer_id: "17850",
        stock_code: "85123A",
        quantity: 10,
        unit_price: 2.55
    })
})
.then(response => response.json())
.then(data => {
    console.log('Risk Score:', data.data.risk_score);
    console.log('Risk Level:', data.data.risk_level);
});
```

---

## 🛠️ Files Đã Được Cập Nhật

### ✅ Configuration
- `src/main/resources/application.properties` - Cấu hình URLs cho 4 APIs

### ✅ Backend Java
- `ExternalApiService.java` - Service gọi Python APIs
- `ApiGatewayController.java` - Controller routing requests
- `TestController.java` - Controller cho test page

### ✅ Frontend
- `src/main/resources/templates/api-test.html` - Trang test APIs

### ✅ Scripts
- `python-apis/run_all.bat` - Script chạy tất cả Python APIs
- `test_integration.bat` - Script test tích hợp

### ✅ Documentation
- `INTEGRATION_STEPS.md` - Hướng dẫn chi tiết từng bước
- `QUICK_START.md` - Guide này

---

## 🔍 Test Nhanh

### Test 1: Health Check
```bash
curl http://localhost:8080/api/gateway/health
```
Kết quả:
```json
{
  "admin": true,
  "inventory": true,
  "marketing": true,
  "sales": true
}
```

### Test 2: Admin API
```bash
curl -X POST http://localhost:8080/api/gateway/admin/kpis ^
  -H "Content-Type: application/json" ^
  -d "{}"
```

### Test 3: Web Interface
Mở browser: http://localhost:8080/api-test

---

## ⚠️ Troubleshooting

### Lỗi: "Connection refused"
- ✅ Đảm bảo Python APIs đang chạy
- ✅ Check ports: 8001, 8002, 8003, 8004

### Lỗi: "ModuleNotFoundError"
```bash
pip install -r python-apis/requirements.txt
```

### Lỗi: "MongoDB connection failed"
- ✅ Kiểm tra internet connection
- ✅ MongoDB Atlas đã cho phép IP của bạn

### APIs chạy chậm
- ⏱️ Bình thường! Dataset có 530K+ transactions
- ⏱️ Timeout đã set 30 giây
- ⏱️ Lần đầu chạy sẽ lâu hơn

---

## 📚 Tài Liệu Đầy Đủ

- **Chi tiết tích hợp**: `INTEGRATION_STEPS.md`
- **Python APIs**: `python-apis/README.md`
- **Test Results**: `python-apis/TEST_RESULTS.md`
- **API Gateway**: `API_GATEWAY_SUMMARY.md`

---

## ✅ Checklist

- [ ] Python installed
- [ ] Packages installed (`pip install -r requirements.txt`)
- [ ] Python APIs running (4 terminals hoặc run_all.bat)
- [ ] Spring Boot running (`mvnw spring-boot:run`)
- [ ] Health check passed (http://localhost:8080/api/gateway/health)
- [ ] Test page working (http://localhost:8080/api-test)

---

## 🎯 Các Endpoint Hữu Ích

| URL | Mô Tả |
|-----|-------|
| http://localhost:8080 | Spring Boot Homepage |
| http://localhost:8080/login | Login page |
| http://localhost:8080/api-test | API Integration Test Page |
| http://localhost:8080/api/gateway/health | Health Check |
| http://localhost:8001/docs | Admin API Documentation |
| http://localhost:8002/docs | Inventory API Documentation |
| http://localhost:8003/docs | Marketing API Documentation |
| http://localhost:8004/docs | Sales API Documentation |

---

## 🚀 Next Steps

1. ✅ Tích hợp APIs vào dashboards có sẵn
2. ✅ Thêm charts/visualizations
3. ✅ Implement caching cho performance
4. ✅ Deploy to production (Docker/Cloud)

Chúc bạn code vui vẻ! 💻✨
