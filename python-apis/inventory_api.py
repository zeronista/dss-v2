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
import os

# Import database utilities (fallback only)
from db_utils import get_transactions_df as get_transactions_df_mongo, get_db

# ============ Local File Configuration ============
# Inventory Manager uses FULL dataset (online_retail.csv) to analyze returns and cancellations
CSV_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'online_retail.csv')
PARQUET_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'online_retail.parquet')

# Cache for local data (1 hour TTL)
_cached_df = None
_cache_timestamp = None
_cache_ttl = 3600  # seconds

def get_local_transactions_df() -> pd.DataFrame:
    """
    Load transactions from local CSV file with caching
    INVENTORY MANAGER: Uses FULL dataset including cancelled/returned orders (InvoiceNo starts with 'C')
    This is essential for return risk analysis and policy simulation
    Falls back to MongoDB if file not found
    """
    global _cached_df, _cache_timestamp
    
    # Check cache validity
    if _cached_df is not None and _cache_timestamp is not None:
        elapsed = (datetime.now() - _cache_timestamp).seconds
        if elapsed < _cache_ttl:
            print(f"✅ Using cached FULL data ({len(_cached_df)} rows, age: {elapsed}s)")
            # Return copy and ensure datetime type
            df_copy = _cached_df.copy()
            if df_copy['InvoiceDate'].dtype == 'object':
                df_copy['InvoiceDate'] = pd.to_datetime(df_copy['InvoiceDate'], errors='coerce')
            return df_copy
    
    # Try loading from local CSV
    if os.path.exists(CSV_FILE):
        print(f"📂 Loading FULL transactions from local CSV: {CSV_FILE}")
        df = pd.read_csv(CSV_FILE, low_memory=False)
        
        # Convert InvoiceDate to datetime with error handling
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')
        
        # Ensure numeric columns
        if 'Quantity' in df.columns:
            df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
        if 'UnitPrice' in df.columns:
            df['UnitPrice'] = pd.to_numeric(df['UnitPrice'], errors='coerce')
        
        # Calculate Revenue if not exists (can be negative for returns)
        if 'Revenue' not in df.columns:
            df['Revenue'] = df['Quantity'] * df['UnitPrice']
        
        # IMPORTANT: For Inventory Manager, keep ALL transactions including cancelled/returns
        # Only filter out completely invalid data (missing critical fields)
        df = df[df['InvoiceDate'].notna() & df['InvoiceNo'].notna()].copy()
        
        # Add flags to identify returns and cancellations
        df['IsReturn'] = df['InvoiceNo'].astype(str).str.startswith('C')
        df['IsNegativeQty'] = df['Quantity'] < 0
        
        # Update cache
        _cached_df = df.copy()
        _cache_timestamp = datetime.now()
        
        returns_count = df['IsReturn'].sum()
        negative_qty_count = df['IsNegativeQty'].sum()
        print(f"✅ Loaded {len(df)} FULL transactions from CSV")
        print(f"   📊 Returns/Cancellations: {returns_count} ({returns_count/len(df)*100:.1f}%)")
        print(f"   📊 Negative Quantities: {negative_qty_count} ({negative_qty_count/len(df)*100:.1f}%)")
        print(f"   💾 Cached for {_cache_ttl}s")
        return df
    
    # Fallback to Parquet
    elif os.path.exists(PARQUET_FILE):
        print(f"📂 Loading FULL data from Parquet: {PARQUET_FILE}")
        df = pd.read_parquet(PARQUET_FILE)
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')
        
        # Add return flags
        df['IsReturn'] = df['InvoiceNo'].astype(str).str.startswith('C')
        df['IsNegativeQty'] = df['Quantity'] < 0
        
        # Update cache
        _cached_df = df.copy()
        _cache_timestamp = datetime.now()
        
        print(f"✅ Loaded {len(df)} transactions from Parquet (FULL dataset)")
        return df
    
    # Final fallback to MongoDB
    else:
        print("⚠️  Local files not found, falling back to MongoDB...")
        df = get_transactions_df_mongo()
        
        # Cache MongoDB data too
        _cached_df = df.copy()
        _cache_timestamp = datetime.now()
        
        return df

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
        "port": 8002,
        "data_source": "Full dataset (online_retail.csv)"
    }

