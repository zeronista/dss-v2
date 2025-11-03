"""
FastAPI Example - Inventory Service
Port: 8001
Member: 1
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

app = FastAPI(
    title="Inventory API",
    description="API for inventory management and prediction",
    version="1.0.0"
)

# CORS Configuration - REQUIRED
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Spring Boot URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ Request/Response Models ============

class StockPredictionRequest(BaseModel):
    product_id: str
    days_ahead: int = 7
    
class StockPredictionResponse(BaseModel):
    success: bool
    product_id: str
    predicted_stock: int
    recommendation: str
    message: str

class ReorderRequest(BaseModel):
    product_id: str
    quantity: int

# ============ REQUIRED: Health Check ============

@app.get("/health")
async def health_check():
    """Required health check endpoint for Spring Boot gateway"""
    return {
        "status": "healthy",
        "service": "inventory",
        "version": "1.0.0",
        "port": 8001
    }

# ============ Inventory Endpoints ============

@app.get("/")
async def root():
    return {
        "service": "Inventory API",
        "version": "1.0.0",
        "endpoints": ["/health", "/predict-stock", "/stats", "/low-stock", "/reorder"]
    }

@app.post("/predict-stock", response_model=StockPredictionResponse)
async def predict_stock(request: StockPredictionRequest):
    """
    Predict stock levels for a product
    Example call from Spring Boot: POST /api/gateway/inventory/predict-stock
    """
    try:
        # TODO: Replace with actual ML model prediction
        predicted_stock = 150  # Dummy prediction
        
        recommendation = "Reorder soon" if predicted_stock < 100 else "Stock sufficient"
        
        return {
            "success": True,
            "product_id": request.product_id,
            "predicted_stock": predicted_stock,
            "recommendation": recommendation,
            "message": f"Prediction for {request.days_ahead} days ahead"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_inventory_stats():
    """
    Get overall inventory statistics
    Example call: GET /api/gateway/inventory/stats
    """
    return {
        "success": True,
        "data": {
            "total_products": 3847,
            "total_value": 1250000,
            "low_stock_items": 127,
            "out_of_stock": 15,
            "avg_stock_level": 250
        }
    }

@app.get("/low-stock")
async def get_low_stock_items():
    """
    Get list of low stock items
    Example call: GET /api/gateway/inventory/low-stock
    """
    return {
        "success": True,
        "data": [
            {"product_id": "P001", "name": "Product A", "current_stock": 10, "min_stock": 50},
            {"product_id": "P002", "name": "Product B", "current_stock": 5, "min_stock": 30}
        ],
        "count": 2
    }

@app.post("/reorder")
async def create_reorder(request: ReorderRequest):
    """
    Create a reorder request
    Example call: POST /api/gateway/inventory/reorder
    """
    try:
        # TODO: Implement actual reorder logic
        return {
            "success": True,
            "message": f"Reorder created for {request.product_id}",
            "data": {
                "product_id": request.product_id,
                "quantity": request.quantity,
                "estimated_arrival": "7-10 days"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ Run Server ============

if __name__ == "__main__":
    print("🚀 Starting Inventory API on port 8001...")
    print("📝 Documentation: http://localhost:8001/docs")
    print("🔍 Health check: http://localhost:8001/health")
    uvicorn.run(app, host="0.0.0.0", port=8001)

