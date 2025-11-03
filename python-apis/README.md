# Python APIs for DSS Project

Dự án Decision Support System (DSS) với 4 APIs Python cho 4 vai trò khác nhau, kết nối trực tiếp với MongoDB.

## 📋 Tổng Quan

| API | Port | Vai Trò | DSS Type | Mô tả |
|-----|------|---------|----------|-------|
| **Admin API** | 8001 | Admin/Director | Descriptive | Sales overview, KPIs, revenue trends |
| **Inventory API** | 8002 | Inventory Manager | Prescriptive | Return risk management, policy simulation |
| **Marketing API** | 8003 | Marketing Manager | Prescriptive | Customer segmentation, market basket analysis |
| **Sales API** | 8004 | Sales Manager | Predictive | Cross-sell recommendations, next best offer |

## 🚀 Cài Đặt

### 1. Cài đặt dependencies

```bash
cd python-apis
pip install -r requirements.txt
```

Hoặc với virtual environment:

```bash
cd python-apis
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 2. Kiểm tra kết nối MongoDB

```bash
python db_utils.py
```

Nên thấy output:
```
✅ MongoDB connection successful!
📦 Available collections: ['transactions', 'customer_rfm', ...]
```

## 🏃 Chạy APIs

### Chạy từng API riêng lẻ:

#### Admin API (Port 8001)
```bash
python admin_api.py
```
- Documentation: http://localhost:8001/docs
- Health check: http://localhost:8001/health

#### Inventory API (Port 8002)
```bash
python inventory_api.py
```
- Documentation: http://localhost:8002/docs
- Health check: http://localhost:8002/health

#### Marketing API (Port 8003)
```bash
python marketing_api.py
```
- Documentation: http://localhost:8003/docs
- Health check: http://localhost:8003/health

#### Sales API (Port 8004)
```bash
python sales_api.py
```
- Documentation: http://localhost:8004/docs
- Health check: http://localhost:8004/health

### Chạy tất cả APIs cùng lúc:

Tạo file `run_all.sh` (Linux/Mac):
```bash
#!/bin/bash
python admin_api.py &
python inventory_api.py &
python marketing_api.py &
python sales_api.py &
wait
```

Hoặc `run_all.bat` (Windows):
```batch
start python admin_api.py
start python inventory_api.py
start python marketing_api.py
start python sales_api.py
```

## 📚 Chi Tiết APIs

### 1. Admin API (Port 8001)

**Mục đích:** Giám sát tổng thể, phân tích doanh thu, Top-N countries/products

**Endpoints chính:**
- `POST /kpis` - Lấy KPIs tổng quan
- `POST /monthly-trend` - Xu hướng doanh thu theo tháng
- `POST /top-countries` - Top N quốc gia theo doanh thu
- `POST /top-products` - Top N sản phẩm theo doanh thu
- `POST /revenue-summary` - Báo cáo tổng hợp

**Ví dụ request:**
```bash
curl -X POST "http://localhost:8001/kpis" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "top_n": 10,
    "exclude_cancelled": true
  }'
```

### 2. Inventory API (Port 8002)

**Mục đích:** Quản lý rủi ro trả hàng, mô phỏng chính sách

**Endpoints chính:**
- `POST /calculate-risk-score` - Tính điểm rủi ro cho đơn hàng
- `POST /simulate-policy` - Mô phỏng chính sách với threshold tau
- `POST /find-optimal-threshold` - Tìm threshold tối ưu
- `GET /risk-distribution` - Phân bố điểm rủi ro

**Ví dụ - Tính risk score:**
```bash
curl -X POST "http://localhost:8002/calculate-risk-score" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "12345",
    "stock_code": "85123A",
    "quantity": 10,
    "unit_price": 2.55,
    "country": "United Kingdom"
  }'
```

**Ví dụ - Mô phỏng policy:**
```bash
curl -X POST "http://localhost:8002/simulate-policy" \
  -H "Content-Type: application/json" \
  -d '{
    "threshold_tau": 50,
    "return_processing_cost": 10.0,
    "conversion_impact": 0.2,
    "sample_size": 1000
  }'
```

### 3. Marketing API (Port 8003)

**Mục đích:** Phân khúc khách hàng (RFM), Market Basket Analysis

**Endpoints chính:**
- `POST /calculate-rfm` - Tính RFM scores cho khách hàng
- `POST /run-segmentation` - Chạy K-Means clustering
- `GET /segment-overview` - Tổng quan các segments
- `POST /market-basket-analysis` - Phân tích giỏ hàng
- `POST /product-bundles` - Gợi ý gói sản phẩm

**Ví dụ - Phân khúc khách hàng:**
```bash
curl -X POST "http://localhost:8003/run-segmentation" \
  -H "Content-Type: application/json" \
  -d '{
    "n_segments": 4,
    "use_existing_rfm": true
  }'
