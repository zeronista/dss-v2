"""
FastAPI - Marketing Manager API
Port: 8003
Role: Customer Segmentation & Market Basket Analysis (Prescriptive DSS)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from mlxtend.frequent_patterns import apriori, association_rules

# Import database utilities
from db_utils import get_transactions_df, get_customers_rfm, get_db

app = FastAPI(
    title="Marketing API - Customer Segmentation",
    description="RFM segmentation, K-Means clustering, and Market Basket Analysis",
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

class SegmentationRequest(BaseModel):
    n_segments: int = Field(3, ge=2, le=10, description="Number of customer segments")
    use_existing_rfm: bool = Field(True, description="Use pre-calculated RFM or calculate fresh")

class SegmentInfo(BaseModel):
    segment_id: int
    segment_name: str
    customer_count: int
    avg_recency: float
    avg_frequency: float
    avg_monetary: float
    total_value: float
    characteristics: str
    recommended_actions: List[str]

class BasketAnalysisRequest(BaseModel):
    segment_id: Optional[int] = Field(None, description="Analyze specific segment (optional)")
    min_support: float = Field(0.01, ge=0.001, le=0.5, description="Minimum support threshold")
    min_confidence: float = Field(0.3, ge=0.1, le=1.0, description="Minimum confidence threshold")
    top_n: int = Field(10, ge=1, le=50, description="Top N product bundles")

class ProductBundle(BaseModel):
    antecedents: List[str]
    consequents: List[str]
    support: float
    confidence: float
    lift: float
    expected_revenue: float

# ============ Health Check ============

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "marketing",
        "version": "1.0.0",
        "port": 8003
    }

# ============ Marketing Endpoints ============

@app.get("/")
async def root():
    return {
        "service": "Marketing API - Customer Segmentation",
        "version": "1.0.0",
        "role": "Marketing Manager",
        "dss_type": "Prescriptive",
        "endpoints": [
            "/health",
            "/calculate-rfm",
            "/run-segmentation",
            "/segment-overview",
            "/market-basket-analysis",
            "/product-bundles"
        ]
    }

@app.post("/calculate-rfm")
async def calculate_rfm() -> Dict[str, Any]:
    """
    Calculate RFM (Recency, Frequency, Monetary) scores for all customers
    """
    try:
        df = get_transactions_df()
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No transaction data found")
        
        # Get the reference date (latest transaction date + 1 day)
        reference_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
        
        # Calculate RFM
        rfm = df.groupby('CustomerID').agg({
            'InvoiceDate': lambda x: (reference_date - x.max()).days,  # Recency
            'InvoiceNo': 'nunique',  # Frequency
            'Revenue': 'sum'  # Monetary
        }).reset_index()
        
        rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']
        
        # Calculate RFM scores (1-5 scale using quantiles)
        rfm['R_Score'] = pd.qcut(rfm['Recency'], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop')
        rfm['F_Score'] = pd.qcut(rfm['Frequency'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
        rfm['M_Score'] = pd.qcut(rfm['Monetary'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
        
        # Convert to numeric
        rfm['R_Score'] = pd.to_numeric(rfm['R_Score'])
        rfm['F_Score'] = pd.to_numeric(rfm['F_Score'])
        rfm['M_Score'] = pd.to_numeric(rfm['M_Score'])
        
        # Calculate RFM Score
        rfm['RFM_Score'] = rfm['R_Score'] + rfm['F_Score'] + rfm['M_Score']
        
        # Save to MongoDB (optional)
        # db = get_db()
        # rfm_dict = rfm.to_dict('records')
        # db['customer_rfm'].insert_many(rfm_dict)
        
        return {
            "success": True,
            "message": "RFM calculation completed",
            "customers_analyzed": len(rfm),
            "summary": {
                "avg_recency": round(rfm['Recency'].mean(), 2),
                "avg_frequency": round(rfm['Frequency'].mean(), 2),
                "avg_monetary": round(rfm['Monetary'].mean(), 2)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating RFM: {str(e)}")

@app.post("/run-segmentation")
async def run_segmentation(request: SegmentationRequest) -> Dict[str, Any]:
    """
    Run K-Means clustering on RFM scores to segment customers
    """
    try:
        # Get or calculate RFM data
        if request.use_existing_rfm:
            rfm = get_customers_rfm(as_dataframe=True)
            if rfm.empty:
                # Calculate if not exists
                await calculate_rfm()
                rfm = get_customers_rfm(as_dataframe=True)
        else:
            # Calculate fresh RFM
            df = get_transactions_df()
            reference_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
            rfm = df.groupby('CustomerID').agg({
                'InvoiceDate': lambda x: (reference_date - x.max()).days,
                'InvoiceNo': 'nunique',
                'Revenue': 'sum'
            }).reset_index()
            rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']
        
        if rfm.empty or len(rfm) < request.n_segments:
            raise HTTPException(status_code=400, detail="Not enough data for segmentation")
        
        # Prepare features for clustering
        features = rfm[['Recency', 'Frequency', 'Monetary']].copy()
        
        # Standardize features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Run K-Means
        kmeans = KMeans(n_clusters=request.n_segments, random_state=42, n_init=10)
        rfm['Segment'] = kmeans.fit_predict(features_scaled)
        
        # Assign segment names based on RFM characteristics
        segment_summary = []
        for seg_id in range(request.n_segments):
            seg_data = rfm[rfm['Segment'] == seg_id]
            
            avg_r = seg_data['Recency'].mean()
            avg_f = seg_data['Frequency'].mean()
            avg_m = seg_data['Monetary'].mean()
            
            # Name segments based on characteristics
            if avg_f > rfm['Frequency'].quantile(0.7) and avg_m > rfm['Monetary'].quantile(0.7):
                name = "Champions"
                char = "High-value loyal customers with recent purchases"
                actions = [
                    "VIP early access to new products",
                    "Exclusive rewards program",
                    "Personalized product recommendations"
                ]
            elif avg_r < rfm['Recency'].quantile(0.3) and avg_f > rfm['Frequency'].median():
                name = "Loyal Customers"
                char = "Regular customers with good engagement"
                actions = [
                    "Loyalty rewards",
                    "Upsell premium products",
                    "Referral program incentives"
                ]
            elif avg_r > rfm['Recency'].quantile(0.7):
                name = "At Risk"
                char = "Previously active customers who haven't purchased recently"
                actions = [
                    "Win-back campaigns with special offers",
                    "Survey to understand churn reasons",
                    "Re-engagement email series"
                ]
            elif avg_f < rfm['Frequency'].quantile(0.3):
                name = "New Customers"
                char = "Recent customers with limited purchase history"
                actions = [
                    "Welcome series and onboarding",
                    "First-time buyer incentives",
                    "Product education content"
                ]
            else:
                name = f"Segment {seg_id + 1}"
                char = "Mixed customer characteristics"
                actions = [
                    "General marketing campaigns",
                    "A/B test different offers"
                ]
            
            segment_summary.append({
                "segment_id": int(seg_id),
                "segment_name": name,
                "customer_count": int(len(seg_data)),
                "avg_recency": round(avg_r, 2),
                "avg_frequency": round(avg_f, 2),
                "avg_monetary": round(avg_m, 2),
                "total_value": round(seg_data['Monetary'].sum(), 2),
                "characteristics": char,
                "recommended_actions": actions
            })
        
        return {
            "success": True,
            "n_segments": request.n_segments,
            "total_customers": len(rfm),
            "segments": segment_summary
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running segmentation: {str(e)}")

@app.get("/segment-overview")
async def get_segment_overview(n_segments: int = 3) -> Dict[str, Any]:
    """
    Get overview of all customer segments
    """
    try:
        seg_request = SegmentationRequest(n_segments=n_segments)
        result = await run_segmentation(seg_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting segment overview: {str(e)}")

@app.post("/market-basket-analysis")
async def market_basket_analysis(request: BasketAnalysisRequest) -> Dict[str, Any]:
    """
    Run Market Basket Analysis (Apriori Algorithm) to find product associations
    """
    try:
        df = get_transactions_df()
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No transaction data found")
        
        # Filter by segment if specified
        if request.segment_id is not None:
            # Get segment customers (would need to run segmentation first)
            # For now, we'll analyze all data
            pass
        
        # OPTIMIZATION: Limit to top N products by frequency
        product_counts = df['Description'].value_counts()
        top_products = product_counts.head(100).index.tolist()  # Reduced to 100
        df = df[df['Description'].isin(top_products)].copy()
        
        # Limit transactions
        df = df.nlargest(50000, 'InvoiceDate')
        
        # Create basket (one-hot encoding)
        # Group by invoice and create a list of products
        basket = df.groupby(['InvoiceNo', 'Description'])['Quantity'].sum().unstack().fillna(0)
        
        # Convert to binary (1 if purchased, 0 otherwise)
        def encode_units(x):
            return 1 if x > 0 else 0
        
        basket_encoded = basket.map(encode_units)
        
        # Run Apriori algorithm
        frequent_itemsets = apriori(
            basket_encoded, 
            min_support=request.min_support, 
            use_colnames=True
        )
        
        if frequent_itemsets.empty:
            return {
                "success": True,
                "message": "No frequent itemsets found. Try lowering min_support.",
                "bundles": []
            }
        
        # Generate association rules
        rules = association_rules(
            frequent_itemsets, 
            metric="confidence", 
            min_threshold=request.min_confidence
        )
        
        if rules.empty:
            return {
                "success": True,
                "message": "No rules found. Try lowering min_confidence.",
                "bundles": []
            }
        
        # Sort by lift and get top N
        rules = rules.sort_values('lift', ascending=False).head(request.top_n)
        
        # Format results
        bundles = []
        for _, rule in rules.iterrows():
            # Estimate revenue impact
            antecedents_list = list(rule['antecedents'])
            consequents_list = list(rule['consequents'])
            
            # Calculate average revenue for consequent items
            consequent_revenue = df[
                df['Description'].isin(consequents_list)
            ]['Revenue'].mean() if len(consequents_list) > 0 else 0
            
            expected_revenue = consequent_revenue * rule['confidence'] * rule['support'] * len(df)
            
            bundles.append({
                "antecedents": antecedents_list,
                "consequents": consequents_list,
                "support": round(rule['support'], 4),
                "confidence": round(rule['confidence'], 4),
                "lift": round(rule['lift'], 4),
                "expected_revenue": round(expected_revenue, 2)
            })
        
        return {
            "success": True,
            "total_rules": len(rules),
            "bundles": bundles,
            "parameters": {
                "min_support": request.min_support,
                "min_confidence": request.min_confidence
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in market basket analysis: {str(e)}")

@app.post("/product-bundles")
async def get_product_bundles(
    min_support: float = 0.01,
    min_confidence: float = 0.3,
    top_n: int = 10
) -> Dict[str, Any]:
    """
    Get recommended product bundles based on Market Basket Analysis
    """
    try:
        request = BasketAnalysisRequest(
            min_support=min_support,
            min_confidence=min_confidence,
            top_n=top_n
        )
        return await market_basket_analysis(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting product bundles: {str(e)}")

# ============ Run Server ============

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Marketing API on port 8003...")
    print("💖 Role: Marketing Manager - Customer Segmentation")
    print("📝 Documentation: http://localhost:8003/docs")
    print("🔍 Health check: http://localhost:8003/health")
    uvicorn.run(app, host="0.0.0.0", port=8003)
