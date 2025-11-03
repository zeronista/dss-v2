# 🐍 FastAPI Integration Guide - DSS System

## 📋 Tổng quan

Hệ thống DSS sử dụng **API Gateway Pattern** với Spring Boot làm gateway chính, kết nối tới các FastAPI services riêng biệt của từng thành viên.

## 🏗️ Kiến trúc

```
Spring Boot (Port 8080)
    │
    ├── FastAPI 1 - Inventory  (Port 8001)
    ├── FastAPI 2 - Marketing  (Port 8002)
    ├── FastAPI 3 - Sales      (Port 8003)
    └── FastAPI 4 - Analytics  (Port 8004)
```

## 🎯 Phân công ports

| Thành viên | Module | Port | Base URL |
|------------|--------|------|----------|
| Member 1 | Inventory | 8001 | http://localhost:8001 |
| Member 2 | Marketing | 8002 | http://localhost:8002 |
| Member 3 | Sales | 8003 | http://localhost:8003 |
| Member 4 | Analytics | 8004 | http://localhost:8004 |

## 📝 Yêu cầu cho mỗi FastAPI service

### 1. **CORS Configuration**

Mỗi FastAPI service phải enable CORS để Spring Boot có thể gọi:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Spring Boot URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. **Health Check Endpoint (REQUIRED)**

Mỗi service PHẢI có endpoint `/health` để gateway check status:

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "inventory"}
```

### 3. **Standard Response Format**

Để dễ xử lý, nên trả về format chuẩn:

```python
# Success response
{
    "success": True,
    "data": {...},
    "message": "Operation successful"
}

# Error response
{
    "success": False,
    "error": "Error message",
    "code": "ERROR_CODE"
}
```

## 🚀 Template FastAPI Service

### File: `main.py`

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="Inventory API",
    description="API for inventory management",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class PredictRequest(BaseModel):
    data: dict

class PredictResponse(BaseModel):
    success: bool
    prediction: dict
    message: str

# Health Check (REQUIRED)
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "inventory",
        "version": "1.0.0"
    }

# Example Prediction Endpoint
@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    try:
        # Your ML/AI logic here
        result = {"prediction": "sample result"}
        
        return {
            "success": True,
            "prediction": result,
            "message": "Prediction successful"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Example GET Endpoint
@app.get("/stats")
async def get_stats():
    return {
        "success": True,
        "data": {
            "total_items": 1000,
            "low_stock": 50
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

### File: `requirements.txt`

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.4.2
```

### Chạy service:

```bash
pip install -r requirements.txt
python main.py
```

## 🔌 Cách Spring Boot gọi FastAPI

### Từ Spring Boot Dashboard/Frontend:

```javascript
// Gọi Inventory API
fetch('/api/gateway/inventory/predict', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        data: { ... }
    })
})
.then(response => response.json())
.then(data => console.log(data));

// Gọi Marketing API
fetch('/api/gateway/marketing/recommend', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        customer_id: 123
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

## 📊 Testing

### 1. Test trực tiếp FastAPI:

```bash
# Test health
curl http://localhost:8001/health

# Test predict
curl -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -d '{"data": {"test": "value"}}'
```

### 2. Test qua Spring Boot Gateway:

```bash
# Login first to get session
# Then test via gateway
curl http://localhost:8080/api/gateway/health

curl -X POST http://localhost:8080/api/gateway/inventory/predict \
  -H "Content-Type: application/json" \
  -H "Cookie: JSESSIONID=your_session_id" \
  -d '{"data": {"test": "value"}}'
```

## 🛠️ Development Workflow

### 1. **Mỗi thành viên:**
   - Tạo FastAPI service riêng
   - Sử dụng port được phân công
   - Implement `/health` endpoint
   - Test locally

### 2. **Integration:**
   - Cập nhật `application.properties` nếu cần
   - Spring Boot tự động route request tới đúng service
   - Frontend gọi qua `/api/gateway/{module}/{endpoint}`

### 3. **Deployment:**
   - Mỗi FastAPI service có thể deploy riêng
   - Chỉ cần update URL trong `application.properties`
   - Không cần thay đổi code Spring Boot

## ⚠️ Common Issues & Solutions

### Issue 1: CORS Error
**Solution:** Đảm bảo đã add CORS middleware trong FastAPI

### Issue 2: Connection Refused
**Solution:** Kiểm tra FastAPI đang chạy đúng port

### Issue 3: 404 Not Found
**Solution:** Kiểm tra endpoint path trong FastAPI phải match với URL gọi

### Issue 4: Timeout
**Solution:** Tăng timeout trong `application.properties`

## 📞 API Gateway Endpoints

### Format:
```
POST /api/gateway/{module}/{endpoint}
GET  /api/gateway/{module}/{endpoint}
```

### Examples:

```bash
# Inventory
POST /api/gateway/inventory/predict
GET  /api/gateway/inventory/stats

# Marketing
POST /api/gateway/marketing/recommend
GET  /api/gateway/marketing/campaigns

# Sales
POST /api/gateway/sales/forecast
GET  /api/gateway/sales/targets

# Analytics
POST /api/gateway/analytics/analyze
GET  /api/gateway/analytics/reports
```

## 🔐 Security

- Tất cả requests qua gateway đều được authenticate
- Mỗi module chỉ được truy cập bởi role tương ứng
- FastAPI services nên ở private network (không expose ra internet)
- Chỉ Spring Boot gateway expose public

## 📝 Notes

1. **Port conflicts:** Đảm bảo mỗi người dùng port khác nhau
2. **Shared data:** Sử dụng MongoDB chung để share data
3. **Testing:** Luôn test `/health` endpoint trước
4. **Error handling:** Return proper HTTP status codes
5. **Documentation:** FastAPI tự động tạo docs tại `/docs`

## 🎓 Best Practices

1. ✅ Luôn implement `/health` endpoint
2. ✅ Sử dụng Pydantic models cho validation
3. ✅ Return consistent response format
4. ✅ Log errors properly
5. ✅ Handle exceptions gracefully
6. ✅ Test locally trước khi integrate
7. ✅ Document API endpoints trong code
8. ✅ Version your API nếu cần breaking changes

## 🆘 Support

Nếu gặp vấn đề khi integrate, check:
1. FastAPI service đang chạy chưa?
2. Port có đúng không?
3. CORS đã config chưa?
4. `/health` endpoint hoạt động chưa?
5. Spring Boot logs có error gì không?

