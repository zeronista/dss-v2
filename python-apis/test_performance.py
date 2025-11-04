"""
Performance Test: Before and After Optimization
"""
import time
from db_utils import get_transactions_df, get_date_range_fast, get_db

print("=" * 70)
print("PERFORMANCE TEST: Database Query Optimization")
print("=" * 70)

# Test 1: Get date range (NEW optimized method)
print("\n1️⃣  Test: Get Date Range (Optimized Aggregation)")
print("-" * 70)
start = time.time()
date_info = get_date_range_fast()
elapsed = time.time() - start
print(f"⏱️  Time: {elapsed:.3f} seconds")
print(f"📅 Min Date: {date_info['min_date']}")
print(f"📅 Max Date: {date_info['max_date']}")

# Test 2: Load limited data (1000 records)
print("\n2️⃣  Test: Load 1,000 Transactions")
print("-" * 70)
start = time.time()
df_small = get_transactions_df(limit=1000)
elapsed = time.time() - start
print(f"⏱️  Time: {elapsed:.3f} seconds")
print(f"📊 Loaded: {len(df_small):,} records")
print(f"💾 Memory: {df_small.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")

# Test 3: Load 10,000 records
print("\n3️⃣  Test: Load 10,000 Transactions")
print("-" * 70)
start = time.time()
df_medium = get_transactions_df(limit=10000)
elapsed = time.time() - start
print(f"⏱️  Time: {elapsed:.3f} seconds")
print(f"📊 Loaded: {len(df_medium):,} records")
print(f"💾 Memory: {df_medium.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")

# Test 4: Load 50,000 records
print("\n4️⃣  Test: Load 50,000 Transactions")
print("-" * 70)
start = time.time()
df_large = get_transactions_df(limit=50000)
elapsed = time.time() - start
print(f"⏱️  Time: {elapsed:.3f} seconds")
print(f"📊 Loaded: {len(df_large):,} records")
print(f"💾 Memory: {df_large.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")

# Test 5: Count documents using MongoDB (very fast)
print("\n5️⃣  Test: Count Total Documents (MongoDB)")
print("-" * 70)
start = time.time()
db = get_db()
count = db['DSSFull'].count_documents({'InvoiceNo': {'$not': {'$regex': '^C'}}})
elapsed = time.time() - start
print(f"⏱️  Time: {elapsed:.3f} seconds")
print(f"📊 Total Valid Transactions: {count:,}")

# Test 6: Query with date filter (indexed field)
print("\n6️⃣  Test: Query with Date Filter (Using Index)")
print("-" * 70)
from datetime import datetime
start = time.time()
df_filtered = get_transactions_df(
    filters={
        'InvoiceDate': {
            '$gte': datetime(2011, 1, 1),
            '$lte': datetime(2011, 3, 31)
        }
    },
    limit=10000
)
elapsed = time.time() - start
print(f"⏱️  Time: {elapsed:.3f} seconds")
print(f"📊 Loaded: {len(df_filtered):,} records (Q1 2011)")

print("\n" + "=" * 70)
print("✅ PERFORMANCE TEST COMPLETE")
print("=" * 70)
print("\n💡 KEY RECOMMENDATIONS:")
print("   1. Always use 'limit' parameter when testing")
print("   2. Use date filters to reduce data load")
print("   3. Use get_date_range_fast() instead of loading all data")
print("   4. Indexes are now created for InvoiceNo, InvoiceDate, CustomerID, StockCode")
print("   5. For large queries, consider pagination or streaming")
print("\n⚠️  WARNING: Loading all 541K+ records will take significant time and memory!")
print("   Estimated: ~30-60 seconds, ~120-150 MB RAM")
print("=" * 70)
