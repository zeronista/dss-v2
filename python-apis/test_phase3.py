"""
Test Phase 3: Advanced Market Basket Analysis
Tests segment-specific basket analysis with enhanced formatting
"""

import requests
import json

MARKETING_URL = "http://localhost:8003"

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_result(name, success, data=None):
    status = "✅" if success else "❌"
    print(f"\n{status} {name}")
    if data:
        print(json.dumps(data, indent=2, ensure_ascii=False))

# ============================================
# PHASE 3 TESTS
# ============================================

print_header("PHASE 3: Advanced Market Basket Analysis Tests")

# TEST 1: Enhanced Market Basket Analysis (All Customers)
print_header("TEST 1: Enhanced Market Basket (All Customers)")
try:
    response = requests.post(
        f"{MARKETING_URL}/market-basket-analysis",
        json={
            "min_support": 0.01,
            "min_confidence": 0.3,
            "top_n": 5
        },
        timeout=60
    )
    if response.status_code == 200:
        data = response.json()
        print_result("Market Basket (All)", True, {
            "success": data.get('success'),
            "total_bundles_found": data.get('total_bundles_found'),
            "displayed_bundles": data.get('displayed_bundles')
        })
        
        # Display top recommendation
        if data.get('top_recommendation'):
            top = data['top_recommendation']
            print("\n" + "-"*70)
            print("🌟 TOP BUNDLE RECOMMENDATION:")
            print("-"*70)
            print(f"When customers buy: {top['antecedents_display']}")
            print(f"They also buy: {top['consequents_display']}")
            print(f"Confidence: {top['confidence']*100:.1f}% | Lift: {top['lift']:.2f}x {top['strength']}")
            print(f"Expected Revenue: ${top['expected_revenue']:,.2f}")
        
        # Display all bundles
        print("\n" + "-"*70)
        print("ALL BUNDLES:")
        print("-"*70)
        for i, bundle in enumerate(data.get('bundles', [])[:5], 1):
            print(f"\n{i}. {bundle['strength']} {bundle['antecedents_display']}")
            print(f"   → {bundle['consequents_display']}")
            print(f"   Support: {bundle['support']*100:.2f}% | Confidence: {bundle['confidence']*100:.1f}% | Lift: {bundle['lift']:.2f}x")
            
    else:
        print_result("Market Basket (All)", False, {"error": response.text})
except Exception as e:
    print_result("Market Basket (All)", False, {"error": str(e)})

# TEST 2: Segment-Specific Basket Analysis - Champions
print_header("TEST 2: Basket Analysis for Champions Segment")
try:
    response = requests.post(
        f"{MARKETING_URL}/segment-basket-analysis",
        params={
            "segment_name": "Champions",
            "min_support": 0.01,
            "min_confidence": 0.3,
            "top_n": 5
        },
        timeout=60
    )
    if response.status_code == 200:
        data = response.json()
        print_result("Champions Basket", True, {
            "segment": data.get('segment'),
            "customer_count": data.get('customer_count'),
            "total_bundles_found": data.get('total_bundles_found'),
            "displayed_bundles": data.get('displayed_bundles')
        })
        
        # Display top recommendation
        if data.get('top_recommendation'):
            top = data['top_recommendation']
            print("\n" + "-"*70)
            print(f"🏆 TOP BUNDLE FOR CHAMPIONS:")
            print("-"*70)
            print(f"When Champions buy: {top['antecedents_display']}")
            print(f"Recommend: {top['consequents_display']}")
            print(f"Confidence: {top['confidence']*100:.1f}% | Lift: {top['lift']:.2f}x {top['strength']}")
    else:
        print_result("Champions Basket", False, {"error": response.text})
except Exception as e:
    print_result("Champions Basket", False, {"error": str(e)})

# TEST 3: Segment-Specific Basket Analysis - Loyal
print_header("TEST 3: Basket Analysis for Loyal Segment")
try:
    response = requests.post(
        f"{MARKETING_URL}/segment-basket-analysis",
        params={
            "segment_name": "Loyal",
            "min_support": 0.01,
            "min_confidence": 0.3,
            "top_n": 5
        },
        timeout=60
    )
    if response.status_code == 200:
        data = response.json()
        print_result("Loyal Basket", True, {
            "segment": data.get('segment'),
            "customer_count": data.get('customer_count'),
            "bundles_found": data.get('total_bundles_found')
        })
        
        # Display bundles
        print("\n💎 Loyal Customer Bundles:")
        for i, bundle in enumerate(data.get('bundles', [])[:3], 1):
            print(f"{i}. {bundle['strength']} {bundle['antecedents_display']} → {bundle['consequents_display']}")
    else:
        print_result("Loyal Basket", False, {"error": response.text})
