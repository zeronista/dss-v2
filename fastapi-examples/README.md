# FastAPI Examples for DSS System

## Quick Start

### 1. Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Run example service:
```bash
python inventory_api_example.py
```

### 3. Test:
```bash
# Health check
curl http://localhost:8001/health

# Get stats
curl http://localhost:8001/stats

# Predict stock
curl -X POST http://localhost:8001/predict-stock \
  -H "Content-Type: application/json" \
  -d '{"product_id": "P001", "days_ahead": 7}'
```

### 4. View auto-generated docs:
Open: http://localhost:8001/docs

## Port Assignment

- Member 1 (Inventory): Port 8001
- Member 2 (Marketing): Port 8002
- Member 3 (Sales): Port 8003
- Member 4 (Analytics): Port 8004

## Important Notes

1. **MUST have `/health` endpoint** - Spring Boot uses this to check if service is running
2. **Enable CORS** - Allow Spring Boot (localhost:8080) to call your API
3. **Use assigned port** - Don't change ports to avoid conflicts
4. **Standard response format** - Include `success` field in responses

