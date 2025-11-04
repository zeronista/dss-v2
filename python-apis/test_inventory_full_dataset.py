"""
Test script to verify Inventory API is using FULL dataset (online_retail.csv)
including cancelled/returned orders
"""

import requests
import json

BASE_URL = "http://localhost:8002"

def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def test_health_check():
    print_section("1. HEALTH CHECK - Verify Data Source")
    response = requests.get(f"{BASE_URL}/health")
    data = response.json()
    print(json.dumps(data, indent=2))
    
    if "data_source" in data:
        print(f"\n✅ Data source field found: {data['data_source']}")
        if "Full dataset" in data['data_source'] or "online_retail.csv" in data['data_source']:
            print("✅ Confirmed: Using FULL dataset!")
        else:
            print("❌ Warning: Not using full dataset")
    else:
        print("⚠️  No data source information in health check")

def test_root_endpoint():
    print_section("2. ROOT ENDPOINT - Check Service Info")
    response = requests.get(f"{BASE_URL}/")
    data = response.json()
    print(json.dumps(data, indent=2))
    
    if "data_source" in data:
        print(f"\n✅ Data source: {data['data_source']}")
    if "note" in data:
        print(f"✅ Note: {data['note']}")

def test_return_statistics():
    print_section("3. RETURN STATISTICS - Verify Return Data Exists")
    response = requests.get(f"{BASE_URL}/return-statistics")
    
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
        
        stats = data.get('overall_statistics', {})
        total_returns = stats.get('total_returns', 0)
        return_rate = stats.get('return_rate_percent', 0)
        
        print(f"\n📊 ANALYSIS:")
        print(f"   Total Returns: {total_returns}")
        print(f"   Return Rate: {return_rate}%")
        
        if total_returns > 0:
            print(f"   ✅ SUCCESS: Found {total_returns} return/cancelled orders!")
            print(f"   ✅ This confirms we're using FULL dataset with returns")
        else:
            print("   ❌ ERROR: No returns found - may not be using full dataset!")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def test_risk_score_calculation():
    print_section("4. RISK SCORE CALCULATION - Test with Real Customer")
    
    # Test with a sample customer and product
    payload = {
        "customer_id": "12346",
        "stock_code": "22632",
        "quantity": 6,
        "unit_price": 1.65,
        "country": "United Kingdom"
    }
    
    print(f"Testing with payload:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(f"{BASE_URL}/calculate-risk-score", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nResponse:")
        print(json.dumps(data, indent=2))
        
        print(f"\n📊 RISK ANALYSIS:")
        print(f"   Risk Score: {data['risk_score']}")
        print(f"   Risk Level: {data['risk_level']}")
        print(f"   Message: {data['message']}")
        
        # Check if message contains return rate info
        if "Return Rate" in data['message']:
            print(f"   ✅ Message includes customer/product return rates!")
            print(f"   ✅ Confirms calculation uses actual return history from full dataset")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def test_risk_distribution():
    print_section("5. RISK DISTRIBUTION - Verify Data Source")
    
    response = requests.get(f"{BASE_URL}/risk-distribution?sample_size=500")
    
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
        
        if "data_source" in data:
            print(f"\n✅ Data source confirmed: {data['data_source']}")
        
        if "overall_return_rate" in data:
            print(f"✅ Overall return rate: {data['overall_return_rate']}%")
            print(f"✅ Total returns in DB: {data.get('total_returns_in_db', 0)}")
            print(f"✅ Confirms using full dataset with return data!")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def test_policy_simulation():
    print_section("6. POLICY SIMULATION - Test with Threshold")
    
    payload = {
        "threshold_tau": 50.0,
        "return_processing_cost": 10.0,
        "conversion_impact": 0.2,
        "sample_size": 200
    }
    
    print(f"Testing policy simulation with threshold tau=50:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(f"{BASE_URL}/simulate-policy", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nResponse:")
        print(json.dumps(data, indent=2))
        
        print(f"\n📊 SIMULATION RESULTS:")
        print(f"   Total Expected Profit: ${data['total_expected_profit']:,.2f}")
        print(f"   Orders Blocked: {data['orders_blocked']}")
        print(f"   Orders Allowed: {data['orders_allowed']}")
        print(f"   Avg Risk (Blocked): {data['avg_risk_blocked']:.2f}")
        print(f"   Avg Risk (Allowed): {data['avg_risk_allowed']:.2f}")
        print(f"   Recommendation: {data['recommendation']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def main():
    print("\n" + "#"*80)
    print("#  INVENTORY API - FULL DATASET VERIFICATION TEST")
    print("#  Testing if API correctly uses online_retail.csv (with returns)")
    print("#"*80)
    
    try:
        # Run all tests
        test_health_check()
        test_root_endpoint()
        test_return_statistics()
        test_risk_score_calculation()
        test_risk_distribution()
        test_policy_simulation()
        
        print("\n" + "#"*80)
        print("#  TEST COMPLETE")
        print("#"*80)
        print("\n✅ If you see return statistics with actual return data,")
        print("   the API is correctly using the FULL dataset!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to Inventory API")
        print("   Make sure the API is running on http://localhost:8002")
        print("   Run: python inventory_api.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    main()
