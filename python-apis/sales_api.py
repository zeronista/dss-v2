"""
FastAPI - Sales Manager API
Port: 8004
Role: Cross-sell & Next Best Offer (Predictive DSS)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime
from mlxtend.frequent_patterns import apriori, association_rules
from collections import defaultdict

# Import database utilities
from db_utils import get_transactions_df, get_customers_rfm, get_db

app = FastAPI(
    title="Sales API - Cross-sell & Next Best Offer",
    description="Product recommendations using Association Rules Mining",
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

class RecommendationRequest(BaseModel):
    stock_code: str = Field(..., description="Source product StockCode")
    customer_id: Optional[str] = Field(None, description="Customer ID for personalization")
    confidence_threshold: float = Field(0.3, ge=0.1, le=1.0, description="Minimum confidence")
    top_n: int = Field(5, ge=1, le=20, description="Number of recommendations")
    min_support: float = Field(0.01, ge=0.001, le=0.5, description="Minimum support for rules")

class ProductRecommendation(BaseModel):
    rank: int
    stock_code: str
    description: str
    support: float
    confidence: float
    lift: float
    expected_impact: float
    recommendation_reason: str

class CrossSellInsight(BaseModel):
    bundle_opportunity: str
    timing_strategy: str
    expected_aov_increase: float

class NetworkNode(BaseModel):
    id: str
    label: str
    value: float

class NetworkEdge(BaseModel):
    source: str
    target: str
    confidence: float
    lift: float

# ============ Health Check ============

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "sales",
        "version": "1.0.0",
        "port": 8004
    }

# ============ Sales Endpoints ============

@app.get("/")
async def root():
    return {
        "service": "Sales API - Cross-sell & Next Best Offer",
        "version": "1.0.0",
        "role": "Sales Manager",
        "dss_type": "Predictive",
        "endpoints": [
            "/health",
            "/generate-recommendations",
            "/cross-sell-insights",
            "/product-network",
            "/customer-recommendations",
            "/top-bundles"
        ]
    }

@app.post("/generate-recommendations")
async def generate_recommendations(request: RecommendationRequest) -> Dict[str, Any]:
    """
    Generate product recommendations based on Association Rules
    """
    try:
        df = get_transactions_df()
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No transaction data found")
        
        # Verify source product exists
        source_product = df[df['StockCode'] == request.stock_code]
        if source_product.empty:
            raise HTTPException(status_code=404, detail=f"Product {request.stock_code} not found")
        
        source_description = source_product['Description'].iloc[0]
        
        # OPTIMIZATION: Limit to top N products by frequency to reduce memory
        product_counts = df['StockCode'].value_counts()
        top_products = product_counts.head(50).index.tolist()  # Reduced to top 50 products for memory
        
        # Ensure source product is included
        if request.stock_code not in top_products:
            top_products.append(request.stock_code)
        
        # Filter dataframe to only include top products
        df_filtered = df[df['StockCode'].isin(top_products)].copy()
        
        # Also limit to recent transactions (last 3 months)
        df_filtered = df_filtered.nlargest(10000, 'InvoiceDate')  # Limit to 10k most recent transactions
        
        # Create transaction basket
        basket = df_filtered.groupby(['InvoiceNo', 'StockCode'])['Quantity'].sum().unstack().fillna(0)
        
        # Binary encoding
        basket_encoded = basket.map(lambda x: 1 if x > 0 else 0)
        
        # Run Apriori
        frequent_itemsets = apriori(
            basket_encoded,
            min_support=request.min_support,
            use_colnames=True
        )
        
        if frequent_itemsets.empty:
            return {
                "success": True,
                "message": "No frequent patterns found. Try lowering min_support.",
                "recommendations": []
            }
        
        # Generate association rules
        rules = association_rules(
            frequent_itemsets,
            metric="confidence",
            min_threshold=request.confidence_threshold
        )
        
        if rules.empty:
            return {
                "success": True,
                "message": "No association rules found.",
                "recommendations": []
            }
        
        # Filter rules where source product is in antecedents
        relevant_rules = rules[
            rules['antecedents'].apply(lambda x: request.stock_code in x)
        ].copy()
        
        if relevant_rules.empty:
            return {
                "success": True,
                "message": f"No recommendations found for {request.stock_code}",
                "recommendations": []
            }
        
        # Calculate ranking score: Confidence × Lift
        relevant_rules['score'] = relevant_rules['confidence'] * relevant_rules['lift']
        relevant_rules = relevant_rules.sort_values('score', ascending=False).head(request.top_n)
        
        # Format recommendations
        recommendations = []
        rank = 1
        
        for _, rule in relevant_rules.iterrows():
            consequents = list(rule['consequents'])
            
            for consequent_code in consequents:
                # Get product description
                product_info = df[df['StockCode'] == consequent_code]
                if not product_info.empty:
                    description = product_info['Description'].iloc[0]
                    avg_price = product_info['UnitPrice'].mean()
                    
                    # Calculate expected impact (estimated additional revenue)
                    expected_impact = rule['confidence'] * avg_price * rule['support'] * 1000
                    
                    # Generate recommendation reason
                    if rule['lift'] > 3:
                        reason = "Strong association - frequently bought together"
                    elif rule['confidence'] > 0.7:
                        reason = "High confidence - customers who buy this often buy that"
                    else:
                        reason = "Good cross-sell opportunity"
                    
                    recommendations.append({
                        "rank": rank,
                        "stock_code": consequent_code,
                        "description": description,
                        "support": round(rule['support'], 4),
                        "confidence": round(rule['confidence'], 4),
                        "lift": round(rule['lift'], 4),
                        "expected_impact": round(expected_impact, 2),
                        "recommendation_reason": reason
                    })
                    
                    rank += 1
                    
                    if rank > request.top_n:
                        break
            
            if rank > request.top_n:
                break
        
        # Personalize if customer_id provided
        customer_segment = None
        if request.customer_id:
            # Get customer RFM segment (simplified)
            customer_segment = "Loyal Customer"  # Placeholder
        
        return {
            "success": True,
            "source_product": {
                "stock_code": request.stock_code,
                "description": source_description
            },
            "customer_segment": customer_segment,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.post("/cross-sell-insights")
async def get_cross_sell_insights(request: RecommendationRequest) -> Dict[str, Any]:
    """
    Get strategic insights for cross-selling
    """
    try:
        # Generate recommendations first
        recs = await generate_recommendations(request)
        
        if not recs.get("recommendations"):
            return {
                "success": True,
                "insights": {
                    "bundle_opportunity": "Insufficient data for bundle analysis",
                    "timing_strategy": "N/A",
                    "expected_aov_increase": 0.0
                }
            }
        
        recommendations = recs["recommendations"]
        
        # Calculate insights
        avg_confidence = np.mean([r['confidence'] for r in recommendations])
        avg_lift = np.mean([r['lift'] for r in recommendations])
        total_impact = sum([r['expected_impact'] for r in recommendations])
        
        # Bundle opportunity
        if avg_lift > 2.5:
            bundle_opp = "Strong bundle opportunity - Create product package with top recommendations"
        elif avg_lift > 1.5:
            bundle_opp = "Moderate bundle opportunity - Consider promotional bundling"
        else:
            bundle_opp = "Weak bundle signal - Focus on individual cross-sells"
        
        # Timing strategy
        if avg_confidence > 0.6:
            timing = "Recommend at checkout - High purchase probability"
        elif avg_confidence > 0.4:
            timing = "Recommend during browsing - Good upsell opportunity"
        else:
            timing = "Recommend post-purchase - Follow-up email campaign"
        
        # Expected AOV increase
        df = get_transactions_df()
        current_aov = df.groupby('InvoiceNo')['Revenue'].sum().mean()
        expected_increase = (total_impact / len(recommendations)) / current_aov * 100 if current_aov > 0 else 0
        
        return {
            "success": True,
            "source_product": recs["source_product"],
            "insights": {
                "bundle_opportunity": bundle_opp,
                "timing_strategy": timing,
                "expected_aov_increase": round(expected_increase, 2)
            },
            "metrics": {
                "avg_confidence": round(avg_confidence, 4),
                "avg_lift": round(avg_lift, 4),
                "total_expected_impact": round(total_impact, 2)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")

@app.post("/product-network")
async def get_product_network(
    stock_codes: List[str] = None,
    min_confidence: float = 0.3,
    max_products: int = 20
) -> Dict[str, Any]:
    """
    Generate product network graph showing associations
    """
    try:
        df = get_transactions_df()
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        # OPTIMIZATION: Limit to top products
        product_counts = df['StockCode'].value_counts()
        top_products = product_counts.head(100).index.tolist()
        df = df[df['StockCode'].isin(top_products)].copy()
        
        # Limit transactions
        df = df.nlargest(50000, 'InvoiceDate')
        
        # Create basket
        basket = df.groupby(['InvoiceNo', 'StockCode'])['Quantity'].sum().unstack().fillna(0)
        basket_encoded = basket.map(lambda x: 1 if x > 0 else 0)
        
        # Run Apriori
        frequent_itemsets = apriori(basket_encoded, min_support=0.01, use_colnames=True)
        
        if frequent_itemsets.empty:
            return {"success": True, "nodes": [], "edges": []}
        
        # Generate rules
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
        
        if rules.empty:
            return {"success": True, "nodes": [], "edges": []}
        
        # Filter by stock_codes if provided
        if stock_codes:
            rules = rules[
                rules['antecedents'].apply(lambda x: any(code in x for code in stock_codes)) |
                rules['consequents'].apply(lambda x: any(code in x for code in stock_codes))
            ]
        
        # Limit to top rules
        rules = rules.sort_values('lift', ascending=False).head(max_products)
        
        # Build nodes and edges
        nodes_dict = {}
        edges = []
        
        for _, rule in rules.iterrows():
            for item in rule['antecedents']:
                if item not in nodes_dict:
                    # Get product description
                    prod_info = df[df['StockCode'] == item]
                    desc = prod_info['Description'].iloc[0] if not prod_info.empty else item
                    revenue = prod_info['Revenue'].sum() if not prod_info.empty else 0
                    
                    nodes_dict[item] = {
                        "id": item,
                        "label": desc[:30],  # Truncate
                        "value": float(revenue)
                    }
            
            for item in rule['consequents']:
                if item not in nodes_dict:
                    prod_info = df[df['StockCode'] == item]
                    desc = prod_info['Description'].iloc[0] if not prod_info.empty else item
                    revenue = prod_info['Revenue'].sum() if not prod_info.empty else 0
                    
                    nodes_dict[item] = {
                        "id": item,
                        "label": desc[:30],
                        "value": float(revenue)
                    }
            
            # Create edges
            for ant in rule['antecedents']:
                for cons in rule['consequents']:
                    edges.append({
                        "source": ant,
                        "target": cons,
                        "confidence": round(rule['confidence'], 4),
                        "lift": round(rule['lift'], 4)
                    })
        
        return {
            "success": True,
            "nodes": list(nodes_dict.values()),
            "edges": edges,
            "total_nodes": len(nodes_dict),
            "total_edges": len(edges)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating network: {str(e)}")

@app.get("/customer-recommendations/{customer_id}")
async def get_customer_recommendations(
    customer_id: str,
    top_n: int = 5
) -> Dict[str, Any]:
    """
    Get personalized recommendations for a specific customer
    """
    try:
        df = get_transactions_df()
        
        # Get customer's purchase history
        customer_purchases = df[df['CustomerID'] == customer_id]['StockCode'].unique()
        
        if len(customer_purchases) == 0:
            raise HTTPException(status_code=404, detail="Customer not found or no purchase history")
        
        # Get recommendations for each purchased product
        all_recommendations = []
        
        for stock_code in customer_purchases[:5]:  # Limit to recent 5 products
            req = RecommendationRequest(
                stock_code=stock_code,
                customer_id=customer_id,
                top_n=3
            )
            
            recs = await generate_recommendations(req)
            if recs.get("recommendations"):
                all_recommendations.extend(recs["recommendations"])
        
        # Remove duplicates and rank by score
        seen = set()
        unique_recs = []
        for rec in all_recommendations:
            if rec['stock_code'] not in seen and rec['stock_code'] not in customer_purchases:
                seen.add(rec['stock_code'])
                unique_recs.append(rec)
        
        # Sort by confidence * lift and take top N
        unique_recs.sort(key=lambda x: x['confidence'] * x['lift'], reverse=True)
        unique_recs = unique_recs[:top_n]
        
        # Rerank
        for i, rec in enumerate(unique_recs, 1):
            rec['rank'] = i
        
        return {
            "success": True,
            "customer_id": customer_id,
            "purchase_history_count": len(customer_purchases),
            "recommendations": unique_recs,
            "total_recommendations": len(unique_recs)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting customer recommendations: {str(e)}")

@app.get("/top-bundles")
async def get_top_bundles(
    min_support: float = 0.01,
    min_confidence: float = 0.3,
    top_n: int = 10
) -> Dict[str, Any]:
    """
    Get top product bundles across all products
    """
    try:
        df = get_transactions_df()
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        # OPTIMIZATION: Limit to top products
        product_counts = df['StockCode'].value_counts()
        top_products = product_counts.head(100).index.tolist()
        df = df[df['StockCode'].isin(top_products)].copy()
        
        # Limit transactions
        df = df.nlargest(50000, 'InvoiceDate')
        
        # Create basket
        basket = df.groupby(['InvoiceNo', 'StockCode'])['Quantity'].sum().unstack().fillna(0)
        basket_encoded = basket.map(lambda x: 1 if x > 0 else 0)
        
        # Apriori
        frequent_itemsets = apriori(basket_encoded, min_support=min_support, use_colnames=True)
        
        if frequent_itemsets.empty:
            return {"success": True, "bundles": []}
        
        # Association rules
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
        
        if rules.empty:
            return {"success": True, "bundles": []}
        
        # Sort and get top
        rules['score'] = rules['confidence'] * rules['lift']
        rules = rules.sort_values('score', ascending=False).head(top_n)
        
        # Format bundles
        bundles = []
        for i, (_, rule) in enumerate(rules.iterrows(), 1):
            antecedents = list(rule['antecedents'])
            consequents = list(rule['consequents'])
            
            # Get descriptions
            ant_desc = []
            for code in antecedents:
                prod = df[df['StockCode'] == code]
                if not prod.empty:
                    ant_desc.append(prod['Description'].iloc[0])
            
            cons_desc = []
            for code in consequents:
                prod = df[df['StockCode'] == code]
                if not prod.empty:
                    cons_desc.append(prod['Description'].iloc[0])
            
            bundles.append({
                "rank": i,
                "antecedent_codes": antecedents,
                "consequent_codes": consequents,
                "antecedent_names": ant_desc,
                "consequent_names": cons_desc,
                "support": round(rule['support'], 4),
                "confidence": round(rule['confidence'], 4),
                "lift": round(rule['lift'], 4),
                "score": round(rule['score'], 4)
            })
        
        return {
            "success": True,
            "bundles": bundles,
            "total_bundles": len(bundles)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting top bundles: {str(e)}")

# ============ Run Server ============

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Sales API on port 8004...")
    print("🛍️ Role: Sales Manager - Cross-sell & Next Best Offer")
    print("📝 Documentation: http://localhost:8004/docs")
    print("🔍 Health check: http://localhost:8004/health")
    uvicorn.run(app, host="0.0.0.0", port=8004)
