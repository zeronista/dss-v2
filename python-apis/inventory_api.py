"""
FastAPI - Inventory Manager API
Port: 8002
Role: Return Risk Management & Policy Simulation (Prescriptive DSS)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime

# Import database utilities
from db_utils import get_transactions_df, get_db

app = FastAPI(
    title="Inventory API - Return Risk Management",
    description="Return risk scoring, policy simulation, and expected profit optimization",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ Request/Response Models ============

class RiskScoreRequest(BaseModel):
    customer_id: str
    stock_code: str
    quantity: int
    unit_price: float
    country: Optional[str] = "Unknown"

class RiskScoreResponse(BaseModel):
    success: bool
    customer_id: str
    stock_code: str
    risk_score: float  # 0-100
    risk_level: str  # Low, Medium, High
    message: str

class PolicySimulationRequest(BaseModel):
    threshold_tau: float = Field(..., ge=0, le=100, description="Risk threshold (0-100)")
    return_processing_cost: float = Field(10.0, description="Cost to process returns")
    conversion_impact: float = Field(0.2, ge=0, le=1, description="Impact on conversion rate (0-1)")
    sample_size: Optional[int] = Field(1000, description="Number of orders to simulate")

class PolicySimulationResponse(BaseModel):
    success: bool
    threshold_tau: float
    total_expected_profit: float
    orders_blocked: int
    orders_allowed: int
    avg_risk_blocked: float
    avg_risk_allowed: float
    recommendation: str

class OptimalThresholdResponse(BaseModel):
    success: bool
    optimal_tau: float
    max_expected_profit: float
    orders_blocked_at_optimal: int
    simulation_results: List[Dict[str, Any]]

# ============ Health Check ============

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "inventory",
        "version": "1.0.0",
        "port": 8002
    }

# ============ Inventory Endpoints ============

@app.get("/")
async def root():
    return {
        "service": "Inventory API - Return Risk Management",
        "version": "1.0.0",
        "role": "Inventory Manager",
        "dss_type": "Prescriptive",
        "endpoints": [
            "/health",
            "/calculate-risk-score",
            "/simulate-policy",
            "/find-optimal-threshold",
            "/risk-distribution"
        ]
    }

@app.post("/calculate-risk-score", response_model=RiskScoreResponse)
async def calculate_risk_score(request: RiskScoreRequest):
    """
    Calculate return risk score for a single order
    Risk Score = weighted combination of:
    - Customer history (return rate)
    - Product return rate
    - Order value
    - Quantity anomaly
    """
    try:
        df = get_transactions_df()
        
        if df.empty:
            # Default risk score if no data
            risk_score = 50.0
        else:
            # Calculate customer return rate
            customer_data = df[df['CustomerID'] == request.customer_id]
            if not customer_data.empty:
                # Check for cancelled invoices (starts with 'C')
                all_customer_invoices = customer_data['InvoiceNo'].nunique()
                # Get all invoices including cancelled ones
                df_all = get_transactions_df(exclude_cancelled=False)
                cancelled = df_all[
                    (df_all['CustomerID'] == request.customer_id) & 
                    (df_all['InvoiceNo'].str.startswith('C', na=False))
                ]['InvoiceNo'].nunique()
                customer_return_rate = (cancelled / all_customer_invoices * 100) if all_customer_invoices > 0 else 0
            else:
                customer_return_rate = 30.0  # Default for new customers
            
            # Calculate product return rate
            product_data = df[df['StockCode'] == request.stock_code]
            if not product_data.empty:
                df_all = get_transactions_df(exclude_cancelled=False)
                product_invoices = product_data['InvoiceNo'].nunique()
                product_cancelled = df_all[
                    (df_all['StockCode'] == request.stock_code) & 
                    (df_all['InvoiceNo'].str.startswith('C', na=False))
                ]['InvoiceNo'].nunique()
                product_return_rate = (product_cancelled / product_invoices * 100) if product_invoices > 0 else 0
            else:
                product_return_rate = 20.0  # Default for new products
            
            # Quantity anomaly (high quantity = higher risk)
            avg_quantity = df['Quantity'].mean()
            quantity_risk = min(100, (request.quantity / avg_quantity) * 30)
            
            # Order value risk (very high or very low values are risky)
            order_value = request.quantity * request.unit_price
            avg_order_value = (df['Revenue']).mean()
            value_deviation = abs(order_value - avg_order_value) / avg_order_value if avg_order_value > 0 else 0
            value_risk = min(100, value_deviation * 50)
            
            # Weighted risk score
            risk_score = (
                customer_return_rate * 0.4 +
                product_return_rate * 0.3 +
                quantity_risk * 0.2 +
                value_risk * 0.1
            )
            risk_score = max(0, min(100, risk_score))  # Clamp to 0-100
        
        # Determine risk level
        if risk_score < 33:
            risk_level = "Low"
        elif risk_score < 67:
            risk_level = "Medium"
        else:
            risk_level = "High"
        
        return {
            "success": True,
            "customer_id": request.customer_id,
            "stock_code": request.stock_code,
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "message": f"Risk assessment completed. Score: {risk_score:.2f}/100"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating risk: {str(e)}")

@app.post("/simulate-policy", response_model=PolicySimulationResponse)
async def simulate_policy(request: PolicySimulationRequest):
    """
    Simulate policy with given threshold (tau)
    - Orders with Risk >= tau: Apply policy (e.g., block COD, require prepayment)
    - Orders with Risk < tau: Allow normally
    """
    try:
        df = get_transactions_df()
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No transaction data found")
        
        # Sample orders for simulation
        if len(df) > request.sample_size:
            df_sample = df.sample(n=request.sample_size, random_state=42)
        else:
            df_sample = df.copy()
        
        # Calculate risk scores for all orders (simplified for simulation)
        # In production, this would use the calculate_risk_score function
        np.random.seed(42)
        df_sample['RiskScore'] = np.random.beta(2, 5, len(df_sample)) * 100  # Beta distribution 0-100
        
        # Apply policy simulation
        df_sample['Blocked'] = df_sample['RiskScore'] >= request.threshold_tau
        
        # Calculate expected profit
        def calc_expected_profit(row):
            revenue = row['Revenue']
            costs = revenue * 0.3  # Assume 30% cost
            base_profit = revenue - costs
            
            if row['Blocked']:
                # Apply conversion impact
                return base_profit * (1 - request.conversion_impact)
            else:
                # Allow but account for return risk
                return_cost = row['RiskScore'] / 100 * request.return_processing_cost
                return base_profit - return_cost
        
        df_sample['ExpectedProfit'] = df_sample.apply(calc_expected_profit, axis=1)
        
        # Aggregate results
        total_profit = df_sample['ExpectedProfit'].sum()
        orders_blocked = df_sample['Blocked'].sum()
        orders_allowed = len(df_sample) - orders_blocked
        
        avg_risk_blocked = df_sample[df_sample['Blocked']]['RiskScore'].mean() if orders_blocked > 0 else 0
        avg_risk_allowed = df_sample[~df_sample['Blocked']]['RiskScore'].mean() if orders_allowed > 0 else 0
        
        # Generate recommendation
        if request.threshold_tau < 20:
            recommendation = "Very lenient policy - Low protection against returns"
        elif request.threshold_tau < 40:
            recommendation = "Balanced policy - Moderate risk management"
        elif request.threshold_tau < 60:
            recommendation = "Strict policy - Good protection but may impact conversion"
        else:
            recommendation = "Very strict policy - High protection but significant conversion impact"
        
        return {
            "success": True,
            "threshold_tau": request.threshold_tau,
            "total_expected_profit": round(total_profit, 2),
            "orders_blocked": int(orders_blocked),
            "orders_allowed": int(orders_allowed),
            "avg_risk_blocked": round(avg_risk_blocked, 2),
            "avg_risk_allowed": round(avg_risk_allowed, 2),
            "recommendation": recommendation
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error simulating policy: {str(e)}")

@app.post("/find-optimal-threshold", response_model=OptimalThresholdResponse)
async def find_optimal_threshold(
    return_processing_cost: float = 10.0,
    conversion_impact: float = 0.2,
    sample_size: int = 1000
):
    """
    Find optimal threshold (tau*) that maximizes expected profit
    Uses grid search across tau values from 0 to 100
    """
    try:
        # Grid search parameters
        tau_values = list(range(0, 101, 5))  # 0, 5, 10, ..., 100
        results = []
        
        for tau in tau_values:
            sim_request = PolicySimulationRequest(
                threshold_tau=tau,
                return_processing_cost=return_processing_cost,
                conversion_impact=conversion_impact,
                sample_size=sample_size
            )
            
            sim_result = await simulate_policy(sim_request)
            
            results.append({
                "tau": tau,
                "expected_profit": sim_result.total_expected_profit,
                "orders_blocked": sim_result.orders_blocked,
                "orders_allowed": sim_result.orders_allowed
            })
        
        # Find optimal tau
        optimal_result = max(results, key=lambda x: x['expected_profit'])
        
        return {
            "success": True,
            "optimal_tau": optimal_result['tau'],
            "max_expected_profit": round(optimal_result['expected_profit'], 2),
            "orders_blocked_at_optimal": optimal_result['orders_blocked'],
            "simulation_results": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding optimal threshold: {str(e)}")

@app.get("/risk-distribution")
async def get_risk_distribution(sample_size: int = 1000) -> Dict[str, Any]:
    """
    Get distribution of risk scores across orders
    """
    try:
        df = get_transactions_df()
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        # Sample and calculate risk scores
        if len(df) > sample_size:
            df_sample = df.sample(n=sample_size, random_state=42)
        else:
            df_sample = df.copy()
        
        # Simulate risk scores
        np.random.seed(42)
        risk_scores = np.random.beta(2, 5, len(df_sample)) * 100
        
        # Create distribution buckets
        buckets = {
            "0-20": sum((risk_scores >= 0) & (risk_scores < 20)),
            "20-40": sum((risk_scores >= 20) & (risk_scores < 40)),
            "40-60": sum((risk_scores >= 40) & (risk_scores < 60)),
            "60-80": sum((risk_scores >= 60) & (risk_scores < 80)),
            "80-100": sum((risk_scores >= 80) & (risk_scores <= 100))
        }
        
        return {
            "success": True,
            "sample_size": len(df_sample),
            "distribution": buckets,
            "mean_risk": round(float(np.mean(risk_scores)), 2),
            "median_risk": round(float(np.median(risk_scores)), 2),
            "std_risk": round(float(np.std(risk_scores)), 2)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating distribution: {str(e)}")

# ============ Run Server ============

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Inventory API on port 8002...")
    print("📦 Role: Inventory Manager - Return Risk Management")
    print("📝 Documentation: http://localhost:8002/docs")
    print("🔍 Health check: http://localhost:8002/health")
    uvicorn.run(app, host="0.0.0.0", port=8002)
