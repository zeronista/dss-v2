# 📦 Vai Trò: Inventory Manager

## I. Mục Tiêu & Nhiệm Vụ Chính
* [cite_start]**Mục tiêu:** Đảm bảo chất lượng dữ liệu, phát hiện giao dịch bất thường, và mô phỏng chính sách kiểm soát rủi ro (ví dụ: trả hàng)[cite: 56].
* [cite_start]**Chiều mô hình DSS:** Prescriptive (Chỉ định/Gợi ý)[cite: 151, 154]. [cite_start]Hỗ trợ thiết lập chính sách tối ưu cho các đơn hàng có rủi ro trả hàng cao bằng phương pháp **Mô phỏng (Simulation)**[cite: 152, 155].

## II. Màn Hình & Chức Năng Chính
| Màn hình / Chức năng | Mô tả chi tiết | Quyền truy cập |
| :--- | :--- | :--- |
| **Return-Risk Gatekeeping – Main Screen** | [cite_start]Màn hình mô phỏng chính sách kiểm soát rủi ro trả hàng để tối đa hóa lợi nhuận kỳ vọng[cite: 71, 149]. | [cite_start]**X** (Truy cập đầy đủ)[cite: 71]. |
| **Input Tham số mô phỏng** | [cite_start]Nhập **Chi phí xử lý trả hàng** (ReturnProcessingCost) và **Tỷ lệ ảnh hưởng chuyển đổi** (ConversionRate\_impact)[cite: 89]. | [cite_start]**X**[cite: 71]. |
| **Ngưỡng rủi ro ($\tau$) - Slider** | Công cụ tương tác chính. [cite_start]Kéo thanh trượt (0-100) để thiết lập ngưỡng rủi ro và xem kết quả cập nhật theo thời gian thực[cite: 89]. | [cite_start]**X**[cite: 71]. |
| **Biểu đồ Lợi nhuận kỳ vọng** | Trục hoành là $\tau$, trục tung là Tổng lợi nhuận kỳ vọng. [cite_start]Cho thấy lợi nhuận thay đổi khi siết chặt/nới lỏng chính sách[cite: 92]. | [cite_start]**X**[cite: 71]. |
| **Đề xuất của hệ thống** | [cite_start]Thẻ KPI hiển thị **Ngưỡng tối ưu đề xuất ($\tau^*$)** mang lại tổng lợi nhuận kỳ vọng cao nhất[cite: 71, 92, 162]. | [cite_start]**X**[cite: 71]. |
| **Deploy Policy** | [cite_start]Nút nhấn để áp dụng ngưỡng $\tau$ đã chọn vào hệ thống vận hành thực tế[cite: 71, 95]. | [cite_start]**X**[cite: 71]. |

## III. Dữ Liệu & Quy Trình Hoạt Động

### 0. Nguồn dữ liệu đặc biệt
> ⚠️ **LƯU Ý QUAN TRỌNG:** Role Inventory Manager sử dụng **FULL DATASET** (`online_retail.csv`) bao gồm **TẤT CẢ giao dịch** (kể cả cancelled/returned orders - InvoiceNo bắt đầu bằng 'C').
> 
> **Lý do:**
> - Để phân tích chính xác return patterns và risk scoring
> - Các giao dịch cancelled/returned là dữ liệu cốt lõi cho return risk management
> - Khác với các role khác (Sales, Marketing, Admin) chỉ dùng cleaned dataset
> 
> **Dữ liệu bao gồm:**
> - ✅ Normal orders (positive quantities, normal InvoiceNo)
> - ✅ Cancelled/Returned orders (InvoiceNo starts with 'C')
> - ✅ Negative quantities (returns)
> - ✅ All customer return history

### 1. Dữ liệu đầu vào & Mô hình
* [cite_start]**Dữ liệu nguồn:** Điểm rủi ro (Return\_Risk\_Score) của đơn hàng, chi phí xử lý trả hàng, tỷ lệ ảnh hưởng chuyển đổi[cite: 89, 157].
* [cite_start]**Mô hình chính:** Mô hình tính toán **Expected Profit** (Lợi nhuận kỳ vọng) theo công thức mô phỏng[cite: 160, 161].
* **Chính sách:**
    * [cite_start]Nếu $Risk\_Score < \tau$ (cho qua): $Expected\_Profit = (Revenue - Costs) - (Risk\_Score \times ReturnCost)$[cite: 160].
    * [cite_start]Nếu $Risk\_Score \ge \tau$ (áp dụng chính sách): $Expected\_Profit = (Revenue - Costs) \times (1 - ConversionRate\_impact)$[cite: 161].

### 2. Các bước tiến hành (Use Cases)
1.  [cite_start]**Tính điểm rủi ro:** Hệ thống tính **Return\_Risk\_Score** (0-100) cho đơn hàng dựa trên đặc trưng KH/SKU/đơn[cite: 157].
2.  [cite_start]**Thiết lập tham số:** Nhập **Chi phí xử lý trả hàng** và **Tỷ lệ ảnh hưởng chuyển đổi** để chuẩn bị mô phỏng[cite: 89].
3.  [cite_start]**Mô phỏng "What-if":** Kéo **Thanh trượt $\tau$** để thay đổi chính sách (ví dụ: $Risk\_Score \ge \tau \to Block COD Payment$)[cite: 89, 95].
4.  [cite_start]**Phân tích kết quả:** Xem **Biểu đồ Lợi nhuận kỳ vọng** để tìm điểm tối đa và xem **$\tau^*$ Đề xuất** của hệ thống[cite: 92].
5.  [cite_start]**Áp dụng:** Nhấn nút **"Triển khai chính sách"** để đồng bộ rule vào hệ thống vận hành[cite: 95].

### 3. Chức năng hỗ trợ (Non-UI)
* [cite_start]**Real-time Risk Scoring API:** Dịch vụ tính điểm rủi ro cho đơn mới[cite: 74].
* [cite_start]**Threshold Optimizer (Grid Search):** Batch mô phỏng “what-if” trên lưới $\tau$, tính Total Expected Profit và ghi nhận $\tau^*$ khuyến nghị[cite: 74].
* [cite_start]**Policy Deployment Service:** Service sinh rule và đồng bộ vào Order/Payment gateway[cite: 74].
* [cite_start]**Backtest Simulator:** Chạy lại dữ liệu lịch sử để ước tính lợi nhuận/coverage nếu áp dụng chính sách hiện hành[cite: 74].