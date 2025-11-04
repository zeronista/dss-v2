"""
Database Utilities - MongoDB Connection
Shared across all FastAPI services
"""

from pymongo import MongoClient
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime
import os

# MongoDB Connection String
MONGO_URI = "mongodb+srv://vuthanhlam848:vuthanhlam848@cluster0.s9cdtme.mongodb.net/DSS"
DATABASE_NAME = "DSS"

class MongoDBClient:
    """MongoDB client singleton"""
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBClient, cls).__new__(cls)
            cls._client = MongoClient(MONGO_URI)
            cls._db = cls._client[DATABASE_NAME]
        return cls._instance
    
    @property
    def db(self):
        """Get database instance"""
        return self._db
    
    @property
    def client(self):
        """Get MongoDB client"""
        return self._client
    
    def close(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()

def get_db():
    """Get database instance"""
    mongo = MongoDBClient()
    return mongo.db

def get_transactions_df(filters: Dict[str, Any] = None, exclude_cancelled: bool = True, 
                       limit: int = None, projection: Dict[str, int] = None,
                       batch_size: int = 10000) -> pd.DataFrame:
    """
    Get transactions from MongoDB as pandas DataFrame (OPTIMIZED)
    
    Args:
        filters: MongoDB query filters
        exclude_cancelled: Exclude cancelled invoices (InvoiceNo starts with 'C')
        limit: Maximum number of documents to fetch (None = all, use with caution)
        projection: Fields to include/exclude (e.g., {'_id': 0, 'InvoiceNo': 1})
        batch_size: Cursor batch size for memory efficiency
    
    Returns:
        pandas DataFrame with transactions
    """
    db = get_db()
    collection = db['DSSFull']  # Main transaction collection
    
    # Build query
    query = filters or {}
    
    if exclude_cancelled:
        query['InvoiceNo'] = {'$not': {'$regex': '^C'}}
    
    # Default projection (exclude _id)
    if projection is None:
        projection = {'_id': 0}
    
    # Get data with optimization
    cursor = collection.find(query, projection).batch_size(batch_size)
    
    if limit:
        cursor = cursor.limit(limit)
    
    # Use list comprehension for better memory efficiency with large datasets
    print(f"📊 Fetching transactions from MongoDB (limit={limit if limit else 'all'})...")
    
    # For very large datasets, fetch in chunks
    if limit is None or limit > 50000:
        print("⚠️  Warning: Fetching large dataset. Consider using filters or limit parameter.")
        print(f"💡 Tip: Use limit parameter for testing, e.g., get_transactions_df(limit=10000)")
    
    df = pd.DataFrame(list(cursor))
    
    # Data cleaning
    if not df.empty:
        # Convert InvoiceDate to datetime if it's string
        if 'InvoiceDate' in df.columns and df['InvoiceDate'].dtype == 'object':
            df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
        
        # Ensure numeric columns
        if 'Quantity' in df.columns:
            df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
        if 'UnitPrice' in df.columns:
            df['UnitPrice'] = pd.to_numeric(df['UnitPrice'], errors='coerce')
        
        # Calculate Revenue if not exists
        if 'Revenue' not in df.columns and 'Quantity' in df.columns and 'UnitPrice' in df.columns:
            df['Revenue'] = df['Quantity'] * df['UnitPrice']
        
        # Filter valid transactions
        df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)].copy()
    
    print(f"✅ Loaded {len(df)} transactions")
    return df