```

**Ví dụ - Market Basket Analysis:**
```bash
curl -X POST "http://localhost:8003/market-basket-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "min_support": 0.01,
    "min_confidence": 0.3,
    "top_n": 10
  }'
```

### 4. Sales API (Port 8004)

**Mục đích:** Cross-sell, Next Best Offer, Product Recommendations

**Endpoints chính:**
- `POST /generate-recommendations` - Gợi ý sản phẩm bán kèm
- `POST /cross-sell-insights` - Insights cho chiến lược cross-sell
- `POST /product-network` - Network graph sản phẩm liên quan
- `GET /customer-recommendations/{customer_id}` - Gợi ý cá nhân hóa
- `GET /top-bundles` - Top bundles tổng thể

**Ví dụ - Gợi ý sản phẩm:**
```bash
curl -X POST "http://localhost:8004/generate-recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "85123A",
    "customer_id": "12345",
    "confidence_threshold": 0.3,
    "top_n": 5,
    "min_support": 0.01
  }'
```

**Ví dụ - Gợi ý cho khách hàng:**
```bash
curl -X GET "http://localhost:8004/customer-recommendations/12345?top_n=5"
```

## 🔧 Cấu Trúc Project

```
python-apis/
├── requirements.txt          # Dependencies
├── db_utils.py              # MongoDB connection utilities
├── admin_api.py             # Admin API (Port 8001)
├── inventory_api.py         # Inventory API (Port 8002)
├── marketing_api.py         # Marketing API (Port 8003)
├── sales_api.py             # Sales API (Port 8004)
└── README.md                # Tài liệu này
```

## 📊 Dữ Liệu MongoDB

Các APIs kết nối tới MongoDB với cấu hình:
- **URI:** `mongodb+srv://vuthanhlam848:vuthanhlam848@cluster0.s9cdtme.mongodb.net/DSS`
- **Database:** `DSS`

### Collections dự kiến:
- `transactions` - Dữ liệu giao dịch (online_retail.csv)
- `customer_rfm` - RFM scores (tự động tạo)
- `products` - Thông tin sản phẩm
- `segmentation_results` - Kết quả phân khúc

## 🧪 Testing

### Test với Python:
```python
import requests

# Test Admin API
response = requests.post(
    "http://localhost:8001/kpis",
    json={
        "top_n": 10,
        "exclude_cancelled": True
    }
)
print(response.json())

# Test Inventory API
response = requests.post(
    "http://localhost:8002/simulate-policy",
    json={
        "threshold_tau": 50,
        "return_processing_cost": 10.0,
        "conversion_impact": 0.2
    }
)
print(response.json())
```

### Test với curl:
```bash
# Health checks
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
```

## 📝 Notes cho Development

### Customization:
1. **Collection names:** Sửa trong `db_utils.py` nếu collection names khác
2. **MongoDB URI:** Thay đổi trong `db_utils.py` nếu cần
3. **Port numbers:** Sửa trong từng file API nếu port bị conflict
4. **CORS:** Thêm origins trong mỗi API nếu cần

### Performance:
- Các thuật toán (K-Means, Apriori) có thể chậm với dữ liệu lớn
- Sử dụng `sample_size` parameter để giới hạn dữ liệu
- Cache results trong MongoDB cho production

### Error Handling:
- Tất cả APIs đều có error handling với HTTP status codes
- Check logs để debug issues
- Sử dụng `/docs` endpoint để test interactively

## 🎯 Next Steps

1. **Import dữ liệu vào MongoDB** nếu chưa có
2. **Test từng API** với data thật
3. **Tối ưu parameters** (min_support, confidence, thresholds)
4. **Cache results** cho performance
5. **Add authentication** nếu cần

## 🐛 Troubleshooting

**Import errors:**
```bash
pip install -r requirements.txt --upgrade
```

**MongoDB connection errors:**
- Check MongoDB URI
- Verify network connection
- Check MongoDB Atlas whitelist

**Port already in use:**
```bash
# Linux/Mac
lsof -ti:8001 | xargs kill -9

# Windows
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

## 📞 Support

Nếu có vấn đề, check:
1. FastAPI docs: http://localhost:800X/docs
2. Logs trong terminal
3. MongoDB connection với `python db_utils.py`

---

**Happy coding! 🚀**
