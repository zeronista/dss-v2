# INVENTORY API - FULL DATASET CONFIGURATION

## 📝 Tổng Quan Thay Đổi

Role **Inventory Manager** đã được cấu hình để sử dụng **FULL DATASET** (`online_retail.csv`) thay vì cleaned dataset. Điều này cho phép API phân tích chính xác return patterns và risk management.

## 🎯 Lý Do Sử Dụng Full Dataset

### Tại sao Inventory cần dữ liệu đầy đủ?

1. **Return Risk Analysis yêu cầu dữ liệu về returns/cancellations**
   - Các giao dịch bị hủy (InvoiceNo bắt đầu với 'C') là dữ liệu cốt lõi
   - Negative quantities cho biết sản phẩm bị trả lại
   - Customer return history là yếu tố quan trọng nhất trong risk scoring

2. **Khác biệt so với các role khác**
   - **Sales Manager**: Chỉ cần positive transactions để forecast doanh thu
   - **Marketing Manager**: Chỉ cần successful orders để phân tích customer behavior
   - **Admin**: Tổng quan dữ liệu cleaned
   - **Inventory Manager**: CẦN TẤT CẢ để quản lý rủi ro trả hàng

3. **Tính chính xác của Risk Scoring**
   - Customer return rate = (Số đơn bị trả / Tổng số đơn) × 100%
   - Product return rate = (Số lần sản phẩm bị trả / Tổng số lần bán) × 100%
   - ⚠️ Không thể tính được nếu chỉ có cleaned data!

## 📋 Chi Tiết Thay Đổi

### 1. File: `inventory_api.py`

#### A. Cấu hình nguồn dữ liệu (Lines 18-21)

**TRƯỚC:**
```python
CSV_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'online_retail_cleaned.csv')
PARQUET_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'online_retail_cleaned.parquet')
```

**SAU:**
```python
# Inventory Manager uses FULL dataset (online_retail.csv) to analyze returns and cancellations
CSV_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'online_retail.csv')
PARQUET_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'online_retail.parquet')
```

#### B. Hàm `get_local_transactions_df()` được cập nhật

**Thay đổi chính:**

1. **Không filter out cancelled/returned orders**
   - TRƯỚC: `df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)].copy()`
   - SAU: `df = df[df['InvoiceDate'].notna() & df['InvoiceNo'].notna()].copy()`

2. **Thêm các cột phân tích returns**
   ```python
   df['IsReturn'] = df['InvoiceNo'].astype(str).str.startswith('C')
   df['IsNegativeQty'] = df['Quantity'] < 0
   ```

3. **Logging chi tiết về returns**
   ```python
   returns_count = df['IsReturn'].sum()
   negative_qty_count = df['IsNegativeQty'].sum()
   print(f"   📊 Returns/Cancellations: {returns_count} ({returns_count/len(df)*100:.1f}%)")
   print(f"   📊 Negative Quantities: {negative_qty_count} ({negative_qty_count/len(df)*100:.1f}%)")
   ```

#### C. Endpoint `/calculate-risk-score` - Sử dụng dữ liệu thực

**Cải tiến:**
- Tính **actual customer return rate** từ history
  ```python
  total_customer_orders = customer_data['InvoiceNo'].nunique()
  returned_orders = customer_data[customer_data['IsReturn'] == True]['InvoiceNo'].nunique()
  customer_return_rate = (returned_orders / total_customer_orders * 100)
  ```

- Tính **actual product return rate**
  ```python
  total_product_orders = product_data['InvoiceNo'].nunique()
  returned_product_orders = product_data[product_data['IsReturn'] == True]['InvoiceNo'].nunique()
  product_return_rate = (returned_product_orders / total_product_orders * 100)
  ```

- Kết quả trả về bao gồm return rates trong message

#### D. Endpoint `/simulate-policy` - Dùng actual return history

**Thay đổi:**
- TRƯỚC: `risk_scores = np.random.beta(2, 5, len(df_sample)) * 100` (simulated)
- SAU: Tính risk score thực tế cho từng order dựa trên customer và product return history

#### E. Endpoint `/risk-distribution` - Phân tích thực tế

**Thêm thông tin:**
```python
"overall_return_rate": round(overall_return_rate, 2),
"total_orders_in_db": int(total_orders),
"total_returns_in_db": int(total_returns),
"data_source": "Full dataset (online_retail.csv) including returns"
```

#### F. Endpoint MỚI: `/return-statistics`

**Chức năng:**
- Thống kê tổng quan về returns và cancellations
- Top customers với nhiều returns nhất
- Top products bị trả lại nhiều nhất
- Monthly return trends
- Overall return rate của toàn hệ thống

**Output ví dụ:**
```json
{
  "overall_statistics": {
    "total_returns": 8905,
    "return_rate_percent": 16.54
  },
  "customer_statistics": {
    "customers_with_returns": 1203,
    "customer_return_rate_percent": 28.34
  },
  "top_returned_products": {...},
  "monthly_trends": {...}
}
```

