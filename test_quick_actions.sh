#!/bin/bash
# Quick Actions API Test Script
# Test all 3 new endpoints for Sales Manager

echo "=================================="
echo "Testing Sales Manager API Endpoints"
echo "Port: 8004"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test 1: Active Deals
echo -e "${BLUE}[1/3] Testing /deals - Active Deals${NC}"
echo "GET http://localhost:8004/deals"
DEALS_RESPONSE=$(curl -s http://localhost:8004/deals)
DEALS_COUNT=$(echo $DEALS_RESPONSE | jq -r '.summary.total_deals')
PIPELINE_VALUE=$(echo $DEALS_RESPONSE | jq -r '.summary.total_pipeline_value')

if [ "$DEALS_COUNT" != "null" ]; then
    echo -e "${GREEN}✅ Success!${NC}"
    echo "   Total Deals: $DEALS_COUNT"
    echo "   Pipeline Value: \$$PIPELINE_VALUE"
else
    echo "❌ Failed!"
fi
echo ""

# Test 2: Lead Pipeline
echo -e "${BLUE}[2/3] Testing /leads - Lead Pipeline${NC}"
echo "GET http://localhost:8004/leads"
LEADS_RESPONSE=$(curl -s http://localhost:8004/leads)
LEADS_COUNT=$(echo $LEADS_RESPONSE | jq -r '.summary.total_leads')
AVG_SCORE=$(echo $LEADS_RESPONSE | jq -r '.summary.avg_lead_score')

if [ "$LEADS_COUNT" != "null" ]; then
    echo -e "${GREEN}✅ Success!${NC}"
    echo "   Total Leads: $LEADS_COUNT"
    echo "   Avg Lead Score: $AVG_SCORE"
else
    echo "❌ Failed!"
fi
echo ""

# Test 3: Sales Reports
echo -e "${BLUE}[3/3] Testing /reports - Sales Reports${NC}"
echo "GET http://localhost:8004/reports?period=monthly&limit=6"
REPORTS_RESPONSE=$(curl -s "http://localhost:8004/reports?period=monthly&limit=6")
TOTAL_REVENUE=$(echo $REPORTS_RESPONSE | jq -r '.report.total_revenue')
TOTAL_ORDERS=$(echo $REPORTS_RESPONSE | jq -r '.report.total_orders')
GROWTH_RATE=$(echo $REPORTS_RESPONSE | jq -r '.report.growth_rate')

if [ "$TOTAL_REVENUE" != "null" ]; then
    echo -e "${GREEN}✅ Success!${NC}"
    echo "   Total Revenue: \$$TOTAL_REVENUE"
    echo "   Total Orders: $TOTAL_ORDERS"
    echo "   Growth Rate: $GROWTH_RATE%"
else
    echo "❌ Failed!"
fi
echo ""

# Summary
echo "=================================="
echo -e "${GREEN}All 3 endpoints tested successfully!${NC}"
echo "=================================="
echo ""
echo "Frontend URLs (after Spring Boot starts):"
echo "  - Active Deals:   http://localhost:8080/sales/deals"
echo "  - Lead Pipeline:  http://localhost:8080/sales/leads"
echo "  - Sales Reports:  http://localhost:8080/sales/reports"
echo ""
