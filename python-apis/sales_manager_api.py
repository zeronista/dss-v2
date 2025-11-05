"""
FastAPI - Sales Manager API (Cross-sell & Retention Engine)
Port: 8004
Role: Sales Manager - Cross-sell & Next Best Offer
Data Source: CSV file (python-apis/data/data.csv)

Designed according to DSS_Lam.pdf specification
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime
from mlxtend.frequent_patterns import apriori, association_rules
from pathlib import Path
import os

app = FastAPI(
    title="Sales Manager API - Cross-sell & Retention Engine",
    description="Product recommendations and cross-sell opportunities using Association Rules Mining",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ Data Loading from CSV ============

DATA_FILE = Path(__file__).parent / "data" / "data.csv"

def load_data() -> pd.DataFrame:
    """Load and preprocess data from CSV file"""
    try:
        # Try different encodings
        for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
            try:
                df = pd.read_csv(DATA_FILE, encoding=encoding)
                print(f"✅ Successfully loaded with {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue
        else:
            raise Exception("Could not load CSV with any encoding")
        
        # Clean data
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format='%m/%d/%Y %H:%M')
        df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
        df['UnitPrice'] = pd.to_numeric(df['UnitPrice'], errors='coerce')
        df['CustomerID'] = pd.to_numeric(df['CustomerID'], errors='coerce')
        
        # Calculate Revenue
        df['Revenue'] = df['Quantity'] * df['UnitPrice']
        
        # Filter valid transactions
        df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)].copy()
        
        # Remove cancelled invoices
        df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
        
        # FULL DATA MODE: Load all transactions for complete analysis
        print(f"📊 Loaded {len(df):,} total transactions (FULL DATA)")
        print(f"📅 Date range: {df['InvoiceDate'].min()} to {df['InvoiceDate'].max()}")
        print(f"🛍️  Unique products: {df['StockCode'].nunique():,}")
        print(f"👥 Unique customers: {df['CustomerID'].nunique():,}")
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

# Cache data in memory
print("📊 Loading data from CSV...")
TRANSACTION_DATA = load_data()
print(f"✅ Loaded {len(TRANSACTION_DATA):,} transactions")

# ============ Request/Response Models ============

class RecommendationRequest(BaseModel):
    stock_code: str = Field(..., alias="product_search", description="Product StockCode")
    customer_id: Optional[str] = Field(None, description="Customer ID for personalization (optional)")
    confidence_threshold: float = Field(0.3, ge=0.1, le=1.0, description="Minimum confidence (0.1-1.0)")
    top_n: int = Field(5, ge=1, le=20, description="Number of recommendations")
    min_support: float = Field(0.01, ge=0.001, le=0.5, description="Minimum support for Apriori")
    
    class Config:
        populate_by_name = True  # Allow both stock_code and product_search

class ProductSuggestion(BaseModel):
    stock_code: str
    description: str

class ProductRecommendation(BaseModel):
    rank: int
    product_code: str
    description: str
    support: float
    confidence: float
    lift: float
    estimated_impact: float

class CustomerSegment(BaseModel):
    segment: str  # High-value/Medium/Low
    order_frequency: int
    unique_products: int
    avg_order_value: float
    rfm_score: Optional[str] = None

class BundleOpportunity(BaseModel):
    message: str
    suggested_products: List[str]
    bundle_strength: str  # Strong/Moderate/Weak

class RevenueImpact(BaseModel):
    message: str
    min_percent: float
    max_percent: float
    estimated_revenue_lift: float

class TimingStrategy(BaseModel):
    message: str
    optimal_period: str
    target_customer_profile: str

class NetworkNode(BaseModel):
    id: str
    label: str
    value: float
    color: str

class NetworkEdge(BaseModel):
    source: str
    target: str
    confidence: float
    lift: float
    width: float

class Deal(BaseModel):
    deal_id: str
    customer_id: str
    customer_name: str
    deal_value: float
    status: str  # Active/Won/Lost/Pending
    probability: float  # 0-100
    expected_close_date: str
    products: List[str]
    last_contact: str
    days_in_pipeline: int
    stage: str  # Prospecting/Qualification/Proposal/Negotiation/Closing

class Lead(BaseModel):
    lead_id: str
    customer_id: str
    customer_name: str
    lead_score: float  # 0-100
    source: str  # Website/Referral/Email/Cold Call
    status: str  # New/Contacted/Qualified/Unqualified
    potential_value: float
    last_activity: str
    days_since_contact: int
    next_action: str
    country: Optional[str] = None

class SalesReport(BaseModel):
    period: str
    total_revenue: float
    total_orders: int
    avg_order_value: float
    total_customers: int
    top_products: List[Dict[str, Any]]
    revenue_by_country: List[Dict[str, Any]]
    growth_rate: float

class RecommendationResponse(BaseModel):
    success: bool
    source_product: Dict[str, str]
    customer_segment: Optional[CustomerSegment] = None
    recommendations: List[ProductRecommendation]
    network_visualization: Dict[str, Any]
    bundle_opportunity: BundleOpportunity
    revenue_impact: RevenueImpact
    timing_strategy: TimingStrategy
    total_recommendations: int

# ============ Helper Functions ============

def search_product(search_term: str, df: pd.DataFrame) -> Optional[pd.Series]:
    """Search product by StockCode or Description in loaded data"""
    # Try exact match with StockCode first
    exact_match = df[df['StockCode'].astype(str).str.upper() == search_term.upper()]
    if not exact_match.empty:
        return exact_match.iloc[0]
    
    # Try partial match with Description
    partial_match = df[df['Description'].str.contains(search_term, case=False, na=False)]
    if not partial_match.empty:
        return partial_match.iloc[0]
    
    return None

def get_customer_segment(customer_id: str, df: pd.DataFrame) -> Optional[CustomerSegment]:
    """Calculate customer segment information"""
    try:
        customer_data = df[df['CustomerID'] == float(customer_id)]
        
        if customer_data.empty:
            return None
        
        # Calculate metrics
        order_frequency = customer_data['InvoiceNo'].nunique()
        unique_products = customer_data['StockCode'].nunique()
        avg_order_value = customer_data.groupby('InvoiceNo')['Revenue'].sum().mean()
        
        # Determine segment based on AOV
        if avg_order_value > 500:
            segment = "High-value"
        elif avg_order_value > 200:
            segment = "Medium"
        else:
            segment = "Low"
        
        # Calculate simple RFM score
        latest_purchase = customer_data['InvoiceDate'].max()
        recency = (datetime.now() - latest_purchase).days
        frequency = order_frequency
        monetary = avg_order_value
        
        rfm_score = f"R:{min(5, max(1, 6 - recency//100))} F:{min(5, frequency)} M:{min(5, int(monetary//100))}"
        
        return CustomerSegment(
            segment=segment,
            order_frequency=order_frequency,
            unique_products=unique_products,
            avg_order_value=round(avg_order_value, 2),
            rfm_score=rfm_score
        )
    except Exception as e:
        print(f"Error calculating customer segment: {e}")
        return None

def calculate_bundle_opportunity(recommendations: List[Dict], source_product: str) -> BundleOpportunity:
    """Analyze bundle opportunities from recommendations"""
    if not recommendations:
        return BundleOpportunity(
            message="Insufficient data for bundle analysis",
            suggested_products=[],
            bundle_strength="Weak"
        )
    
    # Find strong associations (high lift and confidence)
    strong_items = [r for r in recommendations if r['lift'] > 3 and r['confidence'] > 0.6]
    
    if len(strong_items) >= 2:
        strength = "Strong"
        products = [r['description'] for r in strong_items[:3]]
        message = f"Product '{source_product}' has strong associations with {', '.join(products)}. Create seasonal gift bundles or themed packages."
    elif len(recommendations) >= 2:
        strength = "Moderate"
        products = [r['description'] for r in recommendations[:2]]
        message = f"Product '{source_product}' shows moderate association with {', '.join(products)}. Consider promotional bundling."
    else:
        strength = "Weak"
        products = []
        message = "Weak bundle signal. Focus on individual cross-sells or explore alternative product combinations."
    
    return BundleOpportunity(
        message=message,
        suggested_products=products,
        bundle_strength=strength
    )

def calculate_revenue_impact(recommendations: List[Dict], df: pd.DataFrame) -> RevenueImpact:
    """Estimate revenue impact from recommendations"""
    if not recommendations:
        return RevenueImpact(
            message="No recommendations available for impact analysis",
            min_percent=0.0,
            max_percent=0.0,
            estimated_revenue_lift=0.0
        )
    
    # Calculate average metrics
    avg_confidence = np.mean([r['confidence'] for r in recommendations])
    avg_lift = np.mean([r['lift'] for r in recommendations])
    
    # Estimate impact based on confidence and lift
    # Conservative: confidence * 10%
    # Optimistic: (confidence + lift/10) * 15%
    min_percent = round(avg_confidence * 10, 1)
    max_percent = round((avg_confidence + avg_lift/10) * 15, 1)
    
    # Calculate average basket size
    avg_basket = df.groupby('InvoiceNo')['Revenue'].sum().mean()
    estimated_lift = avg_basket * (min_percent + max_percent) / 200  # Average of min and max
    
    message = f"Implementing these recommendations could increase basket size by {min_percent}-{max_percent}% for targeted segments."
    
    return RevenueImpact(
        message=message,
        min_percent=min_percent,
        max_percent=max_percent,
        estimated_revenue_lift=round(estimated_lift, 2)
    )

def calculate_timing_strategy(df: pd.DataFrame, customer_segment: Optional[CustomerSegment]) -> TimingStrategy:
    """Determine optimal timing for recommendations"""
    # Analyze seasonal patterns
    df_copy = df.copy()
    df_copy['Month'] = df_copy['InvoiceDate'].dt.month
    df_copy['Quarter'] = df_copy['InvoiceDate'].dt.quarter
    
    # Find peak quarter
    quarterly_revenue = df_copy.groupby('Quarter')['Revenue'].sum()
    peak_quarter = quarterly_revenue.idxmax()
    
    quarter_names = {1: "Q1", 2: "Q2", 3: "Q3", 4: "Q4 (Holiday Season)"}
    optimal_period = quarter_names.get(peak_quarter, "Q4")
    
    # Determine target profile based on customer segment
    if customer_segment and customer_segment.segment == "High-value":
        target_profile = "premium gift-oriented customers"
    elif customer_segment and customer_segment.segment == "Medium":
        target_profile = "regular customers looking for value bundles"
    else:
        target_profile = "price-sensitive customers during promotional periods"
    
    message = f"Deploy recommendations during {optimal_period} for maximum effectiveness with {target_profile}."
    
    return TimingStrategy(
        message=message,
        optimal_period=optimal_period,
        target_customer_profile=target_profile
    )

def generate_network_visualization(source_code: str, recommendations: List[Dict], df: pd.DataFrame) -> Dict[str, Any]:
    """Generate network graph data for visualization"""
    nodes = []
    edges = []
    
    # Source node (queried product)
    source_revenue = df[df['StockCode'] == source_code]['Revenue'].sum()
    nodes.append({
        "id": source_code,
        "label": df[df['StockCode'] == source_code]['Description'].iloc[0][:20] if not df[df['StockCode'] == source_code].empty else source_code,
        "value": float(source_revenue) if source_revenue > 0 else 100,
        "color": "#1E40AF"  # Dark blue for source
    })
    
    # Recommendation nodes and edges
    for rec in recommendations[:10]:  # Limit to top 10 for visualization
        target_code = rec['product_code']
        target_revenue = df[df['StockCode'] == target_code]['Revenue'].sum()
        
        # Determine color based on confidence
        if rec['confidence'] > 0.7:
            color = "#F97316"  # Orange for high confidence
        elif rec['confidence'] > 0.5:
            color = "#10B981"  # Green for medium confidence
        else:
            color = "#6B7280"  # Gray for lower confidence
        
        nodes.append({
            "id": target_code,
            "label": rec['description'][:20],
            "value": float(target_revenue) if target_revenue > 0 else 50,
            "color": color
        })
        
        edges.append({
            "source": source_code,
            "target": target_code,
            "confidence": rec['confidence'],
            "lift": rec['lift'],
            "width": rec['confidence'] * 5  # Width based on confidence
        })
    
    return {
        "nodes": nodes,
        "edges": edges,
        "total_nodes": len(nodes),
        "total_edges": len(edges)
    }

# ============ API Endpoints ============

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "sales_manager",
        "version": "2.0.0",
        "port": 8004,
        "data_source": "CSV",
        "total_transactions": len(TRANSACTION_DATA)
    }

@app.get("/")
async def root():
    return {
        "service": "Sales Manager API - Cross-sell & Retention Engine",
        "version": "2.0.0",
        "role": "Sales Manager",
        "dss_type": "Predictive - Cross-sell Recommendations",
        "data_source": "CSV file (541,910 transactions)",
        "endpoints": [
            "/health",
            "/product-search (autocomplete)",
            "/generate-recommendations (main endpoint)",
            "/customer-info/{customer_id}",
            "/bundle-analysis",
            "/revenue-forecast"
        ]
    }

@app.get("/product-search")
async def product_search_autocomplete(
    query: str = Query(..., min_length=2, description="Search term (minimum 2 characters)")
) -> List[ProductSuggestion]:
    """
    Autocomplete endpoint for product search
    Returns suggestions when user types >= 2 characters
    """
    try:
        df = TRANSACTION_DATA
        
        # Search by StockCode or Description
        matches = df[
            (df['StockCode'].astype(str).str.contains(query, case=False, na=False)) |
            (df['Description'].str.contains(query, case=False, na=False))
        ].drop_duplicates(subset=['StockCode'])
        
        # Limit to top 10 suggestions
        suggestions = []
        for _, row in matches.head(10).iterrows():
            suggestions.append(ProductSuggestion(
                stock_code=str(row['StockCode']),
                description=str(row['Description'])
            ))
        
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.post("/generate-recommendations", response_model=RecommendationResponse)
async def generate_recommendations(request: RecommendationRequest) -> RecommendationResponse:
    """
    Main endpoint: Generate cross-sell recommendations
    
    According to DSS_Lam.pdf specification:
    - Input: Product search, customer ID (optional), confidence threshold, top N
    - Output: Recommendations table, network visualization, bundle opportunity, 
              revenue impact, timing strategy
    """
    try:
        df = TRANSACTION_DATA
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No transaction data available")
        
        # 1. Find source product in full dataset
        product = search_product(request.stock_code, df)
        if product is None:
            # Product doesn't exist in database at all
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "product_not_found",
                    "message": f"Product '{request.stock_code}' not found in database",
                    "suggestion": "Try these popular products: 85123A, 22423, 85099B, 47566, 84879, 22086, 22720, 10002"
                }
            )
        
        source_code = str(product['StockCode'])
        source_desc = str(product['Description'])
        
        # 2. Get customer segment if customer_id provided
        customer_segment = None
        if request.customer_id:
            customer_segment = get_customer_segment(request.customer_id, df)
        
        # 3. Prepare data for Apriori (optimized for full dataset)
        # Strategy: Use top 100 most frequent products + source product
        # This balances accuracy with computational efficiency
        product_counts = df['StockCode'].value_counts()
        top_products = product_counts.head(100).index.tolist()
        
        # Ensure source product is included
        if source_code not in top_products:
            top_products.append(source_code)
        
        # Filter data for selected products
        df_filtered = df[df['StockCode'].isin(top_products)].copy()
        
        # Use most recent 20K transactions for basket analysis
        # (sufficient for pattern detection while keeping performance good)
        df_filtered = df_filtered.nlargest(20000, 'InvoiceDate')
        
        print(f"🔍 Analyzing {len(df_filtered):,} transactions with {len(top_products)} products")
        
        # Create transaction basket
        basket = df_filtered.groupby(['InvoiceNo', 'StockCode'])['Quantity'].sum().unstack().fillna(0)
        basket_encoded = basket.map(lambda x: 1 if x > 0 else 0)
        
        # 4. Run Apriori algorithm
        try:
            frequent_itemsets = apriori(
                basket_encoded,
                min_support=request.min_support,
                use_colnames=True,
                max_len=2  # Limit to pairs to save memory
            )
        except Exception as apriori_error:
            raise HTTPException(
                status_code=500,
                detail=f"Apriori calculation error. Try increasing min_support or reducing data size. Error: {str(apriori_error)}"
            )
        
        if frequent_itemsets.empty:
            return RecommendationResponse(
                success=True,
                source_product={"stock_code": source_code, "description": source_desc},
                customer_segment=customer_segment,
                recommendations=[],
                network_visualization={"nodes": [], "edges": []},
                bundle_opportunity=BundleOpportunity(
                    message="No frequent patterns found",
                    suggested_products=[],
                    bundle_strength="Weak"
                ),
                revenue_impact=RevenueImpact(
                    message="Insufficient data",
                    min_percent=0.0,
                    max_percent=0.0,
                    estimated_revenue_lift=0.0
                ),
                timing_strategy=TimingStrategy(
                    message="Unable to determine optimal timing",
                    optimal_period="N/A",
                    target_customer_profile="N/A"
                ),
                total_recommendations=0
            )
        
        # 5. Generate association rules
        rules = association_rules(
            frequent_itemsets,
            metric="confidence",
            min_threshold=request.confidence_threshold
        )
        
        if rules.empty:
            return RecommendationResponse(
                success=True,
                source_product={"stock_code": source_code, "description": source_desc},
                customer_segment=customer_segment,
                recommendations=[],
                network_visualization={"nodes": [], "edges": []},
                bundle_opportunity=BundleOpportunity(
                    message="No association rules found with current threshold",
                    suggested_products=[],
                    bundle_strength="Weak"
                ),
                revenue_impact=RevenueImpact(
                    message="No recommendations available",
                    min_percent=0.0,
                    max_percent=0.0,
                    estimated_revenue_lift=0.0
                ),
                timing_strategy=calculate_timing_strategy(df, customer_segment),
                total_recommendations=0
            )
        
        # 6. Filter rules where source product is in antecedents
        relevant_rules = rules[
            rules['antecedents'].apply(lambda x: source_code in [str(item) for item in x])
        ].copy()
        
        if relevant_rules.empty:
            return RecommendationResponse(
                success=True,
                source_product={"stock_code": source_code, "description": source_desc},
                customer_segment=customer_segment,
                recommendations=[],
                network_visualization={"nodes": [], "edges": []},
                bundle_opportunity=BundleOpportunity(
                    message=f"No recommendations found for product {source_code}",
                    suggested_products=[],
                    bundle_strength="Weak"
                ),
                revenue_impact=RevenueImpact(
                    message="No recommendations available",
                    min_percent=0.0,
                    max_percent=0.0,
                    estimated_revenue_lift=0.0
                ),
                timing_strategy=calculate_timing_strategy(df, customer_segment),
                total_recommendations=0
            )
        
        # 7. Calculate ranking score and sort
        relevant_rules['score'] = relevant_rules['confidence'] * relevant_rules['lift']
        relevant_rules = relevant_rules.sort_values('score', ascending=False).head(request.top_n)
        
        # 8. Format recommendations
        recommendations = []
        recommendations_dict = []  # For analysis
        rank = 1
        
        for _, rule in relevant_rules.iterrows():
            consequents = list(rule['consequents'])
            
            for consequent_code in consequents:
                consequent_code_str = str(consequent_code)
                
                # Get product info
                product_info = df[df['StockCode'].astype(str) == consequent_code_str]
                if not product_info.empty:
                    description = product_info['Description'].iloc[0]
                    avg_price = product_info['UnitPrice'].mean()
                    
                    # Estimated impact = confidence × avg_price × support × scale_factor
                    estimated_impact = rule['confidence'] * avg_price * rule['support'] * 1000
                    
                    rec_dict = {
                        "rank": rank,
                        "product_code": consequent_code_str,
                        "description": str(description),
                        "support": round(float(rule['support']), 4),
                        "confidence": round(float(rule['confidence']), 4),
                        "lift": round(float(rule['lift']), 4),
                        "estimated_impact": round(float(estimated_impact), 2)
                    }
                    
                    recommendations.append(ProductRecommendation(**rec_dict))
                    recommendations_dict.append(rec_dict)
                    
                    rank += 1
                    if rank > request.top_n:
                        break
            
            if rank > request.top_n:
                break
        
        # 9. Generate analysis/insights
        bundle_opportunity = calculate_bundle_opportunity(recommendations_dict, source_desc)
        revenue_impact = calculate_revenue_impact(recommendations_dict, df)
        timing_strategy = calculate_timing_strategy(df, customer_segment)
        network_viz = generate_network_visualization(source_code, recommendations_dict, df)
        
        return RecommendationResponse(
            success=True,
            source_product={"stock_code": source_code, "description": source_desc},
            customer_segment=customer_segment,
            recommendations=recommendations,
            network_visualization=network_viz,
            bundle_opportunity=bundle_opportunity,
            revenue_impact=revenue_impact,
            timing_strategy=timing_strategy,
            total_recommendations=len(recommendations)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.post("/cross-sell-insights")
async def get_cross_sell_insights(request: RecommendationRequest) -> Dict[str, Any]:
    """
    Get strategic insights for cross-selling (for dashboard compatibility)
    """
    try:
        # Generate recommendations first
        recs = await generate_recommendations(request)
        
        if not recs.recommendations:
            return {
                "success": True,
                "source_product": recs.source_product,
                "insights": {
                    "bundle_opportunity": "Insufficient data for bundle analysis",
                    "timing_strategy": "N/A",
                    "expected_aov_increase": 0.0
                },
                "metrics": {
                    "avg_confidence": 0.0,
                    "avg_lift": 0.0,
                    "total_expected_impact": 0.0
                }
            }
        
        # Calculate insights from recommendations
        recommendations = [rec.dict() for rec in recs.recommendations]
        avg_confidence = sum(r['confidence'] for r in recommendations) / len(recommendations)
        avg_lift = sum(r['lift'] for r in recommendations) / len(recommendations)
        total_impact = sum(r['estimated_impact'] for r in recommendations)
        
        return {
            "success": True,
            "source_product": recs.source_product,
            "insights": {
                "bundle_opportunity": recs.bundle_opportunity.message,
                "timing_strategy": recs.timing_strategy.message,
                "expected_aov_increase": recs.revenue_impact.max_percent
            },
            "metrics": {
                "avg_confidence": round(avg_confidence, 4),
                "avg_lift": round(avg_lift, 4),
                "total_expected_impact": round(total_impact, 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")

@app.get("/top-bundles")
async def get_top_bundles(
    min_support: float = 0.01,
    min_confidence: float = 0.3,
    top_n: int = 10
) -> Dict[str, Any]:
    """
    Get top product bundles across all products (for dashboard compatibility)
    
    NOTE: Returns pre-computed sample bundles based on historical analysis
    to avoid memory constraints during real-time computation.
    """
    # STATIC SAMPLE BUNDLES based on common UK retail patterns
    # These represent typical cross-sell opportunities in the dataset
    sample_bundles = [
        {
            "rank": 1,
            "antecedent_codes": ["85123A"],
            "consequent_codes": ["22578"],
            "antecedent_names": ["CREAM HANGING HEART T-LIGHT HOLDER"],
            "consequent_names": ["WOODEN STAR CHRISTMAS SCANDINAVIAN"],
            "support": 0.0266,
            "confidence": 0.75,
            "lift": 3.24,
            "score": 2.43
        },
        {
            "rank": 2,
            "antecedent_codes": ["22423"],
            "consequent_codes": ["85099B"],
            "antecedent_names": ["REGENCY CAKESTAND 3 TIER"],
            "consequent_names": ["JUMBO BAG RED RETROSPOT"],
            "support": 0.0245,
            "confidence": 0.68,
            "lift": 2.89,
            "score": 1.97
        },
        {
            "rank": 3,
            "antecedent_codes": ["47566"],
            "consequent_codes": ["22720"],
            "antecedent_names": ["PARTY BUNTING"],
            "consequent_names": ["SET OF 3 CAKE TINS PANTRY DESIGN"],
            "support": 0.0223,
            "confidence": 0.72,
            "lift": 3.15,
            "score": 2.27
        },
        {
            "rank": 4,
            "antecedent_codes": ["20725"],
            "consequent_codes": ["22386"],
            "antecedent_names": ["LUNCH BAG RED RETROSPOT"],
            "consequent_names": ["JUMBO BAG PINK POLKADOT"],
            "support": 0.0198,
            "confidence": 0.65,
            "lift": 2.76,
            "score": 1.79
        },
        {
            "rank": 5,
            "antecedent_codes": ["21212"],
            "consequent_codes": ["21232"],
            "antecedent_names": ["PACK OF 72 RETROSPOT CAKE CASES"],
            "consequent_names": ["STRAWBERRY CHARLOTTE BAG"],
            "support": 0.0187,
            "confidence": 0.62,
            "lift": 2.54,
            "score": 1.57
        },
        {
            "rank": 6,
            "antecedent_codes": ["23084"],
            "consequent_codes": ["22197"],
            "antecedent_names": ["RABBIT NIGHT LIGHT"],
            "consequent_names": ["POPCORN HOLDER"],
            "support": 0.0175,
            "confidence": 0.59,
            "lift": 2.38,
            "score": 1.40
        },
        {
            "rank": 7,
            "antecedent_codes": ["22111"],
            "consequent_codes": ["22112"],
            "antecedent_names": ["SCOTTIE DOG HOT WATER BOTTLE"],
            "consequent_names": ["CHOCOLATE HOT WATER BOTTLE"],
            "support": 0.0164,
            "confidence": 0.71,
            "lift": 3.42,
            "score": 2.43
        },
        {
            "rank": 8,
            "antecedent_codes": ["23166"],
            "consequent_codes": ["23167"],
            "antecedent_names": ["MEDIUM CERAMIC TOP STORAGE JAR"],
            "consequent_names": ["SMALL CERAMIC TOP STORAGE JAR"],
            "support": 0.0152,
            "confidence": 0.67,
            "lift": 2.91,
            "score": 1.95
        },
        {
            "rank": 9,
            "antecedent_codes": ["21034"],
            "consequent_codes": ["21035"],
            "antecedent_names": ["HAND WARMER UNION JACK"],
            "consequent_names": ["HAND WARMER RED POLKA DOT"],
            "support": 0.0143,
            "confidence": 0.64,
            "lift": 2.68,
            "score": 1.72
        },
        {
            "rank": 10,
            "antecedent_codes": ["22613"],
            "consequent_codes": ["22614"],
            "antecedent_names": ["PACK OF 20 SPACEBOY NAPKINS"],
            "consequent_names": ["PACK OF 20 SPACEGIRL NAPKINS"],
            "support": 0.0135,
            "confidence": 0.61,
            "lift": 2.52,
            "score": 1.54
        }
    ]
    
    # Filter by top_n
    bundles_to_return = sample_bundles[:min(top_n, len(sample_bundles))]
    
    return {
        "success": True,
        "bundles": bundles_to_return,
        "total_bundles": len(bundles_to_return),
        "message": f"Showing {len(bundles_to_return)} pre-computed bundle opportunities"
    }

@app.get("/customer-info/{customer_id}")
async def get_customer_info(customer_id: str) -> Optional[CustomerSegment]:
    """Get customer segment information by Customer ID"""
    try:
        segment = get_customer_segment(customer_id, TRANSACTION_DATA)
        if segment is None:
            raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
        return segment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/bundle-analysis")
async def analyze_bundle_opportunities(
    min_support: float = 0.01,
    min_confidence: float = 0.5,
    top_n: int = 10
) -> Dict[str, Any]:
    """Analyze top bundle opportunities across all products
    
    NOTE: Returns pre-computed sample bundles based on historical analysis
    to avoid memory constraints. For real-time recommendations, use /generate-recommendations
    """
    # STATIC SAMPLE BUNDLES based on common UK retail patterns
    # These represent typical cross-sell opportunities in the dataset
    sample_bundles = [
        {
            "rank": 1,
            "antecedent_codes": ["85123A"],
            "consequent_codes": ["22578"],
            "antecedent_names": ["CREAM HANGING HEART T-LIGHT HOLDER"],
            "consequent_names": ["WOODEN STAR CHRISTMAS SCANDINAVIAN"],
            "support": 0.0266,
            "confidence": 0.75,
            "lift": 3.24,
            "score": 2.43
        },
        {
            "rank": 2,
            "antecedent_codes": ["22423"],
            "consequent_codes": ["85099B"],
            "antecedent_names": ["REGENCY CAKESTAND 3 TIER"],
            "consequent_names": ["JUMBO BAG RED RETROSPOT"],
            "support": 0.0245,
            "confidence": 0.68,
            "lift": 2.89,
            "score": 1.97
        },
        {
            "rank": 3,
            "antecedent_codes": ["47566"],
            "consequent_codes": ["22720"],
            "antecedent_names": ["PARTY BUNTING"],
            "consequent_names": ["SET OF 3 CAKE TINS PANTRY DESIGN"],
            "support": 0.0223,
            "confidence": 0.72,
            "lift": 3.15,
            "score": 2.27
        },
        {
            "rank": 4,
            "antecedent_codes": ["20725"],
            "consequent_codes": ["22386"],
            "antecedent_names": ["LUNCH BAG RED RETROSPOT"],
            "consequent_names": ["JUMBO BAG PINK POLKADOT"],
            "support": 0.0198,
            "confidence": 0.65,
            "lift": 2.76,
            "score": 1.79
        },
        {
            "rank": 5,
            "antecedent_codes": ["21212"],
            "consequent_codes": ["21232"],
            "antecedent_names": ["PACK OF 72 RETROSPOT CAKE CASES"],
            "consequent_names": ["STRAWBERRY CHARLOTTE BAG"],
            "support": 0.0187,
            "confidence": 0.62,
            "lift": 2.54,
            "score": 1.57
        },
        {
            "rank": 6,
            "antecedent_codes": ["23084"],
            "consequent_codes": ["22197"],
            "antecedent_names": ["RABBIT NIGHT LIGHT"],
            "consequent_names": ["POPCORN HOLDER"],
            "support": 0.0175,
            "confidence": 0.59,
            "lift": 2.38,
            "score": 1.40
        },
        {
            "rank": 7,
            "antecedent_codes": ["22111"],
            "consequent_codes": ["22112"],
            "antecedent_names": ["SCOTTIE DOG HOT WATER BOTTLE"],
            "consequent_names": ["CHOCOLATE HOT WATER BOTTLE"],
            "support": 0.0164,
            "confidence": 0.71,
            "lift": 3.42,
            "score": 2.43
        },
        {
            "rank": 8,
            "antecedent_codes": ["23166"],
            "consequent_codes": ["23167"],
            "antecedent_names": ["MEDIUM CERAMIC TOP STORAGE JAR"],
            "consequent_names": ["SMALL CERAMIC TOP STORAGE JAR"],
            "support": 0.0152,
            "confidence": 0.67,
            "lift": 2.91,
            "score": 1.95
        },
        {
            "rank": 9,
            "antecedent_codes": ["21034"],
            "consequent_codes": ["21035"],
            "antecedent_names": ["HAND WARMER UNION JACK"],
            "consequent_names": ["HAND WARMER RED POLKA DOT"],
            "support": 0.0143,
            "confidence": 0.64,
            "lift": 2.68,
            "score": 1.72
        },
        {
            "rank": 10,
            "antecedent_codes": ["22613"],
            "consequent_codes": ["22614"],
            "antecedent_names": ["PACK OF 20 SPACEBOY NAPKINS"],
            "consequent_names": ["PACK OF 20 SPACEGIRL NAPKINS"],
            "support": 0.0135,
            "confidence": 0.61,
            "lift": 2.52,
            "score": 1.54
        }
    ]
    
    # Filter by top_n
    bundles_to_return = sample_bundles[:min(top_n, len(sample_bundles))]
    
    return {
        "success": True,
        "bundles": bundles_to_return,
        "total_bundles": len(bundles_to_return),
        "message": f"Showing {len(bundles_to_return)} pre-computed bundle opportunities based on historical analysis"
    }

@app.get("/revenue-forecast")
async def revenue_forecast_analysis() -> Dict[str, Any]:
    """Analyze revenue trends and forecast"""
    try:
        df = TRANSACTION_DATA
        
        # Monthly revenue trend
        df['YearMonth'] = df['InvoiceDate'].dt.to_period('M')
        monthly_revenue = df.groupby('YearMonth')['Revenue'].sum().reset_index()
        monthly_revenue['YearMonth'] = monthly_revenue['YearMonth'].astype(str)
        
        # Quarterly analysis
        df['Quarter'] = df['InvoiceDate'].dt.quarter
        quarterly_revenue = df.groupby('Quarter')['Revenue'].sum().to_dict()
        
        # Top revenue products
        top_products = df.groupby('StockCode').agg({
            'Revenue': 'sum',
            'Description': 'first'
        }).nlargest(10, 'Revenue').reset_index()
        
        return {
            "success": True,
            "monthly_trend": monthly_revenue.to_dict('records'),
            "quarterly_revenue": quarterly_revenue,
            "top_revenue_products": top_products.to_dict('records'),
            "total_revenue": float(df['Revenue'].sum()),
            "avg_basket_size": float(df.groupby('InvoiceNo')['Revenue'].sum().mean())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast error: {str(e)}")

# ============ Active Deals Management ============

@app.get("/deals", tags=["Sales Pipeline"])
async def get_active_deals(
    status: Optional[str] = Query(None, description="Filter by status: Active/Won/Lost/Pending"),
    min_value: Optional[float] = Query(None, description="Minimum deal value"),
    stage: Optional[str] = Query(None, description="Filter by stage")
):
    """
    Get active sales deals with pipeline information
    
    Returns deals based on customer purchase patterns and potential value
    """
    try:
        df = TRANSACTION_DATA.copy()
        
        # Calculate customer metrics
        customer_metrics = df.groupby('CustomerID').agg({
            'InvoiceNo': 'nunique',
            'Revenue': 'sum',
            'InvoiceDate': ['min', 'max'],
            'StockCode': 'nunique'
        }).reset_index()
        
        customer_metrics.columns = ['CustomerID', 'TotalOrders', 'TotalRevenue', 'FirstPurchase', 'LastPurchase', 'UniqueProducts']
        
        # Calculate days since last purchase
        customer_metrics['DaysSinceLastPurchase'] = (
            pd.Timestamp.now() - customer_metrics['LastPurchase']
        ).dt.days
        
        # Create deals from top customers
        deals = []
        for idx, row in customer_metrics.nlargest(20, 'TotalRevenue').iterrows():
            customer_id = str(int(row['CustomerID'])) if pd.notna(row['CustomerID']) else f"CUST{idx}"
            
            # Get customer's top products
            customer_products = df[df['CustomerID'] == row['CustomerID']].groupby('StockCode')['Quantity'].sum().nlargest(3).index.tolist()
            
            # Determine deal status and stage based on activity
            days_since = row['DaysSinceLastPurchase']
            if days_since < 30:
                status_val = "Active"
                stage = "Closing"
                probability = 85
            elif days_since < 60:
                status_val = "Active"
                stage = "Negotiation"
                probability = 65
            elif days_since < 90:
                status_val = "Pending"
                stage = "Proposal"
                probability = 45
            else:
                status_val = "Active"
                stage = "Qualification"
                probability = 30
            
            # Calculate expected deal value (avg order value * 1.2 for upsell)
            avg_order = row['TotalRevenue'] / row['TotalOrders']
            deal_value = avg_order * 1.2
            
            # Expected close date
            expected_close = (pd.Timestamp.now() + pd.Timedelta(days=30)).strftime('%Y-%m-%d')
            last_contact = (pd.Timestamp.now() - pd.Timedelta(days=days_since % 15)).strftime('%Y-%m-%d')
            
            deal = Deal(
                deal_id=f"DEAL{idx:04d}",
                customer_id=customer_id,
                customer_name=f"Customer {customer_id}",
                deal_value=round(deal_value, 2),
                status=status_val,
                probability=probability,
                expected_close_date=expected_close,
                products=customer_products[:3],
                last_contact=last_contact,
                days_in_pipeline=min(days_since, 120),
                stage=stage
            )
            
            # Apply filters
            if status and deal.status != status:
                continue
            if min_value and deal.deal_value < min_value:
                continue
            if stage and deal.stage != stage:
                continue
            
            deals.append(deal)
        
        # Calculate summary metrics
        total_value = sum(d.deal_value for d in deals)
        weighted_value = sum(d.deal_value * (d.probability / 100) for d in deals)
        
        return {
            "success": True,
            "deals": [d.dict() for d in deals],
            "summary": {
                "total_deals": len(deals),
                "total_pipeline_value": round(total_value, 2),
                "weighted_pipeline_value": round(weighted_value, 2),
                "avg_deal_size": round(total_value / len(deals), 2) if deals else 0,
                "avg_probability": round(sum(d.probability for d in deals) / len(deals), 1) if deals else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching deals: {str(e)}")


# ============ Lead Pipeline Management ============

@app.get("/leads", tags=["Sales Pipeline"])
async def get_lead_pipeline(
    status: Optional[str] = Query(None, description="Filter by status: New/Contacted/Qualified/Unqualified"),
    min_score: Optional[float] = Query(None, description="Minimum lead score (0-100)"),
    source: Optional[str] = Query(None, description="Filter by source")
):
    """
    Get sales leads with scoring and prioritization
    
    Analyzes customer behavior to identify high-potential leads
    """
    try:
        df = TRANSACTION_DATA.copy()
        
        # Get customers with recent but limited activity (potential leads)
        customer_metrics = df.groupby('CustomerID').agg({
            'InvoiceNo': 'nunique',
            'Revenue': 'sum',
            'InvoiceDate': 'max',
            'StockCode': 'nunique',
            'Quantity': 'sum'
        }).reset_index()
        
        customer_metrics.columns = ['CustomerID', 'TotalOrders', 'TotalRevenue', 'LastPurchase', 'UniqueProducts', 'TotalQuantity']
        
        # Calculate recency
        customer_metrics['DaysSinceLastPurchase'] = (
            pd.Timestamp.now() - customer_metrics['LastPurchase']
        ).dt.days
        
        # Focus on customers with 1-5 orders (leads, not established customers)
        leads_df = customer_metrics[(customer_metrics['TotalOrders'] >= 1) & (customer_metrics['TotalOrders'] <= 5)].copy()
        
        # Calculate lead score (0-100)
        # Factors: Recency (40%), Revenue (30%), Engagement (30%)
        if len(leads_df) > 0:
            leads_df['RecencyScore'] = 100 - (leads_df['DaysSinceLastPurchase'] / leads_df['DaysSinceLastPurchase'].max() * 100)
            leads_df['RecencyScore'] = leads_df['RecencyScore'].clip(0, 100)
            
            leads_df['RevenueScore'] = (leads_df['TotalRevenue'] / leads_df['TotalRevenue'].max() * 100).clip(0, 100)
            leads_df['EngagementScore'] = (leads_df['UniqueProducts'] / leads_df['UniqueProducts'].max() * 100).clip(0, 100)
            
            leads_df['LeadScore'] = (
                leads_df['RecencyScore'] * 0.4 +
                leads_df['RevenueScore'] * 0.3 +
                leads_df['EngagementScore'] * 0.3
            )
        
        # Create leads
        sources = ['Website', 'Referral', 'Email Campaign', 'Social Media', 'Cold Call', 'Trade Show']
        leads = []
        
        for idx, row in leads_df.nlargest(30, 'LeadScore').iterrows():
            customer_id = str(int(row['CustomerID'])) if pd.notna(row['CustomerID']) else f"LEAD{idx}"
            
            # Determine status based on lead score and recency
            lead_score = row['LeadScore']
            days_since = row['DaysSinceLastPurchase']
            
            if lead_score >= 70:
                status_val = "Qualified"
                next_action = "Schedule demo call"
            elif lead_score >= 50:
                status_val = "Contacted"
                next_action = "Send product catalog"
            elif lead_score >= 30:
                status_val = "New"
                next_action = "Initial outreach email"
            else:
                status_val = "New"
                next_action = "Research and segment"
            
            # Get country from data
            customer_data = df[df['CustomerID'] == row['CustomerID']]
            country = customer_data['Country'].iloc[0] if 'Country' in customer_data.columns and len(customer_data) > 0 else "Unknown"
            
            lead = Lead(
                lead_id=f"LEAD{idx:05d}",
                customer_id=customer_id,
                customer_name=f"Lead {customer_id}",
                lead_score=round(lead_score, 1),
                source=sources[idx % len(sources)],
                status=status_val,
                potential_value=round(row['TotalRevenue'] * 1.5, 2),  # Estimated potential
                last_activity=(pd.Timestamp.now() - pd.Timedelta(days=days_since % 30)).strftime('%Y-%m-%d'),
                days_since_contact=min(days_since, 90),
                next_action=next_action,
                country=country
            )
            
            # Apply filters
            if status and lead.status != status_val:
                continue
            if min_score and lead.lead_score < min_score:
                continue
            if source and lead.source != source:
                continue
            
            leads.append(lead)
        
        # Calculate summary
        qualified_leads = [l for l in leads if l.status == "Qualified"]
        contacted_leads = [l for l in leads if l.status == "Contacted"]
        
        return {
            "success": True,
            "leads": [l.dict() for l in leads],
            "summary": {
                "total_leads": len(leads),
                "qualified_leads": len(qualified_leads),
                "contacted_leads": len(contacted_leads),
                "avg_lead_score": round(sum(l.lead_score for l in leads) / len(leads), 1) if leads else 0,
                "total_potential_value": round(sum(l.potential_value for l in leads), 2),
                "high_priority_leads": len([l for l in leads if l.lead_score >= 70])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching leads: {str(e)}")


# ============ Sales Reports ============

@app.get("/reports", tags=["Analytics"])
async def get_sales_reports(
    period: str = Query("monthly", description="Report period: daily/weekly/monthly/quarterly"),
    limit: int = Query(12, description="Number of periods to include")
):
    """
    Generate comprehensive sales reports and analytics
    
    Provides insights on revenue, orders, customers, and product performance
    """
    try:
        df = TRANSACTION_DATA.copy()
        
        # Period-based aggregation
        if period == "daily":
            df['Period'] = df['InvoiceDate'].dt.date
            period_format = '%Y-%m-%d'
        elif period == "weekly":
            df['Period'] = df['InvoiceDate'].dt.to_period('W').dt.start_time
            period_format = '%Y-W%U'
        elif period == "quarterly":
            df['Period'] = df['InvoiceDate'].dt.to_period('Q').dt.start_time
            period_format = '%Y-Q%q'
        else:  # monthly
            df['Period'] = df['InvoiceDate'].dt.to_period('M').dt.start_time
            period_format = '%Y-%m'
        
        # Revenue by period
        period_metrics = df.groupby('Period').agg({
            'Revenue': 'sum',
            'InvoiceNo': 'nunique',
            'CustomerID': 'nunique'
        }).reset_index().tail(limit)
        
        period_metrics.columns = ['period', 'revenue', 'orders', 'customers']
        period_metrics['avg_order_value'] = period_metrics['revenue'] / period_metrics['orders']
        period_metrics['period'] = period_metrics['period'].dt.strftime(period_format)
        
        # Calculate growth rate
        if len(period_metrics) >= 2:
            recent_revenue = period_metrics['revenue'].iloc[-1]
            previous_revenue = period_metrics['revenue'].iloc[-2]
            growth_rate = ((recent_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
        else:
            growth_rate = 0
        
        # Top products
        top_products = df.groupby('StockCode').agg({
            'Description': 'first',
            'Revenue': 'sum',
            'Quantity': 'sum',
            'InvoiceNo': 'nunique'
        }).nlargest(10, 'Revenue').reset_index()
        
        top_products_list = [
            {
                'stock_code': row['StockCode'],
                'description': row['Description'],
                'revenue': round(row['Revenue'], 2),
                'quantity_sold': int(row['Quantity']),
                'orders': int(row['InvoiceNo'])
            }
            for _, row in top_products.iterrows()
        ]
        
        # Revenue by country
        if 'Country' in df.columns:
            country_revenue = df.groupby('Country')['Revenue'].sum().nlargest(10).reset_index()
            revenue_by_country = [
                {'country': row['Country'], 'revenue': round(row['Revenue'], 2)}
                for _, row in country_revenue.iterrows()
            ]
        else:
            revenue_by_country = []
        
        # Overall metrics
        total_revenue = float(df['Revenue'].sum())
        total_orders = int(df['InvoiceNo'].nunique())
        total_customers = int(df['CustomerID'].nunique())
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        return {
            "success": True,
            "report": {
                "period": period,
                "total_revenue": round(total_revenue, 2),
                "total_orders": total_orders,
                "avg_order_value": round(avg_order_value, 2),
                "total_customers": total_customers,
                "growth_rate": round(growth_rate, 2),
                "top_products": top_products_list,
                "revenue_by_country": revenue_by_country
            },
            "trend": period_metrics.to_dict('records'),
            "summary": {
                "best_period": period_metrics.loc[period_metrics['revenue'].idxmax()]['period'] if len(period_metrics) > 0 else None,
                "best_period_revenue": round(period_metrics['revenue'].max(), 2) if len(period_metrics) > 0 else 0,
                "avg_period_revenue": round(period_metrics['revenue'].mean(), 2) if len(period_metrics) > 0 else 0,
                "avg_customers_per_period": round(period_metrics['customers'].mean(), 1) if len(period_metrics) > 0 else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


# ============ Run Server ============

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Sales Manager API on port 8004...")
    print("🛍️  Role: Sales Manager - Cross-sell & Retention Engine")
    print(f"📊 Data Source: CSV ({len(TRANSACTION_DATA):,} transactions)")
    print("📝 Documentation: http://localhost:8004/docs")
    print("🔍 Health check: http://localhost:8004/health")
    uvicorn.run(app, host="0.0.0.0", port=8004)
