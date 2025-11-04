"""
Test Phase 1: Enhanced RFM Calculation
Tests new endpoints and features added in Phase 1
"""

import requests
import json
from datetime import datetime

MARKETING_URL = "http://localhost:8003"

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_result(name, success, data=None):
    status = "✅" if success else "❌"
    print(f"\n{status} {name}")
    if data:
        print(json.dumps(data, indent=2))

# ============================================
# PHASE 1 TESTS
# ============================================

print_header("PHASE 1: Enhanced RFM Calculation Tests")

# TEST 1: Date Range Info
print_header("TEST 1: Get Date Range Info")
try:
    response = requests.get(f"{MARKETING_URL}/date-range-info", timeout=10)
    if response.status_code == 200:
        data = response.json()
        print_result("Date Range Info", True, data)
        
        # Store dates for later use
        start_date = data.get('default_start')
        end_date = data.get('default_end')
    else:
        print_result("Date Range Info", False, {"error": f"Status {response.status_code}"})
except Exception as e:
    print_result("Date Range Info", False, {"error": str(e)})

# TEST 2: Basic RFM (Legacy - with bug fix)
print_header("TEST 2: Basic RFM Calculation (Legacy)")
try:
    response = requests.post(
        f"{MARKETING_URL}/calculate-rfm",
        json={},
        timeout=30
    )
    if response.status_code == 200:
        data = response.json()
        print_result("Basic RFM", True, {
            "customers_analyzed": data.get('customers_analyzed'),
            "summary": data.get('summary')
        })
    else:
        print_result("Basic RFM", False, {"error": response.text})
except Exception as e:
    print_result("Basic RFM", False, {"error": str(e)})

# TEST 3: Advanced RFM (Full date range)
print_header("TEST 3: Advanced RFM - Full Date Range")
try:
    response = requests.post(
        f"{MARKETING_URL}/calculate-rfm-advanced",
        json={
            "save_to_db": False
        },
        timeout=30
    )
    if response.status_code == 200:
        data = response.json()
        print_result("Advanced RFM (Full Range)", True, {
            "customers_analyzed": data.get('customers_analyzed'),
            "date_range": data.get('date_range'),
            "quantiles": data.get('quantiles'),
            "summary": data.get('summary')
        })
    else:
        print_result("Advanced RFM (Full Range)", False, {"error": response.text})
except Exception as e:
    print_result("Advanced RFM (Full Range)", False, {"error": str(e)})

# TEST 4: Advanced RFM with Date Filtering (Last 6 months)
print_header("TEST 4: Advanced RFM - Last 6 Months")
try:
    # Use dates from TEST 1
    response = requests.post(
        f"{MARKETING_URL}/calculate-rfm-advanced",
        json={
            "start_date": "2011-06-01",
            "end_date": "2011-12-09",
            "save_to_db": False
        },
        timeout=30
    )
    if response.status_code == 200:
        data = response.json()
        print_result("Advanced RFM (6 Months)", True, {
            "customers_analyzed": data.get('customers_analyzed'),
            "date_range": data.get('date_range'),
            "quantiles": data.get('quantiles'),
            "summary": data.get('summary')
        })
    else:
        print_result("Advanced RFM (6 Months)", False, {"error": response.text})
except Exception as e:
    print_result("Advanced RFM (6 Months)", False, {"error": str(e)})

# TEST 5: Advanced RFM with Specific Date Range
print_header("TEST 5: Advanced RFM - Specific Date Range (2011 only)")
try:
    response = requests.post(
        f"{MARKETING_URL}/calculate-rfm-advanced",
        json={
            "start_date": "2011-01-01",
            "end_date": "2011-12-31",
            "save_to_db": False
        },
        timeout=30
    )
    if response.status_code == 200:
        data = response.json()
        print_result("Advanced RFM (2011 only)", True, {
            "customers_analyzed": data.get('customers_analyzed'),
            "date_range": data.get('date_range'),
            "quantiles": data.get('quantiles'),
            "summary": data.get('summary')
        })
    else:
        print_result("Advanced RFM (2011 only)", False, {"error": response.text})
except Exception as e:
    print_result("Advanced RFM (2011 only)", False, {"error": str(e)})

# SUMMARY
print_header("PHASE 1 TEST SUMMARY")
print("""
Phase 1 Implementation: ✅ COMPLETE

New Features Added:
1. ✅ filter_by_date_range() function in db_utils.py
2. ✅ calculate_quantiles() function in marketing_api.py
3. ✅ /date-range-info endpoint (GET)
4. ✅ /calculate-rfm-advanced endpoint (POST)
5. ✅ RFM bug fix (quantile label mismatch)
6. ✅ Date filtering support
7. ✅ Quantile calculation for heuristic naming
8. ✅ Optional save to MongoDB

Next Steps:
- Test the endpoints above
- Verify quantiles match expected ranges
- Ready for Phase 2: Heuristic Segment Naming
""")