### 2. File: `markdown/inventory.md`

**Thêm section mới:**

```markdown
### 0. Nguồn dữ liệu đặc biệt
> ⚠️ **LƯU Ý QUAN TRỌNG:** Role Inventory Manager sử dụng **FULL DATASET** 
> (`online_retail.csv`) bao gồm **TẤT CẢ giao dịch** (kể cả cancelled/returned orders)
> 
> **Dữ liệu bao gồm:**
> - ✅ Normal orders (positive quantities, normal InvoiceNo)
> - ✅ Cancelled/Returned orders (InvoiceNo starts with 'C')
> - ✅ Negative quantities (returns)
> - ✅ All customer return history
```

### 3. File: `test_inventory_full_dataset.py` (MỚI)

**Mục đích:** 
Script test để verify API đang sử dụng đúng full dataset

**Test cases:**
1. Health check - verify data source
2. Root endpoint - check service info
3. Return statistics - verify return data exists
4. Risk score calculation - test với real customer
5. Risk distribution - verify data source
6. Policy simulation - test threshold

## 🧪 Cách Test

### Bước 1: Khởi động API
```powershell
cd f:\FPT\S8\DSS301\G5-GP3\dss-v2\python-apis
python inventory_api.py
```

### Bước 2: Chạy test script
```powershell
# Trong terminal mới
python test_inventory_full_dataset.py
```

### Bước 3: Kiểm tra kết quả

**Dấu hiệu thành công:**
- ✅ Health check hiển thị "Full dataset (online_retail.csv)"
- ✅ Return statistics cho thấy có returns (total_returns > 0)
- ✅ Return rate > 0% (thường khoảng 15-20%)
- ✅ Risk score message bao gồm customer/product return rates
- ✅ Risk distribution có overall_return_rate field

**Dấu hiệu lỗi:**
- ❌ Data source vẫn là "cleaned"
- ❌ total_returns = 0
- ❌ Return rate = 0%
- ❌ Risk scores không realistic (quá cao hoặc quá thấp)

## 📊 So Sánh Với Các Role Khác

| Role | Dataset | Lý Do |
|------|---------|-------|
| **Sales Manager** | `online_retail_cleaned.csv` | Chỉ cần valid sales để forecast |
| **Marketing Manager** | `online_retail_cleaned.csv` | Phân tích successful customers |
| **Admin** | `online_retail_cleaned.csv` | Tổng quan hệ thống |
| **Inventory Manager** | `online_retail.csv` ✅ | **CẦN returns để risk analysis** |

## 🎯 Impact & Benefits

### 1. Tính chính xác cao hơn
- Risk scores phản ánh thực tế return behavior
- Customer/Product return rates dựa trên data thực

### 2. Insights sâu hơn
- Biết customers/products nào hay bị trả hàng
- Phân tích trends của returns theo thời gian
- Tối ưu policy dựa trên actual return rate

### 3. Decision making tốt hơn
- Threshold τ* được tối ưu dựa trên real data
- Policy simulation realistic hơn
- Expected profit calculation chính xác

## ⚠️ Lưu Ý Khi Sử Dụng

1. **Performance**: Full dataset lớn hơn → cần caching tốt
   - ✅ Đã implement caching với TTL 1 hour
   - ✅ Sử dụng pandas operations hiệu quả

2. **Data Quality**: Full dataset có thể chứa outliers
   - ✅ Có validation và error handling
   - ✅ Filter out completely invalid records

3. **Business Logic**: Phân biệt rõ returns vs normal orders
   - ✅ Có flags `IsReturn` và `IsNegativeQty`
   - ✅ Documentation rõ ràng về cách tính toán

## 📚 Tài Liệu Liên Quan

- `inventory_api.py` - Main API code
- `markdown/inventory.md` - Role documentation
- `test_inventory_full_dataset.py` - Test script
- `data/online_retail.csv` - Full dataset
- `data/online_retail_cleaned.csv` - Cleaned dataset (cho các role khác)

## ✅ Checklist

- [x] Cập nhật CSV_FILE và PARQUET_FILE paths
- [x] Sửa `get_local_transactions_df()` để giữ returns
- [x] Thêm `IsReturn` và `IsNegativeQty` flags
- [x] Cập nhật `/calculate-risk-score` để dùng actual data
- [x] Cập nhật `/simulate-policy` để dùng actual data
- [x] Cập nhật `/risk-distribution` để dùng actual data
- [x] Thêm endpoint `/return-statistics`
- [x] Cập nhật root endpoint với data source info
- [x] Cập nhật health check với data source
- [x] Cập nhật documentation (inventory.md)
- [x] Tạo test script
- [x] Tạo summary document (file này)

---

**Ngày cập nhật:** 2025-01-04
**Người thực hiện:** GitHub Copilot
**Status:** ✅ COMPLETED
