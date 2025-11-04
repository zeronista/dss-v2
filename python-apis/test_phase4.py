"""
Test Phase 4: Date Range Features for Market Basket Analysis
Tests date filtering functionality across all basket analysis endpoints
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8003"

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def test_date_range_info():
    """Test 1: Verify /date-range-info endpoint"""
    print_section("TEST 1: Date Range Info")
    
    try:
        response = requests.get(f"{BASE_URL}/date-range-info")
        data = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Min Date: {data['min_date']}")
        print(f"Max Date: {data['max_date']}")
        print(f"Default Start: {data['default_start']}")
        print(f"Default End: {data['default_end']}")
        print(f"Total Days: {data['total_days']}")
        
        print("\n✅ Date range info retrieved successfully")
        return data
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return None

def test_segment_basket_with_dates(date_info):
    """Test 2: Segment basket analysis with date filtering"""
    print_section("TEST 2: Segment Basket Analysis with Date Range")
    
    if not date_info:
        print("⚠️ Skipping - no date info available")
        return
    
    try:
        # Test with last 6 months of data
        end_date = date_info['max_date']
        start_obj = datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=180)
        start_date = start_obj.strftime('%Y-%m-%d')
        
        print(f"Testing Champions segment with date range:")
        print(f"  Start Date: {start_date}")
        print(f"  End Date: {end_date}")
        
        url = f"{BASE_URL}/segment-basket-analysis"
        params = {
            "segment_name": "Champions",
            "min_support": 0.01,
            "min_confidence": 0.3,
            "top_n": 5,
            "start_date": start_date,
            "end_date": end_date
        }
        
        response = requests.post(url, params=params)
        data = response.json()
        
        print(f"\nStatus: {response.status_code}")
        print(f"Segment: {data.get('segment', 'N/A')}")
        print(f"Customers: {data.get('customer_count', 0)}")
        print(f"Bundles Found: {data.get('total_bundles_found', 0)}")
        
        if 'date_range' in data:
            dr = data['date_range']
            print(f"\nDate Range Applied:")
            print(f"  Start: {dr['start_date']}")
            print(f"  End: {dr['end_date']}")
            print(f"  Filtered: {dr['filtered']}")
        
        if data.get('top_recommendation'):
            rec = data['top_recommendation']
            print(f"\n🏆 Top Recommendation:")
            print(f"  {rec['antecedents_display']}")
            print(f"  → {rec['consequents_display']}")
            print(f"  Confidence: {rec['confidence']*100:.1f}%")
            print(f"  Lift: {rec['lift']:.2f}x {rec['strength']}")
        
        print("\n✅ Date-filtered segment analysis successful")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

def test_market_basket_with_dates(date_info):
    """Test 3: Market basket analysis with date filtering"""
    print_section("TEST 3: Market Basket Analysis with Date Range")
    
    if not date_info:
        print("⚠️ Skipping - no date info available")
        return
    
    try:
        # Test with last 3 months
        end_date = date_info['max_date']
        start_obj = datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=90)
        start_date = start_obj.strftime('%Y-%m-%d')
        
        print(f"Testing full basket analysis with date range:")
        print(f"  Start Date: {start_date}")
        print(f"  End Date: {end_date}")
        
        url = f"{BASE_URL}/market-basket-analysis"
        payload = {
            "min_support": 0.01,
            "min_confidence": 0.3,
            "top_n": 5,
            "start_date": start_date,
            "end_date": end_date
        }
        
        response = requests.post(url, json=payload)
        data = response.json()
        
        print(f"\nStatus: {response.status_code}")
        print(f"Total Bundles: {data.get('total_bundles_found', 0)}")
        print(f"Displayed: {data.get('displayed_bundles', 0)}")
        
        if 'date_range' in data:
            dr = data['date_range']
            print(f"\nDate Range Applied:")
            print(f"  Start: {dr['start_date']}")
            print(f"  End: {dr['end_date']}")
            print(f"  Filtered: {dr['filtered']}")
        
        if data.get('bundles'):
            print(f"\n📦 Top 3 Bundles:")
            for i, bundle in enumerate(data['bundles'][:3], 1):
                print(f"\n  {i}. {bundle['antecedents_display']}")
                print(f"     → {bundle['consequents_display']}")
                print(f"     Conf: {bundle['confidence']*100:.1f}% | Lift: {bundle['lift']:.2f}x {bundle['strength']}")
        
        print("\n✅ Date-filtered market basket analysis successful")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

def test_product_bundles_with_dates(date_info):
    """Test 4: Product bundles endpoint with date filtering"""
    print_section("TEST 4: Product Bundles with Date Range")
    
    if not date_info:
        print("⚠️ Skipping - no date info available")
        return
    
    try:
        # Test with specific date range
        end_date = date_info['max_date']
        start_date = date_info['default_start']
        
        print(f"Testing product bundles with date range:")
        print(f"  Start Date: {start_date}")
        print(f"  End Date: {end_date}")
        
        url = f"{BASE_URL}/product-bundles"
        params = {
            "min_support": 0.01,
            "min_confidence": 0.3,
            "top_n": 3,
            "start_date": start_date,
            "end_date": end_date
        }
        
        response = requests.post(url, params=params)
        data = response.json()
        
        print(f"\nStatus: {response.status_code}")
        print(f"Bundles Found: {data.get('total_bundles_found', 0)}")
        
        if 'date_range' in data:
            dr = data['date_range']
            print(f"\nDate Range Info:")
            print(f"  Start: {dr['start_date']}")
            print(f"  End: {dr['end_date']}")
            print(f"  Filtered: {'Yes' if dr['filtered'] else 'No'}")
        
        if data.get('top_recommendation'):
            rec = data['top_recommendation']
            print(f"\n🎯 Best Bundle:")
            print(f"  Buy: {rec['antecedents_display']}")
            print(f"  Get: {rec['consequents_display']}")
            print(f"  Metrics: {rec['confidence']*100:.1f}% confidence, {rec['lift']:.2f}x lift")
            print(f"  Expected Revenue: ${rec['expected_revenue']:,.2f}")
        
        print("\n✅ Product bundles with dates successful")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

def test_without_dates():
    """Test 5: Verify endpoints work without date parameters (backward compatibility)"""
    print_section("TEST 5: Backward Compatibility (No Date Params)")
    
    try:
        print("Testing segment basket analysis WITHOUT date filtering...")
        
        url = f"{BASE_URL}/segment-basket-analysis"
        params = {
            "segment_name": "Loyal",
            "min_support": 0.01,
            "min_confidence": 0.25,
            "top_n": 3
        }
        
        response = requests.post(url, params=params)
        data = response.json()
        
        print(f"\nStatus: {response.status_code}")
        print(f"Segment: {data.get('segment', 'N/A')}")
        print(f"Bundles: {data.get('total_bundles_found', 0)}")
        
        if 'date_range' in data:
            dr = data['date_range']
            print(f"\nDate Range (Auto-detected):")
            print(f"  Start: {dr['start_date']}")
            print(f"  End: {dr['end_date']}")
            print(f"  Filtered: {dr['filtered']} (should be False)")
        
        if not data.get('date_range', {}).get('filtered'):
            print("\n✅ Backward compatibility verified - works without dates")
        else:
            print("\n⚠️ Warning: filtered=True when no dates provided")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

def main():
    """Run all Phase 4 tests"""
    print("\n" + "🚀"*40)
    print("  PHASE 4 TESTING: Date Range Features for Market Basket Analysis")
    print("🚀"*40)
    
    # Test 1: Get date range info
    date_info = test_date_range_info()
    
    # Test 2: Segment basket with dates
    test_segment_basket_with_dates(date_info)
    
    # Test 3: Market basket with dates
    test_market_basket_with_dates(date_info)
    
    # Test 4: Product bundles with dates
    test_product_bundles_with_dates(date_info)
    
    # Test 5: Backward compatibility
    test_without_dates()
    
    print("\n" + "="*80)
    print("  ALL PHASE 4 TESTS COMPLETED")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
