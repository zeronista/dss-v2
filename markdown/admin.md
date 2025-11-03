# 📈 Vai Trò: Admin / Director

## I. Mục Tiêu & Nhiệm Vụ Chính
* [cite_start]**Mục tiêu:** Giám sát tổng thể hiệu suất kinh doanh, dự báo doanh thu, phân khúc khách hàng và quản lý người dùng hệ thống[cite: 55].
* [cite_start]**Chiều mô hình DSS:** Descriptive (Mô tả)[cite: 136]. [cite_start]Cung cấp bức tranh mô tả doanh thu để nhà quản trị nhận diện tháng cao/thấp điểm và ưu tiên nguồn lực[cite: 131, 132, 133].

## II. Màn Hình & Chức Năng Chính
| Màn hình / Chức năng | Mô tả chi tiết | Quyền truy cập |
| :--- | :--- | :--- |
| **Sales Overview – Main Screen** | [cite_start]Bảng điều khiển chính, xem các KPI, xu hướng doanh thu theo tháng, và xếp hạng Top N quốc gia/sản phẩm[cite: 71]. | [cite_start]**X** (Truy cập đầy đủ)[cite: 71]. |
| **Apply Filters** | [cite_start]Áp dụng bộ lọc Date Range, Country (Multi-select), Top-N (5-50), và Exclude cancellations[cite: 71, 79]. | [cite_start]**X**[cite: 71]. |
| **View KPI Cards** | [cite_start]Xem Tổng doanh thu (Total Revenue), Số quốc gia active (#Countries active), %Share Top-N Countries/SKUs[cite: 71, 82]. | [cite_start]**X**[cite: 71]. |
| **View Monthly Trend & Ranking** | [cite_start]Xem biểu đồ xu hướng doanh thu theo tháng (Line Chart) và Top-N Countries/SKUs (Bar Chart)[cite: 71, 82]. | [cite_start]**X**[cite: 71]. |
| **Drill-down & Export** | [cite_start]Click vào 1 bar/nhãn để lọc toàn bộ dashboard theo Country/SKU[cite: 67]. [cite_start]Xuất bảng xếp hạng (Country/SKU Ranking) và Monthly Trend ra CSV/XLSX[cite: 67, 82]. | [cite_start]**X**[cite: 71]. |

## III. Dữ Liệu & Quy Trình Hoạt Động
### 1. Dữ liệu đầu vào
* [cite_start]**Dữ liệu nguồn:** Dữ liệu giao dịch lịch sử từ file `online_retail.csv`[cite: 51, 117].
* [cite_start]**Bộ lọc chính:** Khoảng thời gian (Date Range), Quốc gia (Country filter), Top-N, Loại invoice hủy (Exclude cancellations)[cite: 79].

### 2. Các bước tiến hành (Use Cases)
1.  [cite_start]**Thiết lập tham số:** Sử dụng **Apply Filters** để chọn khoảng thời gian và số lượng Top-N muốn phân tích[cite: 67].
2.  [cite_start]**Giám sát tổng thể:** Xem **KPI Cards** (Total Revenue, %Share Top-N) để nắm bắt hiệu suất nhanh[cite: 67].
3.  [cite_start]**Phân tích sâu:** Xem biểu đồ **Monthly Revenue Trend** (MoM%) để phát hiện mùa vụ/biến động[cite: 67].
4.  [cite_start]**Xác định ưu tiên:** Xem xếp hạng **Top-N Countries/SKUs**[cite: 67]. [cite_start]Sử dụng tính năng **Drill-down** (click vào 1 bar/nhãn) để lọc dashboard theo Country/SKU cụ thể[cite: 67].
5.  [cite_start]**Báo cáo:** Xuất bảng xếp hạng và trend dưới dạng **CSV/XLSX** để báo cáo[cite: 67].

### 3. Chức năng hỗ trợ (Non-UI)
* [cite_start]**Nightly ETL – Revenue Fact Build:** Job gom dữ liệu giao dịch, chuẩn hóa, tính Revenue, tạo bảng fact theo YearMonth/Country/SKU[cite: 74].
* [cite_start]**Country & SKU Ranking Precompute:** Batch xếp hạng Top-N Country/SKU và tính %Share để UI tải nhanh[cite: 74].
* [cite_start]**MoM Trend Cache Warmer:** Chạy trước các truy vấn chuỗi thời gian để giảm thời gian tải (TTFB)[cite: 74].