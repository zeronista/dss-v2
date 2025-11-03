# 🔗 Hướng Dẫn Tích Hợp Python APIs với Dashboard UI

## 📋 Tổng Quan

Dự án DSS đã được cập nhật để tích hợp hoàn toàn giữa:
- **Python APIs** (FastAPI) - Xử lý thuật toán & phân tích dữ liệu
- **Dashboard UI** (HTML/JavaScript) - Giao diện người dùng theo role

### Kiến Trúc Hệ Thống

```
┌─────────────────┐
│   MongoDB       │ ← Dữ liệu giao dịch
│   (Cloud)       │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│        Python FastAPI Services              │
├─────────────────────────────────────────────┤
│ • Admin API     (Port 8001) - Analytics     │
│ • Inventory API (Port 8002) - Risk Mgmt     │
│ • Marketing API (Port 8003) - Segmentation  │
│ • Sales API     (Port 8004) - Cross-sell    │
└────────┬────────────────────────────────────┘
         │ REST API (JSON)
         ▼
┌─────────────────────────────────────────────┐
│        Dashboard HTML Pages                 │
├─────────────────────────────────────────────┤
│ • admin.html     - Sales Overview           │
│ • inventory.html - Policy Simulator         │
│ • marketing.html - Customer Segments        │
│ • sales.html     - Product Recommendations  │
└─────────────────────────────────────────────┘
```

## 🚀 Bước 1: Khởi Động Python APIs

### Cài Đặt Dependencies

```bash
cd python-apis
pip install -r requirements.txt
```

### Chạy Tất Cả APIs

**Linux/Mac:**
```bash
chmod +x run_all.sh
./run_all.sh
```

**Windows:**
```batch
run_all.bat
```

**Hoặc chạy từng API riêng:**
```bash
python admin_api.py      # Port 8001
python inventory_api.py  # Port 8002
python marketing_api.py  # Port 8003
python sales_api.py      # Port 8004
```

### Kiểm Tra APIs Đang Chạy

```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
```

Hoặc dùng test script:
```bash
python test_apis.py
```

## 🎨 Bước 2: Truy Cập Dashboard UI

### Khởi Động Spring Boot Application (Optional)

Nếu muốn dùng authentication của Java backend:

```bash
./mvnw spring-boot:run
```

Hoặc mở trực tiếp các file HTML trong browser (không cần Java backend):

```
file:///path/to/dss-v2/src/main/resources/templates/dashboard/admin.html
file:///path/to/dss-v2/src/main/resources/templates/dashboard/inventory.html
file:///path/to/dss-v2/src/main/resources/templates/dashboard/marketing.html
file:///path/to/dss-v2/src/main/resources/templates/dashboard/sales.html
```

## 📊 Chi Tiết Tích Hợp Từng Dashboard

### 1. Admin Dashboard (admin.html)

**Kết nối:** Admin API - Port 8001

**Chức năng:**
- ✅ **KPI Cards**: Total Revenue, Transactions, Active Countries, Top-N Share
- ✅ **Monthly Trend Chart**: Revenue theo tháng với MoM growth (Chart.js)
- ✅ **Top Countries Table**: Ranking 10 quốc gia theo doanh thu
- ✅ **Top Products Table**: Ranking 10 sản phẩm theo doanh thu

**API Endpoints Sử Dụng:**
```javascript
POST /kpis
POST /monthly-trend
POST /top-countries
POST /top-products
```

**Cách Hoạt Động:**
1. Trang load → Tự động gọi 4 endpoints
2. Hiển thị KPIs realtime từ MongoDB
3. Vẽ biểu đồ xu hướng với Chart.js
4. Fill bảng xếp hạng

**Test:**
```bash
# Mở admin.html trong browser
# Kiểm tra Console log (F12) để xem API calls
# Data sẽ tự động load từ MongoDB
```

---

### 2. Inventory Dashboard (inventory.html)

**Kết nối:** Inventory API - Port 8002

**Chức năng:**
- ✅ **Risk Distribution**: Phân bố điểm rủi ro của đơn hàng
- ✅ **Optimal Threshold**: Tìm threshold τ* tối ưu
- ✅ **Policy Simulator**: Interactive sliders để test chính sách
  - Risk Threshold (τ): 0-100
  - Return Processing Cost: $5-$50
  - Conversion Impact: 0-100%
- ✅ **Simulation Results**: Expected Profit, Orders Blocked/Allowed

**API Endpoints Sử Dụng:**
```javascript
GET /risk-distribution
POST /find-optimal-threshold
POST /simulate-policy
```

**Cách Hoạt Động:**
1. Trang load → Tự động load risk distribution & optimal τ
2. User kéo sliders → Adjust parameters
3. Click "Run Simulation" → POST request với parameters
4. Hiển thị kết quả: Profit, Orders, Recommendation

**Test:**
```bash
# Mở inventory.html
# Kéo slider τ = 50
# Click "Run Simulation"
# Xem Expected Profit thay đổi
```

---

### 3. Marketing Dashboard (marketing.html)

**Kết nối:** Marketing API - Port 8003

**Chức năng:**
- ✅ **RFM Calculation**: Tính Recency, Frequency, Monetary cho customers
- ✅ **Customer Segmentation**: K-Means clustering (3-5 segments)
- ✅ **Segment Cards**: Hiển thị mỗi segment với:
  - Customer count
  - Total value
  - RFM metrics
  - Recommended marketing actions
- ✅ **Market Basket Analysis**: Apriori algorithm
- ✅ **Product Bundles Table**: Frequently bought together

**API Endpoints Sử Dụng:**
```javascript
POST /calculate-rfm
POST /run-segmentation
POST /product-bundles
```

