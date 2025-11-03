"""
Test script for all Python APIs
Run this after starting all APIs to verify they're working correctly
"""

import requests
import json
from datetime import datetime

# API endpoints
ADMIN_URL = "http://localhost:8001"
INVENTORY_URL = "http://localhost:8002"
MARKETING_URL = "http://localhost:8003"
SALES_URL = "http://localhost:8004"

def print_result(name, success, message=""):
    """Print test result"""
    status = "✅" if success else "❌"
    print(f"{status} {name}: {message}")

def test_health_checks():
    """Test health endpoints for all APIs"""
    print("\n🔍 Testing Health Checks...")
    print("-" * 50)
    
    apis = [
        ("Admin API", ADMIN_URL),
        ("Inventory API", INVENTORY_URL),
        ("Marketing API", MARKETING_URL),
        ("Sales API", SALES_URL)
    ]
    
    for name, url in apis:
        try:
            response = requests.get(f"{url}/health", timeout=5)
            success = response.status_code == 200
            message = f"Port {response.json().get('port', 'unknown')}"
            print_result(name, success, message)
        except Exception as e:
            print_result(name, False, f"Error: {str(e)}")

def test_admin_api():
    """Test Admin API endpoints"""
    print("\n📊 Testing Admin API...")
    print("-" * 50)
    
    # Test KPIs
    try:
        response = requests.post(
            f"{ADMIN_URL}/kpis",
            json={
                "top_n": 10,
                "exclude_cancelled": True
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print_result("KPIs", True, f"Revenue: ${data.get('total_revenue', 0):,.2f}")
        else:
            print_result("KPIs", False, f"Status: {response.status_code}")
    except Exception as e:
        print_result("KPIs", False, f"Error: {str(e)}")

def test_inventory_api():
    """Test Inventory API endpoints"""
    print("\n📦 Testing Inventory API...")
    print("-" * 50)
    
    # Test risk score calculation
    try:
        response = requests.post(
            f"{INVENTORY_URL}/calculate-risk-score",
            json={
                "customer_id": "12345",
                "stock_code": "85123A",
                "quantity": 10,
                "unit_price": 2.55,
                "country": "United Kingdom"
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print_result("Risk Score", True, f"Score: {data.get('risk_score', 0)}/100 ({data.get('risk_level', 'N/A')})")
        else:
            print_result("Risk Score", False, f"Status: {response.status_code}")
    except Exception as e:
        print_result("Risk Score", False, f"Error: {str(e)}")
    
    # Test policy simulation
    try:
        response = requests.post(
            f"{INVENTORY_URL}/simulate-policy",
            json={
                "threshold_tau": 50,
                "return_processing_cost": 10.0,
                "conversion_impact": 0.2,
                "sample_size": 100
            },
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            print_result("Policy Simulation", True, f"Expected Profit: ${data.get('total_expected_profit', 0):,.2f}")
        else:
            print_result("Policy Simulation", False, f"Status: {response.status_code}")
    except Exception as e:
        print_result("Policy Simulation", False, f"Error: {str(e)}")

def test_marketing_api():
    """Test Marketing API endpoints"""
    print("\n💖 Testing Marketing API...")
    print("-" * 50)
    
    # Test RFM calculation
    try:
        response = requests.post(
            f"{MARKETING_URL}/calculate-rfm",
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            print_result("RFM Calculation", True, f"Customers: {data.get('customers_analyzed', 0)}")
        else:
            print_result("RFM Calculation", False, f"Status: {response.status_code}")
    except Exception as e:
        print_result("RFM Calculation", False, f"Error: {str(e)}")
    
    # Test segmentation
    try:
        response = requests.post(
            f"{MARKETING_URL}/run-segmentation",
            json={
                "n_segments": 3,
                "use_existing_rfm": False
            },
            timeout=20
        )
        if response.status_code == 200:
            data = response.json()
            print_result("Segmentation", True, f"Segments: {data.get('n_segments', 0)}")
        else:
            print_result("Segmentation", False, f"Status: {response.status_code}")
    except Exception as e:
        print_result("Segmentation", False, f"Error: {str(e)}")

def test_sales_api():
    """Test Sales API endpoints"""
    print("\n🛍️  Testing Sales API...")
    print("-" * 50)
    
    # Test top bundles
    try:
        response = requests.get(
            f"{SALES_URL}/top-bundles",
            params={
                "min_support": 0.01,
                "min_confidence": 0.3,
                "top_n": 5
            },
            timeout=20
        )
        if response.status_code == 200:
            data = response.json()
            print_result("Top Bundles", True, f"Found: {data.get('total_bundles', 0)} bundles")
        else:
            print_result("Top Bundles", False, f"Status: {response.status_code}")
    except Exception as e:
        print_result("Top Bundles", False, f"Error: {str(e)}")

def main():
    """Run all tests"""
    print("=" * 50)
    print("🧪 Testing Python APIs for DSS Project")
    print("=" * 50)
    
    # Test all endpoints
    test_health_checks()
    test_admin_api()
    test_inventory_api()
    test_marketing_api()
    test_sales_api()
    
    print("\n" + "=" * 50)
    print("✅ Testing completed!")
    print("=" * 50)
    print("\n📝 Check Swagger docs for detailed API testing:")
    print("  - Admin:     http://localhost:8001/docs")
    print("  - Inventory: http://localhost:8002/docs")
    print("  - Marketing: http://localhost:8003/docs")
    print("  - Sales:     http://localhost:8004/docs")

if __name__ == "__main__":
    main()