def filter_by_date_range(df: pd.DataFrame, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    Filter transactions by date range (PHASE 1 - Enhanced RFM)
    
    Args:
        df: DataFrame with InvoiceDate column
        start_date: Start date in 'YYYY-MM-DD' format (optional)
        end_date: End date in 'YYYY-MM-DD' format (optional)
    
    Returns:
        Filtered DataFrame
    """
    if df.empty:
        return df
    
    # Ensure InvoiceDate is datetime
    if 'InvoiceDate' in df.columns:
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # Apply filters
    if start_date:
        df = df[df['InvoiceDate'] >= pd.to_datetime(start_date)]
    
    if end_date:
        # Include the entire end date (up to 23:59:59)
        end_datetime = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        df = df[df['InvoiceDate'] <= end_datetime]
    
    return df.copy()

def get_date_range_fast() -> Dict[str, Any]:
    """
    Get min/max dates from transactions using MongoDB aggregation (OPTIMIZED)
    Much faster than loading all data
    
    Returns:
        Dictionary with min_date, max_date
    """
    db = get_db()
    collection = db['DSSFull']
    
    # Use aggregation to get min/max dates efficiently
    pipeline = [
        {
            '$match': {
                'InvoiceNo': {'$not': {'$regex': '^C'}},
                'Quantity': {'$gt': 0},
                'UnitPrice': {'$gt': 0}
            }
        },
        {
            '$group': {
                '_id': None,
                'min_date': {'$min': '$InvoiceDate'},
                'max_date': {'$max': '$InvoiceDate'}
            }
        }
    ]
    
    result = list(collection.aggregate(pipeline))
    
    if result:
        min_date = result[0]['min_date']
        max_date = result[0]['max_date']
        
        # Convert to datetime if string
        if isinstance(min_date, str):
            min_date = pd.to_datetime(min_date)
        if isinstance(max_date, str):
            max_date = pd.to_datetime(max_date)
        
        return {
            'min_date': min_date,
            'max_date': max_date
        }
    
    return {'min_date': None, 'max_date': None}

def get_collection_stats(collection_name: str = 'DSSFull') -> Dict[str, Any]:
    """
    Get collection statistics (DIAGNOSTIC TOOL)
    
    Args:
        collection_name: Name of collection to analyze
    
    Returns:
        Statistics including document count, size, indexes
    """
    db = get_db()
    collection = db[collection_name]
    
    # Get collection stats
    stats = db.command('collStats', collection_name)
    
    # Get indexes
    indexes = list(collection.list_indexes())
    
    return {
        'collection': collection_name,
        'document_count': stats.get('count', 0),
        'size_mb': stats.get('size', 0) / (1024 * 1024),
        'avg_doc_size_bytes': stats.get('avgObjSize', 0),
        'indexes': [{'name': idx['name'], 'keys': idx['key']} for idx in indexes]
    }

def create_recommended_indexes():
    """
    Create recommended indexes for better query performance
    """
    db = get_db()
    collection = db['DSSFull']
    
    print("📑 Creating recommended indexes...")
    
    # Index on InvoiceNo for cancelled invoice filtering
    collection.create_index([('InvoiceNo', 1)], background=True)
    print("✅ Created index on InvoiceNo")
    
    # Index on InvoiceDate for date range queries
    collection.create_index([('InvoiceDate', 1)], background=True)
    print("✅ Created index on InvoiceDate")
    
    # Index on CustomerID for customer queries
    collection.create_index([('CustomerID', 1)], background=True)
    print("✅ Created index on CustomerID")
    
    # Index on StockCode for product queries
    collection.create_index([('StockCode', 1)], background=True)
    print("✅ Created index on StockCode")
    
    # Compound index for common query patterns
    collection.create_index([('InvoiceDate', 1), ('CustomerID', 1)], background=True)
    print("✅ Created compound index on InvoiceDate + CustomerID")
    
    print("🎉 All indexes created successfully!")

def filter_by_date_range(df: pd.DataFrame, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    Filter transactions by date range (PHASE 1 - Enhanced RFM)
    
    Args:
        df: DataFrame with InvoiceDate column
        start_date: Start date in 'YYYY-MM-DD' format (optional)
        end_date: End date in 'YYYY-MM-DD' format (optional)
    
    Returns:
        Filtered DataFrame
    """
    if df.empty:
        return df
    
    # Ensure InvoiceDate is datetime
    if 'InvoiceDate' in df.columns:
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # Apply filters
    if start_date:
        df = df[df['InvoiceDate'] >= pd.to_datetime(start_date)]
    
    if end_date:
        # Include the entire end date (up to 23:59:59)
        end_datetime = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        df = df[df['InvoiceDate'] <= end_datetime]
    
    return df.copy()

def get_customers_rfm(as_dataframe: bool = True) -> pd.DataFrame | List[Dict]:
    """
    Get RFM scores from MongoDB
    
    Args:
        as_dataframe: Return as DataFrame or list of dicts
    
    Returns:
        RFM data as DataFrame or list
    """
    db = get_db()
    collection = db['customer_rfm']  # Adjust collection name if different
    
    cursor = collection.find({})
    data = list(cursor)
    
    if as_dataframe:
        df = pd.DataFrame(data)
        if not df.empty and '_id' in df.columns:
            df = df.drop('_id', axis=1)
        return df
    
    return data

def save_results(collection_name: str, data: List[Dict[str, Any]]) -> bool:
    """
    Save results back to MongoDB
    
    Args:
        collection_name: Name of the collection
        data: List of documents to save
    
    Returns:
        Success status
    """
    try:
        db = get_db()
        collection = db[collection_name]
        
        if data:
            # Add timestamp
            for doc in data:
                doc['created_at'] = datetime.utcnow()
            
            # Insert or update
            collection.insert_many(data)
        
        return True
    except Exception as e:
        print(f"Error saving to MongoDB: {e}")
        return False

def get_product_info(stock_code: str = None) -> pd.DataFrame:
    """
    Get product information
    
    Args:
        stock_code: Specific product code (optional)
    
    Returns:
        Product info DataFrame
    """
    db = get_db()
    collection = db['products']  # Adjust collection name if different
    
    query = {}
    if stock_code:
        query['StockCode'] = stock_code
    
    cursor = collection.find(query)
    df = pd.DataFrame(list(cursor))
    
    if not df.empty and '_id' in df.columns:
        df = df.drop('_id', axis=1)
    
    return df

def test_connection():
    """Test MongoDB connection"""
    try:
        db = get_db()
        # Ping the database
        db.command('ping')
        print("✅ MongoDB connection successful!")
        
        # List collections
        collections = db.list_collection_names()
        print(f"📦 Available collections: {collections}")
        
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

if __name__ == "__main__":
    # Test connection
    test_connection()
    
    # Get collection statistics
    print("\n📊 Collection Statistics:")
    stats = get_collection_stats('DSSFull')
    print(f"Collection: {stats['collection']}")
    print(f"Document Count: {stats['document_count']:,}")
    print(f"Size: {stats['size_mb']:.2f} MB")
    print(f"Avg Document Size: {stats['avg_doc_size_bytes']:.2f} bytes")
    print(f"\n📑 Indexes:")
    for idx in stats['indexes']:
        print(f"  - {idx['name']}: {idx['keys']}")
    
    # Test getting date range (fast method)
    print("\n📅 Getting date range (optimized)...")
    date_info = get_date_range_fast()
    print(f"Min Date: {date_info['min_date']}")
    print(f"Max Date: {date_info['max_date']}")
    
    # Test getting transactions with LIMIT
    print("\n🔍 Testing get_transactions_df with limit=1000...")
    df = get_transactions_df(limit=1000)
    print(f"Loaded {len(df)} transactions")
    if not df.empty:
        print("\nFirst 5 rows:")
        print(df.head())
        print(f"\nColumns: {list(df.columns)}")
        print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    
    # Uncomment to create indexes (run once)
    # print("\n📑 Creating indexes...")
    # create_recommended_indexes()