**Cách Hoạt Động:**
1. Trang load → Calculate RFM scores
2. User chọn số segments (3-5) → Click "Run Segmentation"
3. K-Means clustering → Hiển thị segment cards
4. Click "Find Product Bundles" → Apriori algorithm
5. Show bundles với Support, Confidence, Lift

**Test:**
```bash
# Mở marketing.html
# Chọn "4 Segments"
# Click "Run Segmentation"
# Xem Champions, Loyal, At-Risk segments
# Click "Find Product Bundles"
```

---

### 4. Sales Dashboard (sales.html)

**Kết nối:** Sales API - Port 8004

**Chức năng:**
- ✅ **Product Recommendations**: Nhập StockCode → Gợi ý sản phẩm bán kèm
- ✅ **Recommendation Cards**: Hiển thị với Confidence, Lift, Support, Impact
- ✅ **Cross-sell Insights**: Bundle opportunity, Timing strategy, AOV increase
- ✅ **Top Bundles Table**: 10 bundles phổ biến nhất

**API Endpoints Sử Dụng:**
```javascript
POST /generate-recommendations
POST /cross-sell-insights
GET /top-bundles
```

**Cách Hoạt Động:**
1. User nhập StockCode (vd: 85123A)
2. Optional: Nhập Customer ID để personalize
3. Click "Get Recommendations" → POST request
4. Hiển thị Top N sản phẩm bán kèm
5. Show insights: Bundle strategy, Timing, ROI
6. Click "Load Top Bundles" → Show global bundles

**Test:**
```bash
# Mở sales.html
# Nhập StockCode: 85123A
# Click "Get Recommendations"
# Xem top 6 products được gợi ý
# Check Insights section
```

## 🔧 Cấu Hình & Troubleshooting

### CORS Configuration

Tất cả Python APIs đã được config CORS để accept requests từ:
```python
allow_origins=["http://localhost:8080", "http://localhost:3000"]
```

Nếu dùng port khác, cập nhật trong từng `*_api.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:YOUR_PORT"],  # Thêm port của bạn
    ...
)
```

### API URL Configuration

Trong mỗi HTML file, có config:
```javascript
const ADMIN_API_URL = 'http://localhost:8001';
const INVENTORY_API_URL = 'http://localhost:8002';
const MARKETING_API_URL = 'http://localhost:8003';
const SALES_API_URL = 'http://localhost:8004';
```

Nếu deploy lên server, thay đổi URLs này.

### MongoDB Connection

Tất cả APIs kết nối tới MongoDB qua `db_utils.py`:
```python
MONGO_URI = "mongodb+srv://vuthanhlam848:vuthanhlam848@cluster0.s9cdtme.mongodb.net/DSS"
DATABASE_NAME = "DSS"
```

### Common Issues

**1. API không chạy được:**
```bash
# Kiểm tra dependencies
pip install -r requirements.txt

# Kiểm tra MongoDB connection
python db_utils.py
```

**2. Dashboard không load data:**
```bash
# Mở Browser Console (F12)
# Xem network tab
# Check có lỗi CORS không

# Verify APIs đang chạy
curl http://localhost:8001/health
```

**3. Port already in use:**
```bash
# Linux/Mac
lsof -ti:8001 | xargs kill -9

# Windows
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

## 📈 Kiến Trúc Data Flow

### Ví dụ: Admin Dashboard Load KPIs

```
1. Browser (admin.html)
   ↓
2. JavaScript: fetch('http://localhost:8001/kpis', {method: 'POST', ...})
   ↓
3. Admin API (FastAPI)
   ↓
4. db_utils.get_transactions_df()
   ↓
5. MongoDB Atlas
   ↓
6. pandas DataFrame processing
   ↓
7. Calculate: total_revenue, total_transactions, etc.
   ↓
8. Return JSON: {total_revenue: 1234567.89, ...}
   ↓
9. JavaScript: Update HTML elements
   ↓
10. User sees: "$1.23M"
```

## 🎯 Best Practices

### 1. Development Workflow
```bash
# Terminal 1: Start Python APIs
cd python-apis
./run_all.sh

# Terminal 2: Start Spring Boot (optional)
./mvnw spring-boot:run

# Browser: Open dashboard
http://localhost:8080/dashboard/admin
```

### 2. Testing Flow
```bash
# 1. Test MongoDB connection
python db_utils.py

# 2. Test individual APIs
python test_apis.py

# 3. Test UI integration
# Open each dashboard in browser
# Check Console for errors
# Verify data loads correctly
```

### 3. Debugging
```javascript
// Enable verbose logging in JavaScript
console.log('API Response:', data);

// Check network tab in DevTools
// Look for failed requests (red)
// Check response payloads
```

## 📝 Next Steps

### Production Deployment

1. **Containerize APIs**
```dockerfile
FROM python:3.9
COPY python-apis /app
RUN pip install -r requirements.txt
CMD ["python", "admin_api.py"]
```

2. **Environment Variables**
```bash
export MONGO_URI="mongodb+srv://..."
export API_PORT=8001
```

3. **Load Balancer / Nginx**
```nginx
upstream admin_api {
    server localhost:8001;
}

location /api/admin {
    proxy_pass http://admin_api;
}
```

4. **Authentication**
- Add JWT tokens to API requests
- Validate user roles before returning data

## 🎓 Tài Liệu Tham Khảo

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Chart.js**: https://www.chartjs.org/
- **MongoDB Python**: https://pymongo.readthedocs.io/
- **Scikit-learn**: https://scikit-learn.org/
- **MLxtend (Apriori)**: http://rasbt.github.io/mlxtend/

---

**Tạo bởi:** AI Assistant  
**Ngày:** November 3, 2025  
**Version:** 1.0.0
