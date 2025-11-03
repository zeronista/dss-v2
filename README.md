# 🎯 DSS v2 - Decision Support System

Decision Support System based on online retail dataset with integrated FastAPI microservices architecture.

## 🏗️ Architecture

```
Spring Boot (Port 8080) - API Gateway + Frontend
    │
    ├── MongoDB - Data Storage
    ├── FastAPI 1 (Port 8001) - Inventory Management
    ├── FastAPI 2 (Port 8002) - Marketing Analytics
    ├── FastAPI 3 (Port 8003) - Sales Forecasting
    └── FastAPI 4 (Port 8004) - Advanced Analytics
```

## ✨ Features

- 🔐 **Role-based Authentication** - Admin, Inventory Manager, Marketing Manager, Sales Manager
- 📊 **Data Visualization** - Invoice management with pagination
- 🌐 **API Gateway** - Centralized routing to microservices
- 🐍 **FastAPI Integration** - Python ML/AI services
- 🎨 **Modern UI** - Responsive dashboards for each role
- 🔒 **Spring Security** - Secure authentication & authorization

## 🚀 Quick Start

### 1. Run Spring Boot Application
```bash
mvn spring-boot:run
```
Access: http://localhost:8080

### 2. (Optional) Run FastAPI Services
```bash
cd fastapi-examples
pip install -r requirements.txt
python inventory_api_example.py
```

## 🔑 Demo Accounts

| Role | Username | Password |
|------|----------|----------|
| Admin/Director | `admin` | `admin123` |
| Inventory Manager | `inventory` | `inventory123` |
| Marketing Manager | `marketing` | `marketing123` |
| Sales Manager | `sales` | `sales123` |

## 📚 Documentation

- **[AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md)** - Login & Authorization guide
- **[FASTAPI_INTEGRATION_GUIDE.md](FASTAPI_INTEGRATION_GUIDE.md)** - FastAPI integration for developers
- **[API_GATEWAY_SUMMARY.md](API_GATEWAY_SUMMARY.md)** - API Gateway overview
- **[fastapi-examples/](fastapi-examples/)** - FastAPI service templates

## 🛠️ Tech Stack

- **Backend:** Spring Boot 3.5.7, Spring Security, Spring Data MongoDB
- **Frontend:** Thymeleaf, HTML5, CSS3, JavaScript
- **Database:** MongoDB Atlas
- **API Gateway:** RestTemplate
- **External Services:** FastAPI (Python)

## 📋 API Endpoints

### Authentication
- `POST /perform_login` - Login
- `POST /logout` - Logout
- `GET /dashboard` - Main dashboard (redirects by role)

### API Gateway
- `GET /api/gateway/health` - Check all services status
- `POST /api/gateway/inventory/*` - Inventory APIs
- `POST /api/gateway/marketing/*` - Marketing APIs
- `POST /api/gateway/sales/*` - Sales APIs
- `POST /api/gateway/analytics/*` - Analytics APIs

### Data Management
- `GET /invoices?page={n}&size={m}` - View invoices with pagination

## 🎨 Screenshots

### Login Page
Modern gradient design with role-based access

### Admin Dashboard
- Total revenue tracking
- Order statistics
- User management
- System settings

### Role-specific Dashboards
Each role has custom dashboard with relevant metrics and quick actions

## 🔧 Configuration

Edit `src/main/resources/application.properties`:

```properties
# MongoDB
spring.data.mongodb.uri=your_mongodb_uri
spring.data.mongodb.database=DSS

# FastAPI Services
api.inventory.url=http://localhost:8001
api.marketing.url=http://localhost:8002
api.sales.url=http://localhost:8003
api.analytics.url=http://localhost:8004
```

## 👥 Team Structure

- **Member 1:** Inventory API (Port 8001) - Stock prediction, reorder management
- **Member 2:** Marketing API (Port 8002) - Customer analytics, recommendations
- **Member 3:** Sales API (Port 8003) - Sales forecasting, target tracking
- **Member 4:** Analytics API (Port 8004) - Advanced data analytics

## 🐛 Troubleshooting

### Cannot login
- Check MongoDB connection
- Verify user credentials
- Check console logs

### API returns 404
- Verify FastAPI service is running
- Check port configuration
- Test `/health` endpoint

### CORS errors
- Verify CORS configuration in FastAPI
- Check allowed origins

## 📞 Support

For issues and questions:
1. Check documentation files
2. Review console logs
3. Test health endpoints
4. Contact team lead

## 📄 License

This project is for educational purposes.

---

**Version:** 2.0.0  
**Last Updated:** November 3, 2025  
**Status:** ✅ Production Ready
