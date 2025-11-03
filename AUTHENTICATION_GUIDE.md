# 🔐 Hướng dẫn Đăng nhập và Phân quyền - DSS System

## 📋 Tổng quan

Hệ thống DSS đã được tích hợp với Spring Security để quản lý đăng nhập và phân quyền theo role người dùng.

## 👥 Các Role trong hệ thống

### 1. **Admin/Director** (ADMIN)
- Quyền cao nhất trong hệ thống
- Quản lý toàn bộ hệ thống
- Truy cập: `/admin/dashboard`

### 2. **Inventory Manager** (INVENTORY_MANAGER)
- Quản lý kho hàng và tồn kho
- Theo dõi nhập xuất hàng
- Truy cập: `/inventory/dashboard`

### 3. **Marketing Manager** (MARKETING_MANAGER)
- Quản lý chiến dịch marketing
- Phân tích khách hàng
- Truy cập: `/marketing/dashboard`

### 4. **Sales Manager** (SALES_MANAGER)
- Quản lý doanh số bán hàng
- Theo dõi target và deals
- Truy cập: `/sales/dashboard`

## 🔑 Tài khoản Demo

Hệ thống tự động tạo các tài khoản demo khi khởi động lần đầu:

| Role | Username | Password | Dashboard |
|------|----------|----------|-----------|
| Admin/Director | `admin` | `admin123` | `/admin/dashboard` |
| Inventory Manager | `inventory` | `inventory123` | `/inventory/dashboard` |
| Marketing Manager | `marketing` | `marketing123` | `/marketing/dashboard` |
| Sales Manager | `sales` | `sales123` | `/sales/dashboard` |

## 🚀 Cách sử dụng

### 1. Khởi động ứng dụng

```bash
mvn spring-boot:run
```

### 2. Truy cập trang đăng nhập

Mở trình duyệt và truy cập: **http://localhost:8080**

Bạn sẽ tự động được chuyển đến trang login.

### 3. Đăng nhập

- Nhập username và password từ bảng tài khoản demo ở trên
- Click "Sign In"
- Hệ thống sẽ tự động chuyển bạn đến dashboard tương ứng với role

### 4. Đăng xuất

Click nút "Logout" ở góc trên bên phải của navbar.

## 🔒 Bảo mật

### Password Encryption
- Tất cả password được mã hóa bằng BCrypt
- Không lưu password dạng plain text

### Session Management
- Session tự động invalidate khi logout
- Cookie JSESSIONID được xóa khi logout

### Access Control
- Mỗi role chỉ có thể truy cập các endpoint được phép
- Unauthorized access sẽ bị từ chối (403 Forbidden)

## 📁 Cấu trúc Code

```
src/main/java/com/group5/dss/
├── config/
│   ├── SecurityConfig.java          # Cấu hình Spring Security
│   └── DataInitializer.java         # Khởi tạo dữ liệu user mẫu
├── controller/
│   ├── AuthController.java          # Xử lý login/logout
│   └── InvoiceController.java       # Xử lý invoice
├── model/
│   ├── User.java                    # Model User
│   ├── Role.java                    # Enum Role
│   └── Invoice.java                 # Model Invoice
├── repository/
│   ├── UserRepository.java          # Repository cho User
│   └── InvoiceRepository.java       # Repository cho Invoice
└── service/
    ├── UserService.java             # Service quản lý User
    ├── CustomUserDetailsService.java # UserDetailsService cho Spring Security
    └── InvoiceService.java          # Service quản lý Invoice
```

## 🎨 Templates

```
src/main/resources/templates/
├── login.html                       # Trang đăng nhập
├── invoices.html                    # Trang xem invoices
└── dashboard/
    ├── admin.html                   # Dashboard Admin
    ├── inventory.html               # Dashboard Inventory Manager
    ├── marketing.html               # Dashboard Marketing Manager
    └── sales.html                   # Dashboard Sales Manager
```

## ⚙️ Tùy chỉnh

### Thêm User mới

Sử dụng `UserService.createUser()`:

```java
userService.createUser("newuser", "password123", "Full Name", "email@example.com", Role.ADMIN);
```

### Thêm Role mới

1. Thêm role vào enum `Role.java`
2. Cập nhật `SecurityConfig.java` để thêm access control
3. Tạo dashboard template mới
4. Thêm route trong `AuthController.java`

## 🐛 Troubleshooting

### Không đăng nhập được
- Kiểm tra username/password có đúng không
- Xem console log để biết lỗi cụ thể

### 403 Forbidden
- Bạn đang cố truy cập endpoint không có quyền
- Đăng nhập với user có role phù hợp

### Users không được tạo tự động
- Kiểm tra MongoDB connection
- Xem log startup có lỗi không

## 📞 Liên hệ

Nếu có vấn đề, vui lòng liên hệ team phát triển.