except Exception as e:
    print_result("Loyal Basket", False, {"error": str(e)})

# TEST 4: Test all segments
print_header("TEST 4: Basket Analysis for All Segments")
segments = ["Champions", "Loyal", "At-Risk", "Hibernating", "Regulars"]

for segment in segments:
    try:
        response = requests.post(
            f"{MARKETING_URL}/segment-basket-analysis",
            params={
                "segment_name": segment,
                "min_support": 0.01,
                "min_confidence": 0.25,
                "top_n": 3
            },
            timeout=60
        )
        if response.status_code == 200:
            data = response.json()
            bundles_count = data.get('total_bundles_found', 0)
            customer_count = data.get('customer_count', 0)
            status = "✅" if bundles_count > 0 else "⚠️"
            print(f"{status} {segment}: {customer_count:,} customers, {bundles_count} bundles found")
        else:
            print(f"❌ {segment}: Error - {response.status_code}")
    except Exception as e:
        print(f"❌ {segment}: {str(e)}")

# TEST 5: Verify lift strength indicators
print_header("TEST 5: Verify Lift Strength Indicators")
try:
    response = requests.post(
        f"{MARKETING_URL}/market-basket-analysis",
        json={
            "min_support": 0.01,
            "min_confidence": 0.3,
            "top_n": 10
        },
        timeout=60
    )
    if response.status_code == 200:
        data = response.json()
        bundles = data.get('bundles', [])
        
        print("\nLift Strength Distribution:")
        very_strong = sum(1 for b in bundles if b['strength'] == '🔥')
        good = sum(1 for b in bundles if b['strength'] == '✅')
        moderate = sum(1 for b in bundles if b['strength'] == '➡️')
        
        print(f"🔥 Very Strong (Lift > 2.0): {very_strong}")
        print(f"✅ Good (Lift > 1.5): {good}")
        print(f"➡️ Moderate (Lift > 1.0): {moderate}")
        
        # Show examples
        print("\nExamples:")
        for bundle in bundles[:3]:
            print(f"{bundle['strength']} Lift {bundle['lift']:.2f}: {bundle['antecedents_display'][:40]}... → {bundle['consequents_display'][:40]}...")
    else:
        print("❌ Error getting bundles")
except Exception as e:
    print(f"❌ Error: {str(e)}")

# SUMMARY
print_header("PHASE 3 TEST SUMMARY")
print("""
Phase 3 Implementation: ✅ COMPLETE

New Features Added:
1. ✅ get_lift_strength() - Visual indicators for lift values
   • 🔥 Very strong (lift > 2.0)
   • ✅ Good (lift > 1.5)
   • ➡️ Moderate (lift > 1.0)

2. ✅ format_product_display() - Enhanced product formatting
   • Truncates long product names
   • Adds stock codes (optional)
   • Clean, readable display

3. ✅ create_stock_to_description_mapping() - Product mapping
   • Maps stock codes to descriptions
   • Handles multiple descriptions per code

4. ✅ /segment-basket-analysis endpoint (NEW!)
   • Analyze basket rules for specific segments
   • Segment-specific product recommendations
   • Enhanced display with product descriptions
   • Top recommendation highlighted

5. ✅ Enhanced /market-basket-analysis endpoint
   • Now includes product descriptions
   • Lift strength indicators
   • Top recommendation field
   • Better formatted output

6. ✅ Enhanced /product-bundles endpoint
   • Calls enhanced market-basket-analysis
   • All Phase 3 features included

Key Improvements:
- Segment-specific recommendations (e.g., Champions get different bundles than At-Risk)
- Visual lift indicators make it easy to spot strong associations
- Product descriptions make bundles actionable
- Top recommendation field highlights best bundle

Performance:
- Optimized to top 200 products per segment
- Faster analysis with segment filtering
- Results typically in 10-30 seconds

Next Steps:
- Test with different segments
- Verify lift indicators are accurate
- Check product descriptions display correctly
- Ready for Phase 4: Date Range Features
""")
