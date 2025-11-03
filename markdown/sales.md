# 🛍️ Vai Trò: Sales Manager

## I. Mục Tiêu & Nhiệm Vụ Chính
* **Mục tiêu:** Chịu trách nhiệm gia tăng doanh số và tối ưu hóa chiến lược bán hàng. [cite_start]Sử dụng hệ thống để phân tích cơ hội bán chéo (cross-sell), xây dựng chiến lược gói sản phẩm, và cá nhân hóa đề xuất sản phẩm[cite: 60, 184].
* [cite_start]**Chiều mô hình DSS:** Prediction (Dự đoán)[cite: 188]. [cite_start]Gợi ý Top-N sản phẩm/nhóm mà khách hàng có khả năng mua tiếp theo, nhằm tăng giá trị đơn hàng trung bình (AOV)[cite: 183].

## II. Màn Hình & Chức Năng Chính
| Màn hình / Chức năng | Mô tả chi tiết | Quyền truy cập |
| :--- | :--- | :--- |
| **Cross-sell & NBO – Main Screen** | [cite_start]Màn hình chính để tạo đề xuất bán chéo (cross-sell) và sản phẩm tiếp theo tốt nhất (Next-Best-Offer)[cite: 71]. | [cite_start]**X** (Truy cập đầy đủ)[cite: 71]. |
| **Recommendation Parameters** | [cite_start]Các tham số đầu vào: **Product Search** (bắt buộc), **Customer ID** (Tùy chọn), **Confidence Threshold** (Slider 0.1–1.0), **Top N Recommendations** (Dropdown)[cite: 106]. | [cite_start]**X**[cite: 71]. |
| **Bảng Đề xuất Sản phẩm** | [cite_start]Hiển thị Top N sản phẩm được đề xuất, kèm các chỉ số **Support**, **Confidence**, **Lift**, và **Expected Impact** (Doanh thu ước tính)[cite: 109]. | [cite_start]**X**[cite: 71]. |
| **Trực quan hóa Mạng Kết hợp** | [cite_start]Sơ đồ mạng lưới (Network Graph) hiển thị mối quan hệ giữa sản phẩm nguồn và các sản phẩm đề xuất[cite: 109]. | [cite_start]**X**[cite: 71]. |
| **Customer Segment Info Panel** | (Chỉ hiển thị khi có Customer ID) [cite_start]Thông tin phân khúc khách hàng (RFM) để cá nhân hóa đề xuất[cite: 71, 109]. | [cite_start]**X**[cite: 71]. |

## III. Dữ Liệu & Quy Trình Hoạt Động
### 1. Dữ liệu đầu vào & Mô hình
* [cite_start]**Dữ liệu nguồn:** Dữ liệu giao dịch hợp lệ (đã lọc bỏ đơn hủy, Quantity/UnitPrice > 0)[cite: 192].
* [cite_start]**Thuật toán:** **Association Rules Mining (Apriori)** để phát hiện các mẫu mua chung[cite: 197].
* [cite_start]**Chỉ số đầu ra:** **Support**, **Confidence**, **Lift**[cite: 198, 199, 200].
* [cite_start]**Xếp hạng:** Top N đề xuất được xếp hạng theo điểm (**Confidence $\times$ Lift**)[cite: 201].

### 2. Các bước tiến hành (Use Cases)
1.  **Thiết lập:** Nhập **Mã sản phẩm** muốn tìm cơ hội bán kèm. [cite_start]Tùy chọn nhập **Mã Khách hàng** để cá nhân hóa đề xuất theo RFM segment[cite: 106, 202].
2.  [cite_start]**Điều chỉnh tham số:** Kéo thanh trượt **Confidence Threshold** và chọn **Top N Recommendations**[cite: 106].
3.  [cite_start]**Tạo đề xuất:** Nhấn nút **"Generate Recommendations"**[cite: 106].
4.  [cite_start]**Phân tích kết quả:** Xem **Bảng Đề xuất Sản phẩm** để đánh giá chỉ số và xem **Estimated Impact**[cite: 109].
5.  [cite_start]**Chiến lược:** Đọc **Cross-sell Strategy Insights** để nhận gợi ý về **Bundle Opportunity** và **Timing Strategy**[cite: 112].

### 3. Chức năng hỗ trợ (Non-UI)
* [cite_start]**Basket Builder:** Gom giao dịch theo InvoiceNo thành giỏ hàng hàng giờ[cite: 74].
* [cite_start]**Assoc-Rules Miner (FPGrowth):** Pipeline tính Support/Confidence/Lift, lưu rules theo phiên bản và theo RFM segment[cite: 74].
* [cite_start]**Recommendation API:** API trả Top-N đề xuất, tôn trọng ngưỡng confidence & bộ lọc[cite: 74].
* [cite_start]**Inventory/OOS Sync:** Đồng bộ tồn kho để loại bỏ sản phẩm hết hàng khỏi đề xuất[cite: 74].