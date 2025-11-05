"""
FastAPI - Admin/Director API
Port: 8001
Role: Sales Overview & Revenue Analytics (Descriptive DSS)
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from collections import defaultdict
import os

# Import database utilities
from db_utils import get_transactions_df, get_db

# ============ Local Data Configuration ============
# Path to local cleaned data file (faster than MongoDB)
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
CSV_FILE = os.path.join(DATA_DIR, 'online_retail_cleaned.csv')
PARQUET_FILE = os.path.join(DATA_DIR, 'online_retail_cleaned.parquet')

# Cache for loaded data
_cached_df = None
_cache_timestamp = None
_cache_ttl = 3600  # Cache for 1 hour

def get_local_transactions_df() -> pd.DataFrame:
    """
    Load transactions from local CSV file (FAST!)
    Uses caching to avoid repeated file reads
    
    Returns:
        pandas DataFrame with cleaned transactions
    """
    global _cached_df, _cache_timestamp
    
    # Check if cache is valid
    if _cached_df is not None and _cache_timestamp is not None:
        if (datetime.now() - _cache_timestamp).seconds < _cache_ttl:
            print(f"✅ Using cached data ({len(_cached_df)} rows)")
            df_copy = _cached_df.copy()
            # Ensure InvoiceDate is datetime type
            if df_copy['InvoiceDate'].dtype == 'object':
                df_copy['InvoiceDate'] = pd.to_datetime(df_copy['InvoiceDate'], errors='coerce')
            return df_copy
    
    print(f"📂 Loading data from local file...")
    
    try:
        # Use CSV file (as requested)
        if os.path.exists(CSV_FILE):
            print(f"📊 Loading from CSV: {CSV_FILE}")
            df = pd.read_csv(CSV_FILE)
            # Convert InvoiceDate to datetime
            df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')
            print(f"✅ Loaded {len(df)} transactions from CSV")
        # Fallback to parquet if CSV not found
        elif os.path.exists(PARQUET_FILE):
            print(f"📊 Loading from parquet: {PARQUET_FILE}")
            df = pd.read_parquet(PARQUET_FILE)
            # Ensure datetime conversion
            if df['InvoiceDate'].dtype == 'object':
                df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')
            print(f"✅ Loaded {len(df)} transactions from parquet (fallback)")
        else:
            raise FileNotFoundError(f"No data file found in {DATA_DIR}")
        
        # Ensure required columns
        if 'Revenue' not in df.columns and 'Quantity' in df.columns and 'UnitPrice' in df.columns:
            df['Revenue'] = df['Quantity'] * df['UnitPrice']
        
        # Cache the data
        _cached_df = df.copy()
        _cache_timestamp = datetime.now()
        
        return df
    
    except Exception as e:
        print(f"❌ Error loading local data: {e}")
        print(f"💡 Falling back to MongoDB...")
        # Fallback to MongoDB if local file fails
        return get_transactions_df()

app = FastAPI(
    title="Admin API - Sales Overview",
    description="Sales overview, KPIs, revenue trends, and Top-N analytics",
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

class FilterRequest(BaseModel):
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    countries: Optional[List[str]] = Field(None, description="List of countries")
    top_n: int = Field(10, ge=5, le=50, description="Top N items to show")
    exclude_cancelled: bool = Field(True, description="Exclude cancelled invoices")

class KPIResponse(BaseModel):
    total_revenue: float
    total_transactions: int
    countries_active: int
    top_n_revenue_share: float
    avg_order_value: float
    
class MonthlyTrendItem(BaseModel):
    year_month: str
    revenue: float
    mom_growth: Optional[float] = None
    transactions: int

class TopNItem(BaseModel):
    rank: int
    item: str
    revenue: float
    share_pct: float
    transactions: int

# ============ Health Check ============

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "admin",
        "version": "1.0.0",
        "port": 8001
    }

# ============ Admin Endpoints ============

@app.get("/")
async def root():
    return {
        "service": "Admin API - Sales Overview",
        "version": "1.0.0",
        "role": "Admin/Director",
        "dss_type": "Descriptive",
        "endpoints": [
            "/health",
            "/countries",
            "/kpis",
            "/monthly-trend",
            "/top-countries",
            "/top-products",
            "/revenue-summary"
        ]
    }

@app.get("/countries")
async def get_countries() -> Dict[str, Any]:
    """
    Get list of all available countries for filter dropdown
    """
    try:
        df = get_local_transactions_df()
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        # Get unique countries sorted alphabetically
        countries = sorted(df['Country'].unique().tolist())
        
        return {
            "success": True,
            "countries": countries,
            "count": len(countries)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting countries: {str(e)}")

@app.post("/kpis", response_model=KPIResponse)
async def get_kpis(filters: FilterRequest):
    """
    Get key performance indicators (KPIs)
    - Total Revenue
    - Total Transactions
    - Countries Active
    - Top-N Revenue Share
    - Average Order Value
    """
    try:
        # Get filtered data
        df = _apply_filters(filters)
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found for given filters")
        
        # Calculate KPIs
        total_revenue = df['Revenue'].sum()
        total_transactions = df['InvoiceNo'].nunique()
        countries_active = df['Country'].nunique()
        avg_order_value = total_revenue / total_transactions if total_transactions > 0 else 0
        
        # Calculate Top-N revenue share
        if 'Country' in df.columns:
            top_countries = df.groupby('Country')['Revenue'].sum().nlargest(filters.top_n)
            top_n_revenue = top_countries.sum()
            top_n_share = (top_n_revenue / total_revenue * 100) if total_revenue > 0 else 0
        else:
            top_n_share = 0
        
        return {
            "total_revenue": round(total_revenue, 2),
            "total_transactions": total_transactions,
            "countries_active": countries_active,
            "top_n_revenue_share": round(top_n_share, 2),
            "avg_order_value": round(avg_order_value, 2)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating KPIs: {str(e)}")

@app.post("/monthly-trend")
async def get_monthly_trend(filters: FilterRequest) -> Dict[str, Any]:
    """
    Get monthly revenue trend with MoM growth rate
    """
    try:
        df = _apply_filters(filters)
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        # Ensure InvoiceDate is datetime
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
        
        # Create YearMonth column
        df['YearMonth'] = df['InvoiceDate'].dt.to_period('M')
        
        # Group by month
        monthly = df.groupby('YearMonth').agg({
            'Revenue': 'sum',
            'InvoiceNo': 'nunique'
        }).reset_index()
        
        monthly.columns = ['YearMonth', 'Revenue', 'Transactions']
        monthly['YearMonth'] = monthly['YearMonth'].astype(str)
        
        # Calculate MoM growth
        monthly['MoM_Growth'] = monthly['Revenue'].pct_change() * 100
        
        # Convert to list of dicts
        trend_data = []
        for _, row in monthly.iterrows():
            trend_data.append({
                "year_month": row['YearMonth'],
                "revenue": round(row['Revenue'], 2),
                "mom_growth": round(row['MoM_Growth'], 2) if pd.notna(row['MoM_Growth']) else None,
                "transactions": int(row['Transactions'])
            })
        
        return {
            "success": True,
            "data": trend_data,
            "count": len(trend_data)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating trend: {str(e)}")

@app.post("/top-countries")
async def get_top_countries(filters: FilterRequest) -> Dict[str, Any]:
    """
    Get Top-N countries by revenue
    """
    try:
        df = _apply_filters(filters)
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        # Group by country
        country_stats = df.groupby('Country').agg({
            'Revenue': 'sum',
            'InvoiceNo': 'nunique'
        }).reset_index()
        
        country_stats.columns = ['Country', 'Revenue', 'Transactions']
        
        # Sort and get top N
        country_stats = country_stats.sort_values('Revenue', ascending=False).head(filters.top_n)
        
        # Calculate share
        total_revenue = df['Revenue'].sum()
        country_stats['SharePct'] = (country_stats['Revenue'] / total_revenue * 100) if total_revenue > 0 else 0
        
        # Add rank
        country_stats['Rank'] = range(1, len(country_stats) + 1)
        
        # Convert to list
        result = []
        for _, row in country_stats.iterrows():
            result.append({
                "rank": int(row['Rank']),
                "item": row['Country'],
                "revenue": round(row['Revenue'], 2),
                "share_pct": round(row['SharePct'], 2),
                "transactions": int(row['Transactions'])
            })
        
        return {
            "success": True,
            "data": result,
            "count": len(result)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting top countries: {str(e)}")

@app.post("/top-products")
async def get_top_products(filters: FilterRequest) -> Dict[str, Any]:
    """
    Get Top-N products (SKUs) by revenue
    """
    try:
        df = _apply_filters(filters)
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        # Group by StockCode + Description
        df['Product'] = df['StockCode'].astype(str) + ' - ' + df['Description'].fillna('Unknown')
        
        product_stats = df.groupby('Product').agg({
            'Revenue': 'sum',
            'InvoiceNo': 'nunique'
        }).reset_index()
        
        product_stats.columns = ['Product', 'Revenue', 'Transactions']
        
        # Sort and get top N
        product_stats = product_stats.sort_values('Revenue', ascending=False).head(filters.top_n)
        
        # Calculate share
        total_revenue = df['Revenue'].sum()
        product_stats['SharePct'] = (product_stats['Revenue'] / total_revenue * 100) if total_revenue > 0 else 0
        
        # Add rank
        product_stats['Rank'] = range(1, len(product_stats) + 1)
        
        # Convert to list
        result = []
        for _, row in product_stats.iterrows():
            result.append({
                "rank": int(row['Rank']),
                "item": row['Product'],
                "revenue": round(row['Revenue'], 2),
                "share_pct": round(row['SharePct'], 2),
                "transactions": int(row['Transactions'])
            })
        
        return {
            "success": True,
            "data": result,
            "count": len(result)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting top products: {str(e)}")

@app.post("/revenue-summary")
async def get_revenue_summary(filters: FilterRequest) -> Dict[str, Any]:
    """
    Get comprehensive revenue summary with all KPIs and trends
    """
    try:
        # Get all data
        kpis = await get_kpis(filters)
        monthly = await get_monthly_trend(filters)
        top_countries = await get_top_countries(filters)
        top_products = await get_top_products(filters)
        
        return {
            "success": True,
            "filters_applied": filters.dict(),
            "kpis": kpis,
            "monthly_trend": monthly.get("data", []),
            "top_countries": top_countries.get("data", []),
            "top_products": top_products.get("data", [])
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

# ============ Helper Functions ============

def _apply_filters(filters: FilterRequest) -> pd.DataFrame:
    """
    Apply filters and return filtered DataFrame
    NOW USING LOCAL DATA FOR FASTER PERFORMANCE! 🚀
    """
    # Get data from LOCAL FILE (much faster!)
    df = get_local_transactions_df()
    
    if df.empty:
        return df
    
    # Apply date range filter
    if filters.start_date or filters.end_date:
        if filters.start_date:
            df = df[df['InvoiceDate'] >= pd.to_datetime(filters.start_date)]
        if filters.end_date:
            end_datetime = pd.to_datetime(filters.end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
            df = df[df['InvoiceDate'] <= end_datetime]
    
    # Apply country filter
    if filters.countries and len(filters.countries) > 0:
        df = df[df['Country'].isin(filters.countries)]
    
    # Exclude cancelled invoices
    if filters.exclude_cancelled:
        df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
    
    return df.copy()

# ============ Run Server ============

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Admin API on port 8001...")
    print("📊 Role: Admin/Director - Sales Overview")
    print("📝 Documentation: http://localhost:8001/docs")
    print("🔍 Health check: http://localhost:8001/health")
    uvicorn.run(app, host="0.0.0.0", port=8001)
