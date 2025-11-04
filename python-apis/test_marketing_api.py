"""
Quick Test: Marketing API with Optimized Database
"""
import sys
import asyncio

# Test if we can import everything
print("=" * 70)
print("TESTING: Marketing API Import & Basic Functions")
print("=" * 70)

try:
    print("\n1️⃣  Importing marketing_api module...")
    from marketing_api import (
        app, 
        segment_label, 
        segment_characteristics, 
        segment_rules_text,
        calculate_quantiles
    )
    print("✅ Marketing API imported successfully")
    
    print("\n2️⃣  Importing db_utils optimizations...")
    from db_utils import (
        get_transactions_df,
        get_date_range_fast,
        get_collection_stats
    )
    print("✅ Optimized db_utils imported successfully")
    
    print("\n3️⃣  Testing database connection...")
    stats = get_collection_stats('DSSFull')
    print(f"✅ Connected to MongoDB")
    print(f"   Documents: {stats['document_count']:,}")
    print(f"   Indexes: {len(stats['indexes'])}")
    
    print("\n4️⃣  Testing optimized date range query...")
    date_info = get_date_range_fast()
    print(f"✅ Date range retrieved (fast method)")
    print(f"   Min: {date_info['min_date']}")
    print(f"   Max: {date_info['max_date']}")
    
    print("\n5️⃣  Testing small data load (limit=100)...")
    df = get_transactions_df(limit=100)
    print(f"✅ Loaded {len(df)} transactions")
    print(f"   Memory: {df.memory_usage(deep=True).sum() / 1024:.2f} KB")
    
    print("\n6️⃣  Testing RFM calculation with limited data...")
    import pandas as pd
    df_test = get_transactions_df(limit=5000)
    reference_date = df_test['InvoiceDate'].max() + pd.Timedelta(days=1)
    rfm = df_test.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (reference_date - x.max()).days,
        'InvoiceNo': 'nunique',
        'Revenue': 'sum'
    }).reset_index()
    rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']
    print(f"✅ RFM calculated for {len(rfm)} customers")
    
    print("\n7️⃣  Testing quantile calculation...")
    quantiles = calculate_quantiles(rfm)
    print(f"✅ Quantiles calculated")
    print(f"   Recency Q50: {quantiles['recency']['q50']}")
    print(f"   Frequency Q50: {quantiles['frequency']['q50']}")
    print(f"   Monetary Q50: {quantiles['monetary']['q50']}")
    
    print("\n8️⃣  Testing segment labeling...")
    rfm['SegmentName'] = rfm.apply(lambda row: segment_label(row, quantiles), axis=1)
    seg_counts = rfm['SegmentName'].value_counts()
    print(f"✅ Segments labeled")
    for seg, count in seg_counts.items():
        print(f"   {seg}: {count} customers")
    
    print("\n9️⃣  Testing segment characteristics...")
    for seg_name in ['Champions', 'Loyal', 'At-Risk', 'Hibernating', 'Regulars']:
        if seg_name in rfm['SegmentName'].values:
            seg_data = rfm[rfm['SegmentName'] == seg_name]
            char = segment_characteristics(
                seg_name,
                seg_data['Recency'].mean(),
                seg_data['Frequency'].mean(),
                seg_data['Monetary'].mean()
            )
            print(f"✅ {seg_name}: {len(char)} chars")
            break
    
    print("\n🔟  Testing marketing recommendations...")
    actions = segment_rules_text('Champions')
    print(f"✅ Champions recommendations: {len(actions)} actions")
    for i, action in enumerate(actions, 1):
        print(f"   {i}. {action}")
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
    print("\n💡 The Marketing API is ready to use with optimized database queries!")
    print("\n📚 To start the API:")
    print("   uvicorn marketing_api:app --reload --port 8003")
    print("\n📖 View API docs:")
    print("   http://localhost:8003/docs")
    print("\n⚠️  Remember to use limit parameter for testing:")
    print("   df = get_transactions_df(limit=10000)  # Fast!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
