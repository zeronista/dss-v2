# 🎯 Marketing API Integration Guide

**Objective:** Integrate your advanced Streamlit RFM Segmentation & Market Basket Analysis into the FastAPI Marketing Service (Port 8003)

---

## 📋 Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [Data Compatibility](#data-compatibility)
3. [5-Phase Integration Plan](#5-phase-integration-plan)
4. [Implementation Sequence](#implementation-sequence)
5. [Testing Plan](#testing-plan)
6. [Performance Considerations](#performance-considerations)

---

## 🔍 Current State Analysis

### What You Currently Have:

| Component | Streamlit Version | Current API | Status |
|-----------|------------------|-------------|---------|
| **Data Source** | CSV file | MongoDB | ✅ Compatible |
| **RFM Calculation** | ✅ Advanced (with quantiles) | ✅ Basic | 🔄 Needs Enhancement |
| **Segmentation** | ✅ K-Means + Heuristic Naming | ✅ K-Means + Basic Naming | 🔄 Needs Enhancement |
| **Segment Naming** | ✅ 5 Categories (Champions, Loyal, At-Risk, Hibernating, Regulars) | ⚠️ 4 Categories (simplified) | 🔄 Replace with your logic |
| **Segment Characteristics** | ✅ Detailed descriptions | ❌ Missing | ➕ Add |
| **Market Basket** | ✅ Apriori with top 300 products | ✅ Apriori with top 100 products | ✅ Good |
| **Product Bundle Display** | ✅ Rich formatting with descriptions | ⚠️ Basic list | 🔄 Enhance |
| **Date Filtering** | ✅ Dynamic date range | ❌ Missing | ➕ Add |

### Key Insights:

- ✅ **Perfect data compatibility** - MongoDB structure matches your CSV exactly
- ✅ **Core algorithms already exist** - K-Means and Apriori are implemented
- 🔄 **Logic needs refinement** - Your Streamlit heuristics are more sophisticated
- ➕ **Missing features** - Date filtering, detailed characteristics, advanced naming

---

## 📊 Data Compatibility

### CSV ↔ MongoDB Field Mapping:

| Field | Streamlit (CSV) | MongoDB | Status |
|-------|----------------|---------|---------|
| Invoice ID | `InvoiceNo` | `InvoiceNo` | ✅ Identical |
| Product Code | `StockCode` | `StockCode` | ✅ Identical |
| Product Name | `Description` | `Description` | ✅ Identical |
| Quantity | `Quantity` | `Quantity` | ✅ Identical |
| Date | `InvoiceDate` | `InvoiceDate` | ✅ Identical |
| Unit Price | `UnitPrice` | `UnitPrice` | ✅ Identical |
| Customer ID | `CustomerID` | `CustomerID` | ✅ Identical |
| Country | `Country` | `Country` | ✅ Identical |
| Revenue | `Quantity × UnitPrice` | `Revenue` (pre-calculated) | ✅ Compatible |

**Result:** ✅ **Perfect compatibility - No data transformation needed!**

---

## 🚀 5-Phase Integration Plan

---

### **PHASE 1: Enhance RFM Calculation** ⭐⭐⭐

**Duration:** 1-2 days  
**Goal:** Replace basic RFM with your advanced quantile-based approach

#### Changes Required:

1. **In `db_utils.py` - Add date filtering:**
   ```python
   def filter_by_date_range(df, start_date=None, end_date=None):
       """Filter transactions by date range"""
       if start_date:
           df = df[df['InvoiceDate'] >= pd.to_datetime(start_date)]
       if end_date:
           df = df[df['InvoiceDate'] <= pd.to_datetime(end_date)]
       return df
   ```

2. **In `marketing_api.py` - Add quantile calculation:**
   ```python
   def calculate_quantiles(df):
       """Calculate RFM quantiles for heuristic naming"""
       q = df[['Recency', 'Frequency', 'Monetary']].quantile([0.25, 0.5, 0.75])
       return q.to_dict()
   ```

3. **New endpoint:** `POST /calculate-rfm-advanced`
   
   **Request:**
   ```json
   {
     "start_date": "2010-01-01",
     "end_date": "2011-12-31",
     "save_to_db": false
   }
   ```
   
   **Response:**
   ```json
   {
     "success": true,
     "customers_analyzed": 4339,
     "date_range": {
       "start": "2010-01-01",
       "end": "2011-12-31"
     },
     "quantiles": {
       "recency": {"q25": 20, "q50": 50, "q75": 150},
       "frequency": {"q25": 2, "q50": 5, "q75": 12},
       "monetary": {"q25": 300, "q50": 700, "q75": 2000}
     },
     "summary": {
       "avg_recency": 79.5,
       "avg_frequency": 6.2,
       "avg_monetary": 1891.3
     }
   }
   ```

#### Test Cases:
- [ ] RFM with full date range
- [ ] RFM with 6-month range
- [ ] RFM with 1-year range
- [ ] Verify quantiles match Streamlit output

---

### **PHASE 2: Implement Your Heuristic Segment Naming** ⭐⭐⭐

**Duration:** 2-3 days  
**Goal:** Replace basic segmentation with your 5-category logic

#### Changes Required:

1. **Add to `marketing_api.py` - Your exact segment naming logic:**

   ```python
   def segment_label(row, quantiles):
       """
       Heuristic naming based on RFM characteristics
       
       Champions: R ≤ q25 AND F ≥ q75 AND M ≥ q75
       Loyal: R ≤ q50 AND F ≥ q50
       At-Risk: R ≥ q75 AND F ≤ q25
       Hibernating: R ≥ q50 AND F ≤ q50
       Regulars: (default)
       """
       r_q25 = quantiles['recency']['q25']
       r_q50 = quantiles['recency']['q50']
       r_q75 = quantiles['recency']['q75']
       f_q25 = quantiles['frequency']['q25']
       f_q50 = quantiles['frequency']['q50']
       f_q75 = quantiles['frequency']['q75']
       m_q75 = quantiles['monetary']['q75']
       
       if (row['Recency'] <= r_q25 and 
           row['Frequency'] >= f_q75 and 
           row['Monetary'] >= m_q75):
           return "Champions"
       elif row['Recency'] <= r_q50 and row['Frequency'] >= f_q50:
           return "Loyal"
       elif row['Recency'] >= r_q75 and row['Frequency'] <= f_q25:
           return "At-Risk"
       elif row['Recency'] >= r_q50 and row['Frequency'] <= f_q50:
           return "Hibernating"
       else:
           return "Regulars"
   ```

2. **Add segment characteristics function:**

   ```python
   def segment_characteristics(seg_name, avg_recency, avg_frequency, avg_monetary):
       """Generate detailed description of segment characteristics"""
       characteristics = {
           "Champions": f"🏆 **Nhóm khách hàng VIP nhất!** Họ mua hàng thường xuyên (trung bình {avg_frequency:.1f} đơn/khách), chi tiêu cao ({avg_monetary:,.0f}) và vừa mới quay lại ({avg_recency:.0f} ngày trước).",
           
           "Loyal": f"💎 **Khách hàng trung thành.** Tần suất mua hàng tốt ({avg_frequency:.1f} đơn) và chi tiêu ổn định ({avg_monetary:,.0f}). Recency trung bình là {avg_recency:.0f} ngày.",
           
           "At-Risk": f"⚠️ **Nhóm có nguy cơ rời bỏ cao!** Đã lâu không quay lại ({avg_recency:.0f} ngày) và tần suất mua thấp ({avg_frequency:.1f} đơn). Dù từng có giá trị ({avg_monetary:,.0f}), cần hành động ngay.",
           
           "Hibernating": f"😴 **Khách hàng đang 'ngủ đông'.** Rất lâu không quay lại ({avg_recency:.0f} ngày), tần suất mua thấp ({avg_frequency:.1f} đơn). Cần chiến dịch remarketing mạnh mẽ.",
           
           "Regulars": f"👥 **Khách hàng ổn định.** Mua hàng đều đặn với recency {avg_recency:.0f} ngày, frequency {avg_frequency:.1f} đơn và chi tiêu {avg_monetary:,.0f}."
       }
       return characteristics.get(seg_name, "Standard segment")
   ```

3. **Add marketing recommendations function:**

   ```python
   def segment_rules_text(seg_name):
       """Get recommended marketing actions for each segment"""
       mapping = {
           "Champions": [
               "Ưu đãi VIP/early access",
               "Chương trình giới thiệu bạn bè",
               "Tích điểm và upgrade thành viên"
           ],
           "Loyal": [
               "Tích điểm, upsell gói sản phẩm",
               "Ưu đãi sinh nhật",
               "Chương trình giữ chân"
           ],
           "At-Risk": [
               "Email 'Chúng tôi nhớ bạn' + mã -15%",
               "Reactivation bundle giá tốt",
               "Survey lý do churn"
           ],
           "Hibernating": [
               "Chiến dịch quay lại (remarketing)",
               "Giảm vận phí",
               "Limited time offer"
           ],
           "Regulars": [
               "Khuyến mãi định kỳ",
               "Cross-sell sản phẩm bổ trợ",
               "Loyalty tier program"
           ]
       }
       return mapping.get(seg_name, [])
   ```

4. **Updated `/run-segmentation` response:**

   ```json
   {
     "success": true,
     "n_segments": 5,
     "total_customers": 4339,
     "segments": [
       {
         "segment_id": 0,
         "segment_name": "Champions",
         "customer_count": 432,
         "avg_recency": 15.3,
         "avg_frequency": 25.7,
         "avg_monetary": 5430.21,
         "total_value": 2345782.32,
         "characteristics": "🏆 **Nhóm khách hàng VIP nhất!** Họ mua hàng thường xuyên...",
         "recommended_actions": [
           "Ưu đãi VIP/early access",
           "Chương trình giới thiệu bạn bè"
         ]
       }
     ]
   }
   ```

#### Test Cases:
- [ ] Verify all 5 segment names appear
- [ ] Check segment distribution is reasonable
- [ ] Validate heuristic logic with known data
- [ ] Compare results with Streamlit output

---

### **PHASE 3: Add Advanced Market Basket Analysis** ⭐⭐

**Duration:** 2 days  
**Goal:** Implement segment-specific basket analysis with rich formatting

#### Changes Required:

1. **New endpoint:** `POST /segment-basket-analysis`

   **Request:**
   ```json
   {
     "segment_name": "Champions",
     "min_support": 0.01,
     "min_confidence": 0.3,
     "top_n": 10
   }
   ```

   **Response:**
   ```json
   {
     "success": true,
     "segment": "Champions",
     "customer_count": 432,
     "total_bundles_found": 42,
     "displayed_bundles": 10,
     "top_recommendation": {
       "antecedents_display": "WHITE HANGING HEART (85123A)",
       "consequents_display": "JUMBO BAG RED RETRO (22423)",
       "confidence": 0.65,
       "lift": 2.3,
       "strength": "🔥"
     },
     "bundles": [
       {
         "antecedents_display": "WHITE HANGING HEART (85123A)",
         "consequents_display": "JUMBO BAG RED RETRO (22423)",
         "antecedents": ["85123A"],
         "consequents": ["22423"],
         "support": 0.0234,
         "confidence": 0.65,
         "lift": 2.3,
         "strength": "🔥"
       }
     ]
   }
   ```

2. **Update `build_basket_rules()` function:**
   - Keep top 100-200 products (balance performance vs quality)
   - Add product description mapping
   - Truncate long descriptions to 50 chars
   - Add lift strength indicators

3. **Add strength indicator logic:**
   ```python
   def get_lift_strength(lift):
       """Get visual indicator for lift value"""
       if lift > 2.0:
           return "🔥"  # Very strong
       elif lift > 1.5:
           return "✅"  # Good
       else:
           return "➡️"  # Moderate
   ```

#### Test Cases:
- [ ] Test basket analysis for each segment
- [ ] Verify confidence calculations
- [ ] Check lift calculations
- [ ] Validate product description formatting
- [ ] Performance test with large datasets

---

### **PHASE 4: Add Date Range & Filtering Features** ⭐⭐

**Duration:** 1-2 days  
**Goal:** Allow dynamic date filtering like your Streamlit app

#### Changes Required:

1. **New endpoint:** `GET /date-range-info`

   **Response:**
   ```json
   {
     "min_date": "2010-12-01",
     "max_date": "2011-12-09",
     "default_start": "2010-12-09",
     "default_end": "2011-12-09"
   }
   ```

2. **Update all major endpoints to accept date parameters:**
   ```python
   # All endpoints should support:
   @app.post("/calculate-rfm")
   async def calculate_rfm(
       start_date: Optional[str] = None,
       end_date: Optional[str] = None
   ):
   ```

3. **Add request models:**
   ```python
   class RFMRequest(BaseModel):
       start_date: Optional[str] = None
       end_date: Optional[str] = None
       save_to_db: bool = False
   
   class SegmentationRequest(BaseModel):
       n_segments: int = 5
       start_date: Optional[str] = None
       end_date: Optional[str] = None
       use_existing_rfm: bool = True
   ```

#### Test Cases:
- [ ] Test with various date ranges
- [ ] Verify default dates (1 year back)
- [ ] Check boundary conditions
- [ ] Performance with different date ranges

---

### **PHASE 5: Update Frontend (marketing.html)** ⭐⭐⭐

**Duration:** 3-4 days  
**Goal:** Create UI that mirrors your Streamlit functionality

#### Changes Required:

1. **Add Date Range Picker:**
   ```html
   <div class="date-filter-section">
     <label>📅 Khoảng thời gian phân tích:</label>
     <div class="date-inputs">
       <input type="date" id="startDate">
       <span>→</span>
       <input type="date" id="endDate">
       <button onclick="applyDateFilter()">Apply</button>
     </div>
     <span class="info">💡 Default: Last 12 months</span>
   </div>
   ```

2. **Add Segment Selector:**
   ```html
   <div class="segment-selector">
     <label>🔍 Chọn phân khúc để xem chi tiết:</label>
     <select id="segmentSelector" onchange="loadSegmentBundles()">
       <option value="">-- All Customers --</option>
       <option value="Champions">🏆 Champions</option>
       <option value="Loyal">💎 Loyal</option>
       <option value="At-Risk">⚠️ At-Risk</option>
       <option value="Hibernating">😴 Hibernating</option>
       <option value="Regulars">👥 Regulars</option>
     </select>
   </div>
   ```

3. **Enhanced Segment Display Card:**
   ```html
   <div class="segment-card">
     <h3>{segment.segment_name}</h3>
     <p class="characteristics">{segment.characteristics}</p>
     
     <div class="segment-stats">
       <div class="stat">
         <span>👥 Customers:</span>
         <strong>{customer_count}</strong>
       </div>
       <div class="stat">
         <span>💰 Total Value:</span>
         <strong>${total_value}</strong>
       </div>
       <div class="stat">
         <span>📅 Avg Recency:</span>
         <strong>{avg_recency} days</strong>
       </div>
       <div class="stat">
         <span>📊 Avg Frequency:</span>
         <strong>{avg_frequency} orders</strong>
       </div>
     </div>
     
     <div class="actions">
       <strong>🎯 Recommended Actions:</strong>
       <ul>
         {recommended_actions.map(a => `<li>${a}</li>`)}
       </ul>
     </div>
   </div>
   ```

4. **Top Bundle Recommendation Banner:**
   ```html
   <div class="top-recommendation">
     <div class="success-badge">🌟 Top Bundle Recommendation</div>
     <p>When customers buy: <strong>{antecedent}</strong></p>
     <p>Recommend also buying: <strong>{consequent}</strong></p>
     <p class="metrics">
       Confidence: {confidence}% | Lift: {lift}x {strength}
     </p>
   </div>
   ```

5. **Market Basket Table:**
   ```html
   <table class="bundles-table">
     <thead>
       <tr>
         <th>If Customers Buy...</th>
         <th>They Also Buy...</th>
         <th>Support</th>
         <th>Confidence</th>
         <th>Lift</th>
         <th>Strength</th>
       </tr>
     </thead>
     <tbody>
       {bundles.map(bundle => `
         <tr>
           <td>{bundle.antecedents_display}</td>
           <td>{bundle.consequents_display}</td>
           <td>{bundle.support}%</td>
           <td>{bundle.confidence}%</td>
           <td>{bundle.lift}x</td>
           <td>{bundle.strength}</td>
         </tr>
       `)}
     </tbody>
   </table>
   ```

6. **JavaScript Functions:**
   ```javascript
   // Load available date range
   async function loadDateRangeInfo() { }
   
   // Apply date filter
   async function applyDateFilter() { }
   
   // Load segment overview with selected dates
   async function loadSegmentOverview() { }
   
   // Load bundles for selected segment
   async function loadSegmentBundles() { }
   
   // Format product display (code + description)
   function formatProduct(code, description) { }
   ```

#### Test Cases:
- [ ] Date picker functionality
- [ ] Segment selector functionality
- [ ] Responsive design on mobile
- [ ] Cross-browser compatibility
- [ ] API integration testing
- [ ] Error handling and edge cases

---

## 📅 Implementation Sequence

### **Recommended Timeline:**

```
WEEK 1: BACKEND IMPLEMENTATION
├─ Day 1-2: PHASE 1 - Enhanced RFM
│  ├─ Add date filtering to db_utils.py
│  ├─ Implement quantile calculation
│  ├─ Create /calculate-rfm-advanced endpoint
│  └─ Test with sample data
│
├─ Day 3-4: PHASE 2 - Heuristic Naming
│  ├─ Add segment_label() function
│  ├─ Add segment_characteristics() function
│  ├─ Add segment_rules_text() function
│  ├─ Update /run-segmentation endpoint
│  └─ Test segmentation logic
│
└─ Day 5: PHASE 3 - Market Basket
   ├─ Add segment-specific basket analysis
   ├─ Improve product display formatting
   ├─ Add lift strength indicators
   └─ Performance optimization

WEEK 2: FEATURES & FRONTEND
├─ Day 1: PHASE 4 - Date Filtering
│  ├─ Add date parameters to all endpoints
│  ├─ Create /date-range-info endpoint
│  ├─ Add request models
│  └─ Test date range functionality
│
└─ Day 2-5: PHASE 5 - Frontend Updates
   ├─ Update marketing.html with new UI
   ├─ Implement date picker
   ├─ Add segment selector
   ├─ Create bundle display components
   ├─ Full integration testing
   └─ Documentation & cleanup
```

---

## 🧪 Testing Plan

### **Unit Tests:**
- [ ] RFM calculation accuracy
- [ ] Quantile computation
- [ ] Segment naming logic
- [ ] Product description formatting
- [ ] Lift strength indicators

### **Integration Tests:**
- [ ] API Gateway routing (`/api/gateway/marketing/*`)
- [ ] Direct API calls
- [ ] Database queries
- [ ] Date filtering across endpoints

### **UI Tests:**
- [ ] Date picker works correctly
- [ ] Segment selector updates bundles
- [ ] Responsive layout on mobile
- [ ] Error messages display properly
- [ ] Loading states work

### **Performance Tests:**
- [ ] RFM with full dataset: < 5 seconds
- [ ] Segmentation: < 8 seconds
- [ ] Market basket: < 10 seconds
- [ ] UI responsiveness: < 500ms

---

## ⚡ Performance Considerations

### **Optimization Strategies:**

| Issue | Current | Solution |
|-------|---------|----------|
| Market basket slow | Top 100 products | Cache results, background jobs |
| RFM recalculation | Every request | Cache for common date ranges |
| Segmentation heavy | Every request | Pre-compute and store in MongoDB |
| Large datasets | 530K+ transactions | Pagination, data sampling |

### **Caching Strategy:**
```python
from functools import lru_cache
from datetime import datetime

@lru_cache(maxsize=10)
def get_cached_rfm(start_date, end_date):
    """Cache RFM for 1 hour"""
    return calculate_rfm(start_date, end_date)
```

### **Database Indexes:**
```javascript
// MongoDB - Create indexes for performance
db.DSS.createIndex({ "InvoiceDate": 1 })
db.DSS.createIndex({ "CustomerID": 1 })
db.DSS.createIndex({ "StockCode": 1 })
```

---

## 📚 Expected Outcomes

After completing all 5 phases, you'll have:

✅ **Enhanced Marketing API** with all Streamlit features  
✅ **Modern Dashboard UI** matching Streamlit functionality  
✅ **Complete API Documentation** (FastAPI auto-generated)  
✅ **Comprehensive Test Suite** verifying all endpoints  
✅ **Performance Optimization** for production use  
✅ **Date Filtering** capabilities across all endpoints  
✅ **Production-Ready System** ready for deployment  

---

## 🎯 Quick Reference: File Changes

### **Files to Modify:**

| File | Changes |
|------|---------|
| `python-apis/db_utils.py` | Add date filtering function |
| `python-apis/marketing_api.py` | PHASE 1-4 implementations |
| `src/main/resources/templates/dashboard/marketing.html` | PHASE 5 UI updates |

### **New Functions to Add:**

| Function | File | Purpose |
|----------|------|---------|
| `filter_by_date_range()` | db_utils.py | Date range filtering |
| `calculate_quantiles()` | marketing_api.py | RFM quantiles |
| `segment_label()` | marketing_api.py | Heuristic naming (5 categories) |
| `segment_characteristics()` | marketing_api.py | Detailed descriptions |
| `segment_rules_text()` | marketing_api.py | Marketing recommendations |
| `get_lift_strength()` | marketing_api.py | Lift indicators |

### **New Endpoints to Create:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/date-range-info` | GET | Get min/max dates |
| `/calculate-rfm-advanced` | POST | Enhanced RFM with quantiles |
| `/segment-basket-analysis` | POST | Segment-specific basket analysis |

---

## 💡 Pro Tips

1. **Start Small:** Test each phase independently before moving to the next
2. **Use Postman:** Test all API endpoints with Postman before frontend integration
3. **Compare Output:** Run Streamlit and API side-by-side to verify results match
4. **Performance First:** Add caching/indexing early to prevent bottlenecks
5. **Document As You Go:** Keep API documentation updated with changes

---

## 📞 Support & Questions

For each phase implementation:
- Reference your original Streamlit code for logic verification
- Test with the same date ranges to ensure consistency
- Use `test_apis.py` to validate endpoints
- Check FastAPI auto-generated docs at `http://localhost:8003/docs`

---

**Last Updated:** November 4, 2025  
**Status:** Planning & Design Complete ✅ Ready for Implementation 🚀