@app.get("/return-statistics")
async def get_return_statistics() -> Dict[str, Any]:
    """
    Get detailed statistics about returns and cancellations from FULL dataset
    This endpoint provides insights into return patterns across customers, products, and time
    """
    try:
        df = get_local_transactions_df()
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        # Overall statistics
        total_transactions = len(df)
        total_orders = df['InvoiceNo'].nunique()
        total_returns = df[df['IsReturn'] == True]['InvoiceNo'].nunique()
        total_negative_qty = df[df['IsNegativeQty'] == True]['InvoiceNo'].nunique()
        
        return_rate = (total_returns / total_orders * 100) if total_orders > 0 else 0
        
        # Customer statistics
        customers_with_returns = df[df['IsReturn'] == True]['CustomerID'].nunique()
        total_customers = df['CustomerID'].nunique()
        customer_return_rate = (customers_with_returns / total_customers * 100) if total_customers > 0 else 0
        
        # Product statistics
        products_with_returns = df[df['IsReturn'] == True]['StockCode'].nunique()
        total_products = df['StockCode'].nunique()
        product_return_rate = (products_with_returns / total_products * 100) if total_products > 0 else 0
        
        # Top returned products
        return_df = df[df['IsReturn'] == True]
        if not return_df.empty:
            top_returned_products = (
                return_df.groupby('StockCode')['InvoiceNo']
                .nunique()
                .sort_values(ascending=False)
                .head(10)
                .to_dict()
            )
        else:
            top_returned_products = {}
        
        # Top customers with returns
        if not return_df.empty:
            top_returning_customers = (
                return_df.groupby('CustomerID')['InvoiceNo']
                .nunique()
                .sort_values(ascending=False)
                .head(10)
                .to_dict()
            )
        else:
            top_returning_customers = {}
        
        # Monthly return trends (if InvoiceDate is available)
        monthly_stats = {}
        if 'InvoiceDate' in df.columns and df['InvoiceDate'].notna().any():
            df['YearMonth'] = df['InvoiceDate'].dt.to_period('M').astype(str)
            monthly_returns = df[df['IsReturn'] == True].groupby('YearMonth')['InvoiceNo'].nunique()
            monthly_total = df.groupby('YearMonth')['InvoiceNo'].nunique()
            monthly_stats = {
                month: {
                    "returns": int(monthly_returns.get(month, 0)),
                    "total": int(monthly_total.get(month, 0)),
                    "return_rate": round((monthly_returns.get(month, 0) / monthly_total.get(month, 1) * 100), 2)
                }
                for month in monthly_total.index[-6:]  # Last 6 months
            }
        
        return {
            "success": True,
            "data_source": "Full dataset (online_retail.csv)",
            "overall_statistics": {
                "total_transactions": int(total_transactions),
                "total_orders": int(total_orders),
                "total_returns": int(total_returns),
                "total_negative_qty_orders": int(total_negative_qty),
                "return_rate_percent": round(return_rate, 2)
            },
            "customer_statistics": {
                "total_customers": int(total_customers),
                "customers_with_returns": int(customers_with_returns),
                "customer_return_rate_percent": round(customer_return_rate, 2)
            },
            "product_statistics": {
                "total_products": int(total_products),
                "products_with_returns": int(products_with_returns),
                "product_return_rate_percent": round(product_return_rate, 2)
            },
            "top_returned_products": {str(k): int(v) for k, v in list(top_returned_products.items())[:10]},
            "top_returning_customers": {str(k): int(v) for k, v in list(top_returning_customers.items())[:10]},
            "monthly_trends": monthly_stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting return statistics: {str(e)}")

# ============ Inventory Endpoints ============

@app.get("/")
async def root():
    return {
        "service": "Inventory API - Return Risk Management",
        "version": "1.0.0",
        "role": "Inventory Manager",
        "dss_type": "Prescriptive",
        "data_source": "FULL dataset (online_retail.csv) including returns and cancellations",
        "note": "This API uses complete transaction history to analyze return patterns",
        "endpoints": [
            "/health",
            "/return-statistics",
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
    - Customer history (return rate) - USES FULL DATA including cancellations
    - Product return rate - USES FULL DATA including returns
    - Order value
    - Quantity anomaly
    """
    try:
        df = get_local_transactions_df()
        
        if df.empty:
            # Default risk score if no data
            risk_score = 50.0
        else:
            # Calculate customer return rate (using IsReturn flag from full dataset)
            customer_data = df[df['CustomerID'] == request.customer_id]
            if not customer_data.empty:
                # Calculate actual return rate from full dataset
                total_customer_orders = customer_data['InvoiceNo'].nunique()
                returned_orders = customer_data[customer_data['IsReturn'] == True]['InvoiceNo'].nunique()
                customer_return_rate = (returned_orders / total_customer_orders * 100) if total_customer_orders > 0 else 15.0
                
                # Also check for negative quantities
                negative_qty_orders = customer_data[customer_data['IsNegativeQty'] == True]['InvoiceNo'].nunique()
                negative_qty_rate = (negative_qty_orders / total_customer_orders * 100) if total_customer_orders > 0 else 0
                
                # Combine both indicators
                customer_return_rate = max(customer_return_rate, negative_qty_rate)
            else:
                customer_return_rate = 30.0  # Default for new customers (higher risk)
            
            # Calculate product return rate (using IsReturn flag from full dataset)
            product_data = df[df['StockCode'] == request.stock_code]
            if not product_data.empty:
                # Calculate actual product return rate
                total_product_orders = product_data['InvoiceNo'].nunique()
                returned_product_orders = product_data[product_data['IsReturn'] == True]['InvoiceNo'].nunique()
                product_return_rate = (returned_product_orders / total_product_orders * 100) if total_product_orders > 0 else 10.0
                
                # Check negative quantity rate for this product
                negative_product_orders = product_data[product_data['IsNegativeQty'] == True]['InvoiceNo'].nunique()
                negative_product_rate = (negative_product_orders / total_product_orders * 100) if total_product_orders > 0 else 0
                
                # Combine both indicators
                product_return_rate = max(product_return_rate, negative_product_rate)
            else:
                product_return_rate = 20.0  # Default for new products (higher risk)
            
            # Quantity anomaly (high quantity = higher risk)
            # Filter positive quantities for baseline
            positive_qty_df = df[df['Quantity'] > 0]
            avg_quantity = positive_qty_df['Quantity'].mean() if not positive_qty_df.empty else 1
            quantity_risk = min(100, (request.quantity / avg_quantity) * 30)
            
            # Order value risk (very high or very low values are risky)
            order_value = request.quantity * request.unit_price
            # Use positive revenues for baseline
            positive_revenue_df = df[df['Revenue'] > 0]
            avg_order_value = positive_revenue_df['Revenue'].mean() if not positive_revenue_df.empty else 100
            value_deviation = abs(order_value - avg_order_value) / avg_order_value if avg_order_value > 0 else 0
            value_risk = min(100, value_deviation * 50)
            
            # Weighted risk score
            risk_score = (
                customer_return_rate * 0.4 +  # Customer history is most important
                product_return_rate * 0.3 +    # Product quality/popularity
                quantity_risk * 0.2 +          # Unusual quantities
                value_risk * 0.1               # Unusual values
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
            "message": f"Risk assessment completed. Score: {risk_score:.2f}/100 (Customer Return Rate: {customer_return_rate:.1f}%, Product Return Rate: {product_return_rate:.1f}%)"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating risk: {str(e)}")

@app.post("/simulate-policy", response_model=PolicySimulationResponse)
async def simulate_policy(request: PolicySimulationRequest):
    """
    Simulate policy with given threshold (tau)
    - Orders with Risk >= tau: Apply policy (e.g., block COD, require prepayment)
    - Orders with Risk < tau: Allow normally
    USES FULL DATASET to calculate actual return rates
    """
    try:
        df = get_local_transactions_df()
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No transaction data found")
        
        # Filter to positive transactions only (exclude returns) for baseline simulation
        df_positive = df[~df['IsReturn'] & (df['Quantity'] > 0) & (df['UnitPrice'] > 0)].copy()
        
        if df_positive.empty:
            raise HTTPException(status_code=404, detail="No valid positive transactions found")
        
        # Sample orders for simulation
        if len(df_positive) > request.sample_size:
            df_sample = df_positive.sample(n=request.sample_size, random_state=42)
        else:
            df_sample = df_positive.copy()
        
        # Calculate ACTUAL risk scores based on customer and product return history
        risk_scores = []
        for idx, row in df_sample.iterrows():
            customer_id = row.get('CustomerID')
            stock_code = row.get('StockCode')
            
            # Calculate customer return rate
            if pd.notna(customer_id):
                customer_data = df[df['CustomerID'] == customer_id]
                total_customer_orders = customer_data['InvoiceNo'].nunique()
                returned_orders = customer_data[customer_data['IsReturn'] == True]['InvoiceNo'].nunique()
                customer_return_rate = (returned_orders / total_customer_orders * 100) if total_customer_orders > 0 else 15.0
            else:
                customer_return_rate = 30.0
            
            # Calculate product return rate
            product_data = df[df['StockCode'] == stock_code]
            total_product_orders = product_data['InvoiceNo'].nunique()
            returned_product_orders = product_data[product_data['IsReturn'] == True]['InvoiceNo'].nunique()
            product_return_rate = (returned_product_orders / total_product_orders * 100) if total_product_orders > 0 else 10.0
            
            # Simplified risk score (customer 60% + product 40%)
            risk_score = customer_return_rate * 0.6 + product_return_rate * 0.4
            risk_scores.append(min(100, max(0, risk_score)))
        
        df_sample['RiskScore'] = risk_scores
        
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
    USES ACTUAL return data from full dataset to calculate risk distribution
    """
    try:
        df = get_local_transactions_df()
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        # Filter to positive transactions for risk scoring
        df_positive = df[~df['IsReturn'] & (df['Quantity'] > 0) & (df['UnitPrice'] > 0)].copy()
        
        if df_positive.empty:
            raise HTTPException(status_code=404, detail="No valid positive transactions found")
        
        # Sample and calculate ACTUAL risk scores
        if len(df_positive) > sample_size:
            df_sample = df_positive.sample(n=sample_size, random_state=42)
        else:
            df_sample = df_positive.copy()
        
        # Calculate real risk scores based on return history
        risk_scores = []
        for idx, row in df_sample.iterrows():
            customer_id = row.get('CustomerID')
            stock_code = row.get('StockCode')
            
            # Calculate customer return rate
            if pd.notna(customer_id):
                customer_data = df[df['CustomerID'] == customer_id]
                total_customer_orders = customer_data['InvoiceNo'].nunique()
                returned_orders = customer_data[customer_data['IsReturn'] == True]['InvoiceNo'].nunique()
                customer_return_rate = (returned_orders / total_customer_orders * 100) if total_customer_orders > 0 else 15.0
            else:
                customer_return_rate = 30.0
            
            # Calculate product return rate
            product_data = df[df['StockCode'] == stock_code]
            total_product_orders = product_data['InvoiceNo'].nunique()
            returned_product_orders = product_data[product_data['IsReturn'] == True]['InvoiceNo'].nunique()
            product_return_rate = (returned_product_orders / total_product_orders * 100) if total_product_orders > 0 else 10.0
            
            # Combined risk score
            risk_score = customer_return_rate * 0.6 + product_return_rate * 0.4
            risk_scores.append(min(100, max(0, risk_score)))
        
        risk_scores = np.array(risk_scores)
        
        # Create distribution buckets
        buckets = {
            "0-20": int(sum((risk_scores >= 0) & (risk_scores < 20))),
            "20-40": int(sum((risk_scores >= 20) & (risk_scores < 40))),
            "40-60": int(sum((risk_scores >= 40) & (risk_scores < 60))),
            "60-80": int(sum((risk_scores >= 60) & (risk_scores < 80))),
            "80-100": int(sum((risk_scores >= 80) & (risk_scores <= 100)))
        }
        
        # Calculate overall return statistics
        total_orders = df['InvoiceNo'].nunique()
        total_returns = df[df['IsReturn'] == True]['InvoiceNo'].nunique()
        overall_return_rate = (total_returns / total_orders * 100) if total_orders > 0 else 0
        
        return {
            "success": True,
            "sample_size": int(len(df_sample)),
            "distribution": buckets,
            "mean_risk": round(float(np.mean(risk_scores)), 2),
            "median_risk": round(float(np.median(risk_scores)), 2),
            "std_risk": round(float(np.std(risk_scores)), 2),
            "overall_return_rate": round(overall_return_rate, 2),
            "total_orders_in_db": int(total_orders),
            "total_returns_in_db": int(total_returns),
            "data_source": "Full dataset (online_retail.csv) including returns"
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
