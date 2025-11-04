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
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from mlxtend.frequent_patterns import apriori, association_rules

# Import database utilities
from db_utils import get_transactions_df, get_customers_rfm, get_db, filter_by_date_range

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

class RFMRequest(BaseModel):
    start_date: Optional[str] = Field(None, description="Start date for analysis (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date for analysis (YYYY-MM-DD)")
    save_to_db: bool = Field(False, description="Save results to MongoDB")

class SegmentationRequest(BaseModel):
    n_segments: int = Field(3, ge=2, le=10, description="Number of customer segments")
    use_existing_rfm: bool = Field(True, description="Use pre-calculated RFM or calculate fresh")
    start_date: Optional[str] = Field(None, description="Start date for analysis (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date for analysis (YYYY-MM-DD)")

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
    start_date: Optional[str] = Field(None, description="Start date for analysis (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date for analysis (YYYY-MM-DD)")

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
            "/date-range-info",
            "/calculate-rfm",
            "/calculate-rfm-advanced",
            "/run-segmentation",
            "/segment-overview",
            "/segment-basket-analysis",
            "/market-basket-analysis",
            "/product-bundles"
        ]
    }

def calculate_quantiles(rfm: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Calculate RFM quantiles for heuristic naming (PHASE 1)
    
    Args:
        rfm: DataFrame with Recency, Frequency, Monetary columns
    
    Returns:
        Dictionary with quantile values for each metric
    """
    quantiles = {}
    
    for col in ['Recency', 'Frequency', 'Monetary']:
        q = rfm[col].quantile([0.25, 0.5, 0.75])
        quantiles[col.lower()] = {
            'q25': round(q[0.25], 2),
            'q50': round(q[0.5], 2),
            'q75': round(q[0.75], 2)
        }
    
    return quantiles

def segment_label(row: pd.Series, quantiles: Dict[str, Dict[str, float]]) -> str:
    """
    Heuristic segment naming based on RFM characteristics (PHASE 2)
    From your Streamlit app logic
    
    Rules:
    - Champions: R ≤ q25 AND F ≥ q75 AND M ≥ q75
    - Loyal: R ≤ q50 AND F ≥ q50
    - At-Risk: R ≥ q75 AND F ≤ q25
    - Hibernating: R ≥ q50 AND F ≤ q50
    - Regulars: (default)
    
    Args:
        row: DataFrame row with Recency, Frequency, Monetary values
        quantiles: Dictionary with quantile values
    
    Returns:
        Segment name
    """
    r_q25 = quantiles['recency']['q25']
    r_q50 = quantiles['recency']['q50']
    r_q75 = quantiles['recency']['q75']
    f_q25 = quantiles['frequency']['q25']
    f_q50 = quantiles['frequency']['q50']
    f_q75 = quantiles['frequency']['q75']
    m_q75 = quantiles['monetary']['q75']
    
    # Champions: Recent buyers, frequent, high monetary
    if (row['Recency'] <= r_q25 and 
        row['Frequency'] >= f_q75 and 
        row['Monetary'] >= m_q75):
        return "Champions"
    
    # Loyal: Recent enough, frequent enough
    elif row['Recency'] <= r_q50 and row['Frequency'] >= f_q50:
        return "Loyal"
    
    # At-Risk: Long time no purchase, low frequency
    elif row['Recency'] >= r_q75 and row['Frequency'] <= f_q25:
        return "At-Risk"
    
    # Hibernating: Not recent, low frequency
    elif row['Recency'] >= r_q50 and row['Frequency'] <= f_q50:
        return "Hibernating"
    
    # Regulars: Everyone else
    else:
        return "Regulars"

def segment_characteristics(seg_name: str, avg_recency: float, avg_frequency: float, avg_monetary: float) -> str:
    """
    Generate detailed description of segment characteristics (PHASE 2)
    From your Streamlit app
    
    Args:
        seg_name: Segment name
        avg_recency: Average recency in days
        avg_frequency: Average frequency (orders)
        avg_monetary: Average monetary value
    
    Returns:
        Detailed characteristic description
    """
    characteristics = {
        "Champions": f"🏆 **Nhóm khách hàng VIP nhất của bạn!** Họ mua hàng thường xuyên (trung bình {avg_frequency:.1f} đơn/khách), chi tiêu cao ({avg_monetary:,.0f} đơn vị tiền tệ) và vừa mới quay lại ({avg_recency:.0f} ngày trước). Đây là nhóm đem lại giá trị cao nhất và cần được chăm sóc đặc biệt để duy trì lòng trung thành.",
        
        "Loyal": f"💎 **Khách hàng trung thành đáng tin cậy.** Họ có tần suất mua hàng tốt ({avg_frequency:.1f} đơn) và chi tiêu ổn định ({avg_monetary:,.0f}). Recency trung bình là {avg_recency:.0f} ngày. Nhóm này có tiềm năng trở thành Champions nếu được kích thích đúng cách.",
        
        "At-Risk": f"⚠️ **Nhóm có nguy cơ rời bỏ cao!** Họ đã lâu không quay lại mua hàng (trung bình {avg_recency:.0f} ngày) và có tần suất mua thấp ({avg_frequency:.1f} đơn). Dù từng có giá trị ({avg_monetary:,.0f}), họ đang dần mất kết nối với thương hiệu. **Cần hành động ngay** để tái kích hoạt nhóm này.",
        
        "Hibernating": f"😴 **Khách hàng đang 'ngủ đông'.** Họ đã rất lâu không quay lại ({avg_recency:.0f} ngày) và có tần suất mua thấp ({avg_frequency:.1f} đơn). Chi tiêu trung bình {avg_monetary:,.0f}. Cần chiến dịch remarketing mạnh mẽ để đánh thức nhóm này.",
        
        "Regulars": f"👥 **Khách hàng thường xuyên ổn định.** Họ mua hàng đều đặn với recency {avg_recency:.0f} ngày, frequency {avg_frequency:.1f} đơn và chi tiêu {avg_monetary:,.0f}. Đây là backbone của doanh nghiệp - cần duy trì và nâng cao giá trị của họ."
    }
    
    return characteristics.get(seg_name, f"Phân khúc khách hàng với Recency {avg_recency:.0f} ngày, Frequency {avg_frequency:.1f} đơn, Monetary {avg_monetary:,.0f}.")

def segment_rules_text(seg_name: str) -> List[str]:
    """
    Get recommended marketing actions for each segment (PHASE 2)
    From your Streamlit app
    
    Args:
        seg_name: Segment name
    
    Returns:
        List of recommended actions
    """
    mapping = {
        "Champions": [
            "Ưu đãi VIP/early access",
            "Chương trình giới thiệu bạn bè",
            "Tích điểm và upgrade thành viên"
        ],
        "Loyal": [
            "Tích điểm, upsell gói sản phẩm",
            "Ưu đãi sinh nhật",
            "Chương trình giữ chân khách hàng"
        ],
        "At-Risk": [
            "Email 'Chúng tôi nhớ bạn' + mã giảm giá 15%",
            "Reactivation bundle giá tốt",
            "Survey để hiểu lý do churn"
        ],
        "Hibernating": [
            "Chiến dịch quay lại (remarketing)",
            "Miễn phí vận chuyển",
            "Limited time offer với ưu đãi lớn"
        ],
        "Regulars": [
            "Khuyến mãi định kỳ",
            "Cross-sell sản phẩm bổ trợ",
            "Loyalty tier program"
        ]
    }
    
    return mapping.get(seg_name, ["Khuyến mãi chung", "A/B test các offers khác nhau"])

@app.get("/date-range-info")
async def get_date_range_info() -> Dict[str, Any]:
    """
    Get available date range from transaction data (PHASE 1)
    """
    try:
        df = get_transactions_df()
        
        if df.empty or 'InvoiceDate' not in df.columns:
            raise HTTPException(status_code=404, detail="No transaction data found")
        
        min_date = df['InvoiceDate'].min()
        max_date = df['InvoiceDate'].max()
        
        # Default: last 12 months from max date
        default_start = max_date - timedelta(days=365)
        
        return {
            "min_date": min_date.strftime('%Y-%m-%d'),
            "max_date": max_date.strftime('%Y-%m-%d'),
            "default_start": default_start.strftime('%Y-%m-%d'),
            "default_end": max_date.strftime('%Y-%m-%d'),
            "total_days": (max_date - min_date).days
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting date range: {str(e)}")

@app.post("/calculate-rfm")
async def calculate_rfm() -> Dict[str, Any]:
    """
    Calculate RFM (Recency, Frequency, Monetary) scores for all customers
    LEGACY ENDPOINT - Use /calculate-rfm-advanced for enhanced features
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
        
        # FIX: Use labels=False to avoid quantile mismatch error
        rfm['R_Score'] = pd.qcut(rfm['Recency'], q=5, labels=False, duplicates='drop') + 1
        rfm['R_Score'] = 6 - rfm['R_Score']  # Reverse: lower recency = higher score
        
        rfm['F_Score'] = pd.qcut(rfm['Frequency'], q=5, labels=False, duplicates='drop') + 1
        rfm['M_Score'] = pd.qcut(rfm['Monetary'], q=5, labels=False, duplicates='drop') + 1
        
        # Calculate RFM Score
        rfm['RFM_Score'] = rfm['R_Score'] + rfm['F_Score'] + rfm['M_Score']
        
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

@app.post("/calculate-rfm-advanced")
async def calculate_rfm_advanced(request: RFMRequest) -> Dict[str, Any]:
    """
    Calculate RFM with advanced features (PHASE 1)
    - Date range filtering
    - Quantile calculation
    - Optional save to MongoDB
    """
    try:
        # Get all transactions
        df = get_transactions_df()
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No transaction data found")
        
        # Apply date filtering if provided
        if request.start_date or request.end_date:
            df = filter_by_date_range(df, request.start_date, request.end_date)
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No transactions in selected date range")
        
        # Get the reference date (latest transaction date + 1 day)
        reference_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
        
        # Calculate RFM
        rfm = df.groupby('CustomerID').agg({
            'InvoiceDate': lambda x: (reference_date - x.max()).days,  # Recency
            'InvoiceNo': 'nunique',  # Frequency
            'Revenue': 'sum'  # Monetary
        }).reset_index()
        
        rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']
        
        # Calculate quantiles for heuristic naming
        quantiles = calculate_quantiles(rfm)
        
        # Calculate RFM scores (fixed to avoid quantile mismatch)
        rfm['R_Score'] = pd.qcut(rfm['Recency'], q=5, labels=False, duplicates='drop') + 1
        rfm['R_Score'] = 6 - rfm['R_Score']  # Reverse: lower recency = higher score
        
        rfm['F_Score'] = pd.qcut(rfm['Frequency'], q=5, labels=False, duplicates='drop') + 1
        rfm['M_Score'] = pd.qcut(rfm['Monetary'], q=5, labels=False, duplicates='drop') + 1
        
        # Calculate RFM Score
        rfm['RFM_Score'] = rfm['R_Score'] + rfm['F_Score'] + rfm['M_Score']
        
        # Save to MongoDB if requested
        if request.save_to_db:
            db = get_db()
            rfm_dict = rfm.to_dict('records')
            # Clear existing RFM data
            db['customer_rfm'].delete_many({})
            # Insert new data
            db['customer_rfm'].insert_many(rfm_dict)
        
        # Determine date range for response
        actual_start = df['InvoiceDate'].min().strftime('%Y-%m-%d')
        actual_end = df['InvoiceDate'].max().strftime('%Y-%m-%d')
        
        return {
            "success": True,
            "message": "Advanced RFM calculation completed",
            "customers_analyzed": len(rfm),
            "date_range": {
                "start": actual_start,
                "end": actual_end,
                "total_days": (df['InvoiceDate'].max() - df['InvoiceDate'].min()).days
            },
            "quantiles": quantiles,
            "summary": {
                "avg_recency": round(rfm['Recency'].mean(), 2),
                "avg_frequency": round(rfm['Frequency'].mean(), 2),
                "avg_monetary": round(rfm['Monetary'].mean(), 2),
                "median_recency": round(rfm['Recency'].median(), 2),
                "median_frequency": round(rfm['Frequency'].median(), 2),
                "median_monetary": round(rfm['Monetary'].median(), 2)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating advanced RFM: {str(e)}")

@app.post("/run-segmentation")
async def run_segmentation(request: SegmentationRequest) -> Dict[str, Any]:
    """
    Run customer segmentation using heuristic RFM-based naming (PHASE 2)
    Uses your Streamlit app's 5-category logic
    """
    try:
        # Get transactions
        df = get_transactions_df()
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No transaction data found")
        
        # Apply date filtering if provided (PHASE 1 feature)
        if request.start_date or request.end_date:
            df = filter_by_date_range(df, request.start_date, request.end_date)
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No transactions in selected date range")
        
        # Calculate RFM
        reference_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
        rfm = df.groupby('CustomerID').agg({
            'InvoiceDate': lambda x: (reference_date - x.max()).days,
            'InvoiceNo': 'nunique',
            'Revenue': 'sum'
        }).reset_index()
        rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']
        
        if rfm.empty or len(rfm) < 5:
            raise HTTPException(status_code=400, detail="Not enough data for segmentation")
        
        # Calculate quantiles for heuristic naming
        quantiles = calculate_quantiles(rfm)
        
        # Apply heuristic segment naming (PHASE 2)
        rfm['SegmentName'] = rfm.apply(lambda row: segment_label(row, quantiles), axis=1)
        
        # Build segment summary
        segment_summary = []
        for seg_name in ['Champions', 'Loyal', 'At-Risk', 'Hibernating', 'Regulars']:
            seg_data = rfm[rfm['SegmentName'] == seg_name]
            
            if len(seg_data) == 0:
                continue  # Skip empty segments
            
            avg_r = seg_data['Recency'].mean()
            avg_f = seg_data['Frequency'].mean()
            avg_m = seg_data['Monetary'].mean()
            total_value = seg_data['Monetary'].sum()
            
            # Get characteristics and recommendations (PHASE 2)
            characteristics = segment_characteristics(seg_name, avg_r, avg_f, avg_m)
            actions = segment_rules_text(seg_name)
            
            segment_summary.append({
                "segment_id": ['Champions', 'Loyal', 'At-Risk', 'Hibernating', 'Regulars'].index(seg_name),
                "segment_name": seg_name,
                "customer_count": int(len(seg_data)),
                "avg_recency": round(avg_r, 2),
                "avg_frequency": round(avg_f, 2),
                "avg_monetary": round(avg_m, 2),
                "total_value": round(total_value, 2),
                "characteristics": characteristics,
                "recommended_actions": actions
            })
        
        # Sort by total value (descending)
        segment_summary.sort(key=lambda x: x['total_value'], reverse=True)
        
        return {
            "success": True,
            "n_segments": len(segment_summary),
            "total_customers": len(rfm),
            "date_range": {
                "start": df['InvoiceDate'].min().strftime('%Y-%m-%d'),
                "end": df['InvoiceDate'].max().strftime('%Y-%m-%d')
            },
            "quantiles": quantiles,
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

def get_lift_strength(lift: float) -> str:
    """
    Get visual indicator for lift value (PHASE 3)
    
    Args:
        lift: Lift value from association rules
    
    Returns:
        Emoji indicator
    """
    if lift > 2.0:
        return "🔥"  # Very strong association
    elif lift > 1.5:
        return "✅"  # Good association
    else:
        return "➡️"  # Moderate association

def format_product_display(product_name: str, stock_code: str = None, max_length: int = 50) -> str:
    """
    Format product name for display (PHASE 3)
    Truncate long names and optionally add stock code
    
    Args:
        product_name: Product description
        stock_code: Stock code (optional)
        max_length: Maximum length for product name
    
    Returns:
        Formatted product string
    """
    if not product_name:
        return "Unknown Product"
    
    # Truncate if too long
    if len(str(product_name)) > max_length:
        product_name = str(product_name)[:max_length-3] + "..."
    
    # Add stock code if provided
    if stock_code:
        return f"{product_name} ({stock_code})"
    
    return str(product_name)

def create_stock_to_description_mapping(df: pd.DataFrame) -> Dict[str, str]:
    """
    Create mapping from StockCode to Description (PHASE 3)
    
    Args:
        df: DataFrame with StockCode and Description columns
    
    Returns:
        Dictionary mapping stock codes to descriptions
    """
    if 'StockCode' not in df.columns or 'Description' not in df.columns:
        return {}
    
    # Get the most common description for each stock code
    mapping = df.groupby('StockCode')['Description'].agg(
        lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0]
    ).to_dict()
    
    return mapping

@app.post("/segment-basket-analysis")
async def segment_basket_analysis(
    segment_name: str,
    min_support: float = 0.01,
    min_confidence: float = 0.3,
    top_n: int = 10,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Market Basket Analysis for a specific customer segment (PHASE 3, Enhanced in PHASE 4)
    
    Args:
        segment_name: Name of segment (Champions, Loyal, At-Risk, Hibernating, Regulars)
        min_support: Minimum support threshold
        min_confidence: Minimum confidence threshold
        top_n: Number of top bundles to return
        start_date: Start date for filtering transactions (YYYY-MM-DD)
        end_date: End date for filtering transactions (YYYY-MM-DD)
    """
    try:
        # Get all transactions
        df = get_transactions_df()
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No transaction data found")
        
        # Apply date filtering if provided (PHASE 4)
        if start_date or end_date:
            df = filter_by_date_range(df, start_date, end_date)
        
        # Run segmentation to get customer IDs for the segment
        reference_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
        rfm = df.groupby('CustomerID').agg({
            'InvoiceDate': lambda x: (reference_date - x.max()).days,
            'InvoiceNo': 'nunique',
            'Revenue': 'sum'
        }).reset_index()
        rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']
        
        # Calculate quantiles and apply segment labels
        quantiles = calculate_quantiles(rfm)
        rfm['SegmentName'] = rfm.apply(lambda row: segment_label(row, quantiles), axis=1)
        
        # Get customer IDs for the specified segment
        segment_customers = set(rfm[rfm['SegmentName'] == segment_name]['CustomerID'])
        
        if not segment_customers:
            raise HTTPException(status_code=404, detail=f"No customers found in segment '{segment_name}'")
        
        # Filter transactions to only include segment customers
        seg_df = df[df['CustomerID'].isin(segment_customers)].copy()
        
        if seg_df.empty:
            raise HTTPException(status_code=404, detail=f"No transactions for segment '{segment_name}'")
        
        # Create stock code to description mapping
        stock_to_desc = create_stock_to_description_mapping(seg_df)
        
        # OPTIMIZATION: Limit to top products by frequency in this segment
        product_counts = seg_df['Description'].value_counts()
        top_products = product_counts.head(200).index.tolist()
        seg_df = seg_df[seg_df['Description'].isin(top_products)].copy()
        
        # Create basket (one-hot encoding by Description)
        basket = seg_df.groupby(['InvoiceNo', 'Description'])['Quantity'].sum().unstack().fillna(0)
        basket_encoded = basket.map(lambda x: 1 if x > 0 else 0)
        
        # Run Apriori algorithm
        frequent_itemsets = apriori(
            basket_encoded,
            min_support=min_support,
            use_colnames=True
        )
        
        if frequent_itemsets.empty:
            return {
                "success": True,
                "segment": segment_name,
                "customer_count": len(segment_customers),
                "message": "No frequent itemsets found. Try lowering min_support.",
                "bundles": []
            }
        
        # Generate association rules
        rules = association_rules(
            frequent_itemsets,
            metric="confidence",
            min_threshold=min_confidence
        )
        
        if rules.empty:
            return {
                "success": True,
                "segment": segment_name,
                "customer_count": len(segment_customers),
                "message": "No rules found. Try lowering min_confidence.",
                "bundles": []
            }
        
        # Sort by confidence and lift
        rules = rules.sort_values(['confidence', 'lift'], ascending=False).head(top_n)
        
        # Format results with product descriptions
        bundles = []
        for _, rule in rules.iterrows():
            antecedents_list = list(rule['antecedents'])
            consequents_list = list(rule['consequents'])
            
            # Format product displays
            ant_display = ", ".join([format_product_display(p) for p in antecedents_list])
            cons_display = ", ".join([format_product_display(p) for p in consequents_list])
            
            # Get lift strength indicator
            lift_val = float(rule['lift'])
            strength = get_lift_strength(lift_val)
            
            # Calculate expected revenue
            consequent_revenue = seg_df[
                seg_df['Description'].isin(consequents_list)
            ]['Revenue'].mean() if len(consequents_list) > 0 else 0
            
            expected_revenue = consequent_revenue * rule['confidence'] * rule['support'] * len(seg_df)
            
            bundles.append({
                "antecedents": antecedents_list,
                "consequents": consequents_list,
                "antecedents_display": ant_display,
                "consequents_display": cons_display,
                "support": round(float(rule['support']), 4),
                "confidence": round(float(rule['confidence']), 4),
                "lift": round(lift_val, 4),
                "strength": strength,
                "expected_revenue": round(expected_revenue, 2)
            })
        
        # Get top recommendation
        top_recommendation = bundles[0] if bundles else None
        
        # Get date range for response (PHASE 4)
        date_range_info = {
            "start_date": df['InvoiceDate'].min().strftime('%Y-%m-%d'),
            "end_date": df['InvoiceDate'].max().strftime('%Y-%m-%d'),
            "filtered": bool(start_date or end_date)
        }
        
        return {
            "success": True,
            "segment": segment_name,
            "customer_count": len(segment_customers),
            "total_bundles_found": len(rules),
            "displayed_bundles": len(bundles),
            "date_range": date_range_info,
            "top_recommendation": top_recommendation,
            "bundles": bundles,
            "parameters": {
                "min_support": min_support,
                "min_confidence": min_confidence,
                "top_n": top_n
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in segment basket analysis: {str(e)}")

@app.post("/market-basket-analysis")
async def market_basket_analysis(request: BasketAnalysisRequest) -> Dict[str, Any]:
    """
    Run Market Basket Analysis (Apriori Algorithm) for all customers (PHASE 3, Enhanced in PHASE 4)
    """
    try:
        df = get_transactions_df()
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No transaction data found")
        
        # Apply date filtering if provided (PHASE 4)
        if request.start_date or request.end_date:
            df = filter_by_date_range(df, request.start_date, request.end_date)
        
        # OPTIMIZATION: Limit to top N products by frequency
        product_counts = df['Description'].value_counts()
        top_products = product_counts.head(200).index.tolist()
        df = df[df['Description'].isin(top_products)].copy()
        
        # Limit transactions to most recent
        df = df.nlargest(50000, 'InvoiceDate')
        
        # Create basket (one-hot encoding)
        basket = df.groupby(['InvoiceNo', 'Description'])['Quantity'].sum().unstack().fillna(0)
        basket_encoded = basket.map(lambda x: 1 if x > 0 else 0)
        
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
        
        # Sort by lift and confidence
        rules = rules.sort_values(['lift', 'confidence'], ascending=False).head(request.top_n)
        
        # Format results with enhanced display (PHASE 3)
        bundles = []
        for _, rule in rules.iterrows():
            antecedents_list = list(rule['antecedents'])
            consequents_list = list(rule['consequents'])
            
            # Format product displays
            ant_display = ", ".join([format_product_display(p) for p in antecedents_list])
            cons_display = ", ".join([format_product_display(p) for p in consequents_list])
            
            # Get lift strength
            lift_val = float(rule['lift'])
            strength = get_lift_strength(lift_val)
            
            # Calculate expected revenue
            consequent_revenue = df[
                df['Description'].isin(consequents_list)
            ]['Revenue'].mean() if len(consequents_list) > 0 else 0
            
            expected_revenue = consequent_revenue * rule['confidence'] * rule['support'] * len(df)
            
            bundles.append({
                "antecedents": antecedents_list,
                "consequents": consequents_list,
                "antecedents_display": ant_display,
                "consequents_display": cons_display,
                "support": round(float(rule['support']), 4),
                "confidence": round(float(rule['confidence']), 4),
                "lift": round(lift_val, 4),
                "strength": strength,
                "expected_revenue": round(expected_revenue, 2)
            })
        
        # Get top recommendation
        top_recommendation = bundles[0] if bundles else None
        
        # Get date range for response (PHASE 4)
        date_range_info = {
            "start_date": df['InvoiceDate'].min().strftime('%Y-%m-%d'),
            "end_date": df['InvoiceDate'].max().strftime('%Y-%m-%d'),
            "filtered": bool(request.start_date or request.end_date)
        }
        
        return {
            "success": True,
            "total_rules": len(rules),
            "total_bundles_found": len(rules),
            "displayed_bundles": len(bundles),
            "date_range": date_range_info,
            "top_recommendation": top_recommendation,
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
    top_n: int = 10,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get recommended product bundles based on Market Basket Analysis (PHASE 3, Enhanced in PHASE 4)
    Convenience endpoint for market basket analysis with date filtering support
    """
    try:
        request = BasketAnalysisRequest(
            min_support=min_support,
            min_confidence=min_confidence,
            top_n=top_n,
            start_date=start_date,
            end_date=end_date
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
