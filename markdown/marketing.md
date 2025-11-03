# 💖 Vai Trò: Marketing Manager

## I. Mục Tiêu & Nhiệm Vụ Chính
* [cite_start]**Mục tiêu:** Phân tích hành vi mua hàng (giỏ hàng), ước tính tác động doanh thu từ các chiến dịch, và tối ưu hóa thời điểm tiếp thị[cite: 57].
* [cite_start]**Chiều mô hình DSS:** Prescriptive (Chỉ định/Gợi ý)[cite: 169]. [cite_start]Đưa ra các khuyến nghị hành động cụ thể để tối đa hóa giá trị vòng đời khách hàng và doanh số[cite: 167, 170].

## II. Màn Hình & Chức Năng Chính
| Màn hình / Chức năng | Mô tả chi tiết | Quyền truy cập |
| :--- | :--- | :--- |
| **Customer Segmentation – Main Screen** | [cite_start]Màn hình chính để chạy phân khúc, xem đặc điểm cụm, và nhận gợi ý hành động/gói sản phẩm[cite: 71]. | [cite_start]**X** (Truy cập đầy đủ)[cite: 71]. |
| **Run Segmentation** | [cite_start]Cho phép chọn số lượng phân khúc (S=3–5) để chạy thuật toán K-Means trên điểm RFM[cite: 71, 175]. | [cite_start]**X**[cite: 71]. |
| **Segments Overview Cards** | [cite_start]Tổng quan về các phân khúc (ví dụ: Champions, Loyal, At-Risk) bao gồm kích thước và tổng giá trị (TotalValue)[cite: 71, 100]. | [cite_start]**X**[cite: 71]. |
| **Recommended Actions per Segment** | [cite_start]Gợi ý các chiến lược marketing (ví dụ: Ưu đãi VIP early access) được thiết kế riêng cho phân khúc được chọn[cite: 71, 100]. | [cite_start]**X**[cite: 71]. |
| **Recommended Product Bundles** | [cite_start]Liệt kê các gói sản phẩm (bundles) thường được mua cùng nhau dựa trên **Market Basket Analysis (Apriori)** theo phân khúc[cite: 71, 100]. | [cite_start]**X**[cite: 71]. |

## III. Dữ Liệu & Quy Trình Hoạt Động
### 1. Dữ liệu đầu vào & Mô hình
* [cite_start]**Dữ liệu nguồn:** Điểm RFM (Recency, Frequency, Monetary) của mỗi khách hàng và dữ liệu giao dịch chi tiết (InvoiceNo, StockCode)[cite: 174, 178].
* [cite_start]**Thuật toán:** **K-Means Clustering** trên điểm RFM (Bước 1: Phân khúc) và **Apriori Algorithm** (Market Basket Analysis) trên dữ liệu giao dịch theo từng phân khúc (Bước 2: Gợi ý)[cite: 175, 179].
* [cite_start]**Tham số:** Số lượng phân khúc khách hàng (S=3–5), Min support (cho Market Basket Analysis)[cite: 98].

### 2. Các bước tiến hành (Use Cases)
1.  [cite_start]**Phân khúc:** Chọn **Số lượng phân khúc** mong muốn và chạy K-Means[cite: 98, 175].
2.  [cite_start]**Đánh giá:** Xem **Tổng quan các Phân khúc** để hiểu kích thước và giá trị của từng cụm[cite: 99, 100].
3.  [cite_start]**Chiến lược hành động:** Chọn một phân khúc (ví dụ: Champions) và xem **Đặc điểm Phân khúc** (ví dụ: "Nhóm khách hàng VIP nhất của bạn!") cùng **Gợi ý Hành động Marketing** phù hợp[cite: 101, 99].
4.  [cite_start]**Tạo gói sản phẩm:** Xem **Gợi ý gói sản phẩm (Bundle)** dựa trên luật kết hợp (Association Rule) của phân khúc đó (ví dụ: mua 'Sản phẩm A' thường mua thêm 'Sản phẩm B')[cite: 99].

### 3. Chức năng hỗ trợ (Non-UI)
* [cite_start]**RFM Batch Builder:** Tính điểm R/F/M hàng ngày[cite: 74].
* [cite_start]**K-Means Trainer:** Huấn luyện/gán nhãn cụm theo tham số[cite: 74].
* [cite_start]**Segment Basket Miner:** Chạy Apriori để sinh rules + confidence cho bundles cho từng segment[cite: 74].
* [cite_start]**Audience Push API:** API đồng bộ danh sách khách theo segment sang công cụ marketing[cite: 74].