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

def get_transactions_df(filters: Dict[str, Any] = None, exclude_cancelled: bool = True) -> pd.DataFrame:
    """
    Get transactions from MongoDB as pandas DataFrame
    
    Args:
        filters: MongoDB query filters
        exclude_cancelled: Exclude cancelled invoices (InvoiceNo starts with 'C')
    
    Returns:
        pandas DataFrame with transactions
    """
    db = get_db()
    collection = db['DSS']  # Main transaction collection
    
    # Build query
    query = filters or {}
    
    if exclude_cancelled:
        query['InvoiceNo'] = {'$not': {'$regex': '^C'}}
    
    # Get data
    cursor = collection.find(query)
    df = pd.DataFrame(list(cursor))
    
    # Data cleaning
    if not df.empty:
        # Remove _id column if exists
        if '_id' in df.columns:
            df = df.drop('_id', axis=1)
        
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
    
    return df

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
    
    # Test getting transactions
    print("\n🔍 Testing get_transactions_df...")
    df = get_transactions_df()
    print(f"Total transactions: {len(df)}")
    if not df.empty:
        print(df.head())
