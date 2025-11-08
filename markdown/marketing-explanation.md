# 📢 Marketing Dashboard - Giải thích chi tiết

## 📋 Mục lục
1. [Tổng quan kiến trúc](#1-tổng-quan-kiến-trúc)
2. [Backend - Python FastAPI](#2-backend---python-fastapi)
3. [Middleware - Spring Boot Gateway](#3-middleware---spring-boot-gateway)
4. [Frontend - HTML/JavaScript](#4-frontend---htmljavascript)
5. [Luồng hoạt động](#5-luồng-hoạt-động)
6. [Các tính năng chính](#6-các-tính-năng-chính)

---

## 1. Tổng quan kiến trúc

Hệ thống Marketing Dashboard sử dụng kiến trúc **3-tier** với **microservices**:

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Browser)                        │
│         marketing.html + JavaScript (Port 8080)             │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP Requests
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              MIDDLEWARE (Spring Boot)                        │
│         ApiGatewayController + ExternalApiService           │
│                    (Port 8080)                               │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API Calls
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           BACKEND (Python FastAPI)                           │
│         marketing_api.py (Port 8003)                        │
│   - RFM Analysis                                             │
│   - Customer Segmentation                                    │
│   - Market Basket Analysis (Apriori)                         │
└──────────────────────┬──────────────────────────────────────┘
                       │ Đọc dữ liệu
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              DATA SOURCES                                    │
│   - data/online_retail_cleaned.csv (Local File)             │
│   - MongoDB (Fallback)                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Backend - Python FastAPI

### 📁 File: `python-apis/marketing_api.py`

### 2.1. Cấu trúc tổng quan

```python
FastAPI Application (Port 8003)
├── Data Loading Layer
│   ├── get_local_transactions_df()     # Load từ CSV (NHANH)
│   ├── get_date_range_from_local()     # Lấy khoảng ngày
│   └── Caching mechanism                # Cache 1 giờ
│
├── RFM Analysis Module
│   ├── calculate_quantiles()            # Tính quantiles cho RFM
│   ├── segment_label()                  # Phân loại khách hàng
│   ├── segment_characteristics()        # Mô tả đặc điểm
│   └── segment_rules_text()             # Gợi ý hành động
│
├── Market Basket Analysis Module
│   ├── create_stock_to_description_mapping()
│   ├── format_product_display()
│   └── get_lift_strength()              # Đánh giá độ mạnh association
│
└── API Endpoints
    ├── /date-range-info                 # Lấy phạm vi ngày
    ├── /calculate-rfm                   # RFM cơ bản
    ├── /calculate-rfm-advanced          # RFM nâng cao
    ├── /run-segmentation                # Phân khúc khách hàng
    ├── /segment-basket-analysis         # MBA theo segment
    └── /market-basket-analysis          # MBA tổng quát
```

### 2.2. Chi tiết các chức năng chính

#### 🎯 **A. Customer Segmentation (Phân khúc khách hàng)**

**Endpoint:** `POST /run-segmentation`

**Quy trình xử lý:**

```python
# BƯỚC 1: Load dữ liệu giao dịch
df = get_local_transactions_df()  # Load từ CSV với caching

# BƯỚC 2: Lọc theo khoảng thời gian (nếu có)
if start_date or end_date:
    df = filter_by_date_range(df, start_date, end_date)

# BƯỚC 3: Tính RFM cho mỗi khách hàng
reference_date = df['InvoiceDate'].max() + timedelta(days=1)

rfm = df.groupby('CustomerID').agg({
    'InvoiceDate': lambda x: (reference_date - x.max()).days,  # Recency
    'InvoiceNo': 'nunique',                                     # Frequency  
    'Revenue': 'sum'                                            # Monetary
})

# BƯỚC 4: Tính quantiles để phân loại
quantiles = calculate_quantiles(rfm)
# quantiles = {
#     'recency': {'q25': 18, 'q50': 50, 'q75': 143},
#     'frequency': {'q25': 2, 'q50': 4, 'q75': 9},
#     'monetary': {'q25': 293, 'q50': 648, 'q75': 1570}
# }

# BƯỚC 5: Áp dụng logic phân khúc (Heuristic-based)
rfm['SegmentName'] = rfm.apply(lambda row: segment_label(row, quantiles), axis=1)
```

**Logic phân khúc (5 nhóm):**

```python
def segment_label(row, quantiles):
    """
    🏆 Champions: 
       - Recency ≤ Q25 (mới mua gần đây)
       - Frequency ≥ Q75 (mua thường xuyên)
       - Monetary ≥ Q75 (chi tiêu cao)
       
    💎 Loyal:
       - Recency ≤ Q50 (tương đối gần)
       - Frequency ≥ Q50 (mua khá thường xuyên)
       
    ⚠️ At-Risk:
       - Recency ≥ Q75 (lâu không mua)
       - Frequency ≤ Q25 (mua ít)
       
    😴 Hibernating:
       - Recency ≥ Q50 (khá lâu không mua)
       - Frequency ≤ Q50 (mua ít)
       
    👥 Regulars:
       - Tất cả những khách hàng còn lại
    """
```

**Kết quả trả về:**

```json
{
  "success": true,
  "n_segments": 5,
  "total_customers": 4372,
  "date_range": {
    "start": "2010-12-01",
    "end": "2011-12-09"
  },
  "segments": [
    {
      "segment_id": 0,
      "segment_name": "Champions",
      "customer_count": 873,
      "avg_recency": 12.5,
      "avg_frequency": 15.3,
      "avg_monetary": 3245.67,
      "total_value": 2833427.91,
      "characteristics": "🏆 Nhóm khách hàng VIP nhất...",
      "recommended_actions": [
        "Ưu đãi VIP/early access",
        "Chương trình giới thiệu bạn bè",
        "Tích điểm và upgrade thành viên"
      ]
    },
    // ... 4 segments khác
  ]
}
```

#### 🛒 **B. Market Basket Analysis (Phân tích giỏ hàng)**

**Endpoint:** `POST /market-basket-analysis`

**Thuật toán: Apriori Algorithm**

**Quy trình xử lý:**

```python
# BƯỚC 1: Chuẩn bị dữ liệu
df = get_local_transactions_df()

# BƯỚC 2: Lọc theo segment (nếu có) và date range
if segment_name:
    # Chạy segmentation để lấy danh sách CustomerID của segment
    segment_customers = get_customers_in_segment(segment_name)
    df = df[df['CustomerID'].isin(segment_customers)]

# BƯỚC 3: Tối ưu - Chỉ lấy top 200 sản phẩm phổ biến nhất
product_counts = df['Description'].value_counts()
top_products = product_counts.head(200).index.tolist()
df = df[df['Description'].isin(top_products)]

# BƯỚC 4: Tạo ma trận one-hot encoding (basket)
basket = df.groupby(['InvoiceNo', 'Description'])['Quantity'].sum().unstack().fillna(0)
basket_encoded = basket.map(lambda x: 1 if x > 0 else 0)

# Ma trận basket_encoded:
#              Product_A  Product_B  Product_C  ...
# Invoice_001      1          0          1      ...
# Invoice_002      0          1          1      ...
# Invoice_003      1          1          0      ...

# BƯỚC 5: Chạy thuật toán Apriori
frequent_itemsets = apriori(
    basket_encoded,
    min_support=0.01,      # Xuất hiện ít nhất 1% đơn hàng
    use_colnames=True
)

# BƯỚC 6: Tạo association rules
rules = association_rules(
    frequent_itemsets,
    metric="confidence",
    min_threshold=0.3      # Độ tin cậy tối thiểu 30%
)

# BƯỚC 7: Sắp xếp theo lift và confidence
rules = rules.sort_values(['lift', 'confidence'], ascending=False).head(10)
```

**Giải thích các chỉ số:**

```
📊 Support (Độ phổ biến):
   = P(A ∩ B) = Số đơn có cả A và B / Tổng số đơn
   VD: Support = 0.05 = 5% đơn hàng có cả 2 sản phẩm
   
🎯 Confidence (Độ tin cậy):
   = P(B|A) = P(A ∩ B) / P(A)
   VD: Confidence = 0.7 = 70% khách mua A sẽ mua B
   
📈 Lift (Độ nâng cao):
   = Confidence / P(B)
   VD: Lift = 2.5 = Khả năng mua B tăng 2.5 lần khi đã mua A
   - Lift > 1: Positive correlation (mua A → tăng khả năng mua B)
   - Lift = 1: No correlation
   - Lift < 1: Negative correlation
```

**Kết quả trả về:**

```json
{
  "success": true,
  "total_bundles_found": 45,
  "displayed_bundles": 10,
  "top_recommendation": {
    "antecedents": ["WHITE HANGING HEART T-LIGHT HOLDER"],
    "consequents": ["REGENCY CAKESTAND 3 TIER"],
    "support": 0.0234,
    "confidence": 0.7123,
    "lift": 2.89,
    "strength": "🔥",
    "expected_revenue": 1245.67
  },
  "bundles": [
    // ... 10 product bundles
  ]
}
```

### 2.3. Tối ưu hóa hiệu suất

```python
# ✅ Sử dụng caching
_cached_df = None
_cache_timestamp = None
_cache_ttl = 3600  # Cache 1 giờ

def get_local_transactions_df():
    """Load từ CSV với caching - NHANH GẤP 10 LẦN so với MongoDB"""
    if cache_is_valid():
        return _cached_df.copy()
    
    # Load từ CSV
    df = pd.read_csv(CSV_FILE)
    _cached_df = df.copy()
    _cache_timestamp = datetime.now()
    return df

# ✅ Giới hạn dữ liệu cho Market Basket Analysis
# Chỉ lấy top 200 sản phẩm thay vì toàn bộ
# Chỉ lấy 50,000 transactions gần nhất
```

---

## 3. Middleware - Spring Boot Gateway

### 📁 Files liên quan:
- `ApiGatewayController.java`
- `ExternalApiService.java`

### 3.1. API Gateway Controller

```java
@RestController
@RequestMapping("/api/gateway")
public class ApiGatewayController {
    
    @Autowired
    private ExternalApiService externalApiService;
    
    // ============ MARKETING APIs ============
    
    @PostMapping("/marketing/{endpoint}")
    @PreAuthorize("hasAnyRole('ADMIN', 'MARKETING_MANAGER')")
    public ResponseEntity<Map<String, Object>> callMarketingApi(
            @PathVariable String endpoint,
            @RequestBody(required = false) Map<String, Object> requestBody) {
        
        // Gọi Python API thông qua ExternalApiService
        Map<String, Object> result = externalApiService.post(
            "marketing",      // API type
            "/" + endpoint,   // VD: "/run-segmentation"
            requestBody       // Request body từ frontend
        );
        
        return ResponseEntity.ok(result);
    }
}
```

**Vai trò của API Gateway:**

1. **Authentication & Authorization**: 
   - Kiểm tra user đã đăng nhập
   - Chỉ cho phép ADMIN và MARKETING_MANAGER truy cập

2. **Request Forwarding**:
   - Nhận request từ frontend (port 8080)
   - Forward đến Python API (port 8003)

3. **Error Handling**:
   - Xử lý lỗi kết nối
   - Xử lý timeout
   - Trả về error message thân thiện

### 3.2. External API Service

```java
@Service
public class ExternalApiService {
    
    @Value("${api.marketing.url}")
    private String marketingApiUrl;  // http://localhost:8003
    
    public Map<String, Object> post(String apiType, String endpoint, Object requestBody) {
        String fullUrl = marketingApiUrl + endpoint;
        
        try {
            // Tạo HTTP headers
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            // Tạo HTTP entity
            HttpEntity<?> entity = new HttpEntity<>(requestBody, headers);
            
            // Gọi API
            ResponseEntity<Map> response = restTemplate.exchange(
                fullUrl,
                HttpMethod.POST,
                entity,
                Map.class
            );
            
            // Trả về kết quả
            return Map.of(
                "success", true,
                "data", response.getBody(),
                "statusCode", response.getStatusCode().value()
            );
            
        } catch (ResourceAccessException e) {
            // API không khả dụng hoặc timeout
            return Map.of(
                "success", false,
                "error", "API không khả dụng: " + apiType,
                "message", e.getMessage()
            );
        }
    }
}
```

**Configuration trong `application.properties`:**

```properties
# Marketing API URL
api.marketing.url=http://localhost:8003
```

---

## 4. Frontend - HTML/JavaScript

### 📁 File: `templates/dashboard/marketing.html`

### 4.1. Cấu trúc giao diện

```html
┌─────────────────────────────────────────────────┐
│  📢 DSS - Marketing Analytics                   │
│  User: Marketing Manager         [Logout]       │
├─────────────────────────────────────────────────┤
│                                                  │
│  [👥 Customer Segmentation] [🛒 Market Basket]  │  ← Tabs
│                                                  │
├─────────────────────────────────────────────────┤
│  📅 Analysis Date Range                         │
│  Start: [2010-12-01]  End: [2011-12-09]        │
│  [🔄 Reset to Full Range]                      │
│                                                  │
│  [🚀 Run Segmentation]                         │
├─────────────────────────────────────────────────┤
│  Total Segments: 5    Total Customers: 4,372   │
├─────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────┐    │
│  │ 🏆 Champions                           │    │  ← Segment Card
│  │ 873 customers                          │    │
│  │ ▼                                      │    │
│  ├────────────────────────────────────────┤    │
│  │ 📝 Đặc điểm: Nhóm khách hàng VIP...   │    │
│  │ 📊 Customers: 873                      │    │
│  │ 💰 Total Value: $2,833,428             │    │
│  │ 📅 Avg Recency: 12 days                │    │
│  │ 🔁 Avg Frequency: 15.3 orders          │    │
│  │ 💰 Avg Monetary: $3,246                │    │
│  │ 🎯 Recommended Actions:                │    │
│  │   • Ưu đãi VIP/early access            │    │
│  │   • Chương trình giới thiệu bạn bè     │    │
│  └────────────────────────────────────────┘    │
│  ... (4 segments khác)                         │
└─────────────────────────────────────────────────┘
```

### 4.2. JavaScript - Xử lý tương tác

#### **A. Load Date Range Info (Khởi tạo)**

```javascript
// Khi trang load xong
window.addEventListener('DOMContentLoaded', function() {
    loadDateRangeInfo();
});

async function loadDateRangeInfo() {
    // Gọi API lấy phạm vi ngày
    const response = await fetch(`${MARKETING_API_URL}/date-range-info`);
    const data = await response.json();
    
    // data = {
    //     min_date: "2010-12-01",
    //     max_date: "2011-12-09",
    //     default_start: "2010-12-09",  // Last 12 months
    //     default_end: "2011-12-09"
    // }
    
    // Set giá trị cho date picker
    document.getElementById('segmentStartDate').value = data.default_start;
    document.getElementById('segmentEndDate').value = data.default_end;
    
    // Set min/max cho date picker
    document.getElementById('segmentStartDate').min = data.min_date;
    document.getElementById('segmentStartDate').max = data.max_date;
}
```

#### **B. Run Segmentation**

```javascript
async function runSegmentation() {
    // Lấy giá trị date range
    const startDate = document.getElementById('segmentStartDate').value;
    const endDate = document.getElementById('segmentEndDate').value;
    
    // Hiển thị loading
    container.innerHTML = '<div class="loading">Running segmentation...</div>';
    
    try {
        // Tạo request body
        const requestBody = {
            n_segments: 5,
            use_existing_rfm: false,
            start_date: startDate,
            end_date: endDate
        };
        
        // Gọi API Python thông qua Spring Boot Gateway
        // KHÔNG gọi trực tiếp đến Python API!
        const response = await fetch(`${MARKETING_API_URL}/run-segmentation`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        const data = await response.json();
        
        // Hiển thị kết quả
        displaySegments(data);
        
    } catch (error) {
        // Xử lý lỗi
        container.innerHTML = `<div class="error">
            Failed to run segmentation: ${error.message}
        </div>`;
    }
}

function displaySegments(data) {
    // Update stats
    document.getElementById('totalSegments').textContent = data.n_segments;
    document.getElementById('totalCustomers').textContent = 
        data.total_customers.toLocaleString();
    
    // Render segment cards
    const html = data.segments.map((segment, index) => `
        <div class="segment-accordion ${index === 0 ? 'active' : ''}">
            <div class="segment-tab" onclick="toggleSegment(this)">
                <div class="segment-tab-icon">
                    ${getSegmentEmoji(segment.segment_name)}
                </div>
                <div class="segment-tab-info">
                    <div class="segment-tab-name">${segment.segment_name}</div>
                    <div class="segment-tab-count">
                        ${segment.customer_count.toLocaleString()} customers
                    </div>
                </div>
            </div>
            
            <div class="segment-details">
                <div class="segment-description">
                    ${segment.characteristics}
                </div>
                
                <div class="segment-stats-primary">
                    <div class="stat-primary">
                        <div class="stat-primary-label">Customers</div>
                        <div class="stat-primary-value">
                            ${segment.customer_count.toLocaleString()}
                        </div>
                    </div>
                    <div class="stat-primary">
                        <div class="stat-primary-label">Total Value</div>
                        <div class="stat-primary-value">
                            $${segment.total_value.toLocaleString()}
                        </div>
                    </div>
                </div>
                
                <div class="segment-rfm-grid">
                    <div class="rfm-metric">
                        <div class="rfm-icon">📅</div>
                        <div class="rfm-content">
                            <div class="rfm-label">Avg Recency</div>
                            <div class="rfm-value">
                                ${segment.avg_recency.toFixed(0)} days
                            </div>
                        </div>
                    </div>
                    <!-- ... Frequency, Monetary -->
                </div>
                
                <div class="segment-actions">
                    <div class="actions-header">
                        <span class="actions-icon">🎯</span>
                        <span class="actions-title">Recommended Plays</span>
                    </div>
                    <ul class="actions-list">
                        ${segment.recommended_actions.map(action => 
                            `<li>${action}</li>`
                        ).join('')}
                    </ul>
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}
```

#### **C. Load Product Bundles**

```javascript
async function loadProductBundles() {
    const segmentName = document.getElementById('basketSegment').value;
    const startDate = document.getElementById('basketStartDate').value;
    const endDate = document.getElementById('basketEndDate').value;
    
    container.innerHTML = '<div class="loading">Mining association rules...</div>';
    
    try {
        let response;
        
        // Chọn endpoint dựa trên segment
        if (segmentName) {
            // Phân tích theo segment cụ thể
            const params = new URLSearchParams({
                segment_name: segmentName,
                min_support: '0.01',
                min_confidence: '0.25',
                top_n: '10',
                start_date: startDate,
                end_date: endDate
            });
            
            response = await fetch(
                `${MARKETING_API_URL}/segment-basket-analysis?${params}`,
                { method: 'POST' }
            );
        } else {
            // Phân tích toàn bộ khách hàng
            const params = new URLSearchParams({
                min_support: '0.01',
                min_confidence: '0.3',
                top_n: '10',
                start_date: startDate,
                end_date: endDate
            });
            
            response = await fetch(
                `${MARKETING_API_URL}/product-bundles?${params}`,
                { method: 'POST' }
            );
        }
        
        const data = await response.json();
        
        // Hiển thị top recommendation
        if (data.top_recommendation) {
            const rec = data.top_recommendation;
            html += `
                <div class="top-recommendation-banner">
                    <h3>🎯 Top Product Bundle Recommendation</h3>
                    <div class="recommendation-content">
                        <div>When customers buy: ${rec.antecedents_display}</div>
                        <div class="recommendation-arrow">→</div>
                        <div>They also buy: ${rec.consequents_display}</div>
                    </div>
                    <div class="recommendation-metrics">
                        <span>Confidence: ${(rec.confidence * 100).toFixed(1)}%</span>
                        <span>Lift: ${rec.lift.toFixed(2)}x</span>
                        <span>Expected Revenue: $${rec.expected_revenue.toLocaleString()}</span>
                    </div>
                </div>
            `;
        }
        
        // Hiển thị danh sách bundles
        data.bundles.forEach((bundle, index) => {
            html += renderBundleCard(bundle, index);
        });
        
        container.innerHTML = html;
        
    } catch (error) {
        container.innerHTML = `<div class="error">
            Failed to load bundles: ${error.message}
        </div>`;
    }
}
```

---

## 5. Luồng hoạt động

### 5.1. User Login và Authorization

```
1. User login với username/password
   ↓
2. Spring Security xác thực
   ↓
3. Kiểm tra role = MARKETING_MANAGER
   ↓
4. Redirect đến /marketing/dashboard
   ↓
5. Load marketing.html
```

### 5.2. Run Customer Segmentation

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ 1. User click "Run Segmentation"
       │
       ▼
┌─────────────────────────────────────────────┐
│  marketing.html (JavaScript)                │
│  - Lấy startDate, endDate từ form          │
│  - Tạo requestBody = {                     │
│      n_segments: 5,                        │
│      start_date: "2010-12-01",            │
│      end_date: "2011-12-09"               │
│    }                                        │
└──────┬──────────────────────────────────────┘
       │ 2. POST http://localhost:8003/run-segmentation
       │    (Gọi TRỰC TIẾP đến Python API)
       │    (NOTE: Trong production nên qua Gateway)
       ▼
┌──────────────────────────────────────────────┐
│  marketing_api.py (FastAPI)                  │
│                                              │
│  3. Load data: get_local_transactions_df()   │
│     - Kiểm tra cache (valid trong 1h)       │
│     - Nếu miss: Load từ CSV file            │
│     - Cache lại kết quả                      │
│                                              │
│  4. Filter by date range (if provided)       │
│     df = filter_by_date_range(df, ...)      │
│                                              │
│  5. Calculate RFM:                           │
│     rfm = df.groupby('CustomerID').agg({    │
│         'InvoiceDate': recency,             │
│         'InvoiceNo': frequency,             │
│         'Revenue': monetary                 │
│     })                                       │
│                                              │
│  6. Calculate quantiles:                     │
│     quantiles = {                            │
│         'recency': {q25, q50, q75},         │
│         'frequency': {...},                 │
│         'monetary': {...}                   │
│     }                                        │
│                                              │
│  7. Apply heuristic segmentation:            │
│     rfm['SegmentName'] = rfm.apply(          │
│         lambda row: segment_label(row, q)   │
│     )                                        │
│                                              │
│  8. Build segment summary:                   │
│     For each segment:                        │
│       - Count customers                      │
│       - Calculate avg RFM                    │
│       - Generate characteristics            │
│       - Add recommended actions             │
│                                              │
│  9. Return JSON response                     │
└──────┬───────────────────────────────────────┘
       │ 10. Response: {
       │       success: true,
       │       n_segments: 5,
       │       segments: [...]
       │     }
       ▼
┌──────────────────────────────────────────────┐
│  marketing.html (JavaScript)                 │
│  11. displaySegments(data)                   │
│      - Update stats (total segments/customers)│
│      - Render segment cards                  │
│      - Show characteristics                  │
│      - Show recommended actions              │
└──────┬───────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│  Browser renders segment cards               │
│  🏆 Champions - 873 customers               │
│  💎 Loyal - 1,245 customers                 │
│  ⚠️ At-Risk - 542 customers                 │
│  😴 Hibernating - 897 customers             │
│  👥 Regulars - 815 customers                │
└──────────────────────────────────────────────┘
```

### 5.3. Run Market Basket Analysis

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ 1. User select segment (optional)
       │    User click "Find Product Bundles"
       ▼
┌──────────────────────────────────────────────┐
│  marketing.html (JavaScript)                 │
│  - segmentName = "Champions"                │
│  - startDate, endDate                        │
└──────┬───────────────────────────────────────┘
       │ 2. POST /segment-basket-analysis
       │    OR POST /product-bundles
       ▼
┌──────────────────────────────────────────────┐
│  marketing_api.py (FastAPI)                  │
│                                              │
│  3. Load data from CSV                       │
│                                              │
│  4. Filter by date range                     │
│                                              │
│  5. If segment specified:                    │
│     - Run segmentation                       │
│     - Get customer IDs in segment           │
│     - Filter transactions                    │
│                                              │
│  6. Optimize:                                │
│     - Get top 200 products by frequency     │
│     - Limit to 50,000 recent transactions   │
│                                              │
│  7. Create basket matrix (one-hot):          │
│     basket = df.groupby(['InvoiceNo',       │
│         'Description'])['Quantity']         │
│         .sum().unstack().fillna(0)          │
│     basket_encoded = (basket > 0).astype(int)│
│                                              │
│     Matrix:                                  │
│              Prod_A  Prod_B  Prod_C         │
│     Inv_001    1       0       1            │
│     Inv_002    0       1       1            │
│     Inv_003    1       1       0            │
│                                              │
│  8. Run Apriori algorithm:                   │
│     frequent_itemsets = apriori(             │
│         basket_encoded,                      │
│         min_support=0.01                     │
│     )                                        │
│                                              │
│  9. Generate association rules:              │
│     rules = association_rules(               │
│         frequent_itemsets,                   │
│         metric="confidence",                 │
│         min_threshold=0.3                    │
│     )                                        │
│                                              │
│  10. Sort by lift & confidence               │
│      Calculate expected revenue              │
│                                              │
│  11. Return top 10 bundles                   │
└──────┬───────────────────────────────────────┘
       │ 12. Response with bundles
       ▼
┌──────────────────────────────────────────────┐
│  marketing.html (JavaScript)                 │
│  - Show top recommendation banner           │
│  - Render bundle cards                       │
│  - Show support, confidence, lift            │
└──────────────────────────────────────────────┘
```

---

## 6. Các tính năng chính

### 6.1. Customer Segmentation (RFM Analysis)

**Mục đích:**
- Phân khúc khách hàng dựa trên hành vi mua hàng
- Hiểu đặc điểm của từng nhóm khách hàng
- Đưa ra chiến lược marketing phù hợp

**5 Segments:**

| Segment | Đặc điểm | Chiến lược |
|---------|----------|------------|
| 🏆 **Champions** | Mua gần đây, thường xuyên, chi tiêu cao | VIP offers, Referral program, Early access |
| 💎 **Loyal** | Mua tương đối gần, khá thường xuyên | Upsell, Birthday offers, Loyalty program |
| ⚠️ **At-Risk** | Lâu không mua, tần suất thấp | Win-back email + 15% discount, Survey |
| 😴 **Hibernating** | Rất lâu không mua, tần suất thấp | Remarketing campaign, Free shipping |
| 👥 **Regulars** | Khách hàng ổn định | Regular promotions, Cross-sell |

**Insights có thể rút ra:**

1. **Customer Lifetime Value (CLV)**:
   - Champions có CLV cao nhất
   - Cần focus resources vào retention

2. **Churn Risk**:
   - At-Risk và Hibernating có nguy cơ churn cao
   - Cần intervention campaigns ngay

3. **Growth Opportunities**:
   - Loyal có tiềm năng upgrade lên Champions
   - Regulars có thể nâng frequency

### 6.2. Market Basket Analysis

**Mục đích:**
- Tìm sản phẩm thường được mua cùng nhau
- Tối ưu product bundling và cross-sell
- Tăng average order value

**Use Cases:**

1. **Product Bundling**:
   ```
   "White Hanging Heart T-Light Holder" → "Regency Cakestand 3 Tier"
   Confidence: 71% | Lift: 2.89x
   → Tạo bundle "Home Decoration Set"
   ```

2. **Store Layout Optimization**:
   ```
   Đặt sản phẩm có lift cao gần nhau
   → Tăng impulse buying
   ```

3. **Personalized Recommendations**:
   ```
   User thêm Product A vào giỏ
   → Suggest Product B (từ rules)
   ```

4. **Segment-Specific Bundles**:
   ```
   Champions thích mua:
   - Luxury home decor sets
   
   Regulars thích mua:
   - Practical kitchen items
   
   → Tạo bundles riêng cho từng segment
   ```

**Các chỉ số quan trọng:**

- **Support ≥ 1%**: Xuất hiện đủ thường xuyên để đáng tin
- **Confidence ≥ 30%**: Đủ cao để recommend
- **Lift > 1.5**: Association mạnh, đáng đầu tư

### 6.3. Date Range Filtering

**Mục đích:**
- So sánh performance theo thời gian
- Phân tích seasonal trends
- Đánh giá hiệu quả campaigns

**Ví dụ:**
```
Q1 2011:
- Champions: 800 customers
- At-Risk: 300 customers

Q4 2011:
- Champions: 950 customers (+18.75%)
- At-Risk: 250 customers (-16.67%)

→ Marketing campaigns Q4 hiệu quả!
```

---

## 7. Best Practices & Tips

### 7.1. Performance Optimization

```python
# ✅ DO: Sử dụng caching
_cached_df = None
_cache_ttl = 3600

# ✅ DO: Giới hạn dữ liệu cho MBA
top_products = df['Description'].value_counts().head(200)
recent_transactions = df.nlargest(50000, 'InvoiceDate')

# ❌ DON'T: Load toàn bộ data mỗi lần
df = pd.read_csv(CSV_FILE)  # Slow!
```

### 7.2. Error Handling

```javascript
// ✅ DO: Xử lý lỗi gracefully
try {
    const response = await fetch(url);
    if (!response.ok) throw new Error('API failed');
    const data = await response.json();
    displayData(data);
} catch (error) {
    showErrorMessage(error.message);
}

// ❌ DON'T: Bỏ qua error handling
const data = await fetch(url).then(r => r.json());
```

### 7.3. Security

```java
// ✅ DO: Kiểm tra authorization
@PreAuthorize("hasAnyRole('ADMIN', 'MARKETING_MANAGER')")
public ResponseEntity<?> callMarketingApi() { ... }

// ✅ DO: Validate input
if (min_support < 0.001 || min_support > 0.5) {
    throw new HTTPException(400, "Invalid min_support");
}
```

---

## 8. Troubleshooting

### Vấn đề thường gặp:

1. **Marketing API không khả dụng**
   ```
   Error: "API không khả dụng: marketing"
   
   Giải pháp:
   - Kiểm tra Python API có đang chạy không (port 8003)
   - Run: python marketing_api.py
   - Kiểm tra firewall
   ```

2. **Segmentation trả về 0 segments**
   ```
   Error: "Not enough data for segmentation"
   
   Giải pháp:
   - Kiểm tra date range có dữ liệu không
   - Reset về full date range
   - Kiểm tra CSV file có data không
   ```

3. **Market Basket không tìm thấy rules**
   ```
   Message: "No rules found. Try lowering min_confidence."
   
   Giải pháp:
   - Giảm min_support từ 0.01 → 0.005
   - Giảm min_confidence từ 0.3 → 0.2
   - Chọn segment có nhiều khách hàng hơn
   ```

4. **Slow performance**
   ```
   Segmentation mất > 10 giây
   
   Giải pháp:
   - Kiểm tra cache có hoạt động không
   - Giảm date range
   - Restart Python API để clear memory
   ```

---

## 9. Tóm tắt

**Marketing Dashboard** là một hệ thống **Prescriptive DSS** (Decision Support System) giúp Marketing Manager:

1. **Hiểu khách hàng** qua RFM segmentation
2. **Tối ưu strategy** với recommended actions cho từng segment
3. **Tăng doanh thu** thông qua product bundling và cross-sell
4. **Ra quyết định** dựa trên data, không phải gut feeling

**Tech Stack:**
- **Backend**: Python FastAPI + Pandas + Scikit-learn + MLxtend
- **Middleware**: Spring Boot + Spring Security
- **Frontend**: HTML + JavaScript (Vanilla)
- **Data**: CSV files + MongoDB (fallback)

**Key Algorithms:**
- **RFM Analysis**: Heuristic-based segmentation
- **Apriori Algorithm**: Market basket analysis với association rules

---

**Tác giả**: DSS Group 5  
**Version**: 1.0.0  
**Last Updated**: 2025-11-08
