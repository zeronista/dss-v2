#!/bin/bash
# Quick test script để verify integration

echo "🧪 DSS Integration Test Suite"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test MongoDB connection
echo "📦 Testing MongoDB Connection..."
cd python-apis
python3 -c "from db_utils import test_connection; test_connection()" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ MongoDB connection OK${NC}"
else
    echo -e "${RED}✗ MongoDB connection FAILED${NC}"
fi
echo ""

# Test Admin API
echo "📊 Testing Admin API (Port 8001)..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health 2>/dev/null)
if [ "$response" = "200" ]; then
    echo -e "${GREEN}✓ Admin API is running${NC}"
else
    echo -e "${RED}✗ Admin API not responding (Start with: python3 admin_api.py)${NC}"
fi

# Test Inventory API
echo "📦 Testing Inventory API (Port 8002)..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8002/health 2>/dev/null)
if [ "$response" = "200" ]; then
    echo -e "${GREEN}✓ Inventory API is running${NC}"
else
    echo -e "${RED}✗ Inventory API not responding (Start with: python3 inventory_api.py)${NC}"
fi

# Test Marketing API
echo "💖 Testing Marketing API (Port 8003)..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8003/health 2>/dev/null)
if [ "$response" = "200" ]; then
    echo -e "${GREEN}✓ Marketing API is running${NC}"
else
    echo -e "${RED}✗ Marketing API not responding (Start with: python3 marketing_api.py)${NC}"
fi

# Test Sales API
echo "🛍️  Testing Sales API (Port 8004)..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8004/health 2>/dev/null)
if [ "$response" = "200" ]; then
    echo -e "${GREEN}✓ Sales API is running${NC}"
else
    echo -e "${RED}✗ Sales API not responding (Start with: python3 sales_api.py)${NC}"
fi

echo ""
echo "======================================"
echo "📝 Summary:"
echo ""
echo "✅ APIs Running:"
echo "   Admin:     http://localhost:8001/docs"
echo "   Inventory: http://localhost:8002/docs"
echo "   Marketing: http://localhost:8003/docs"
echo "   Sales:     http://localhost:8004/docs"
echo ""
echo "🎨 Dashboards:"
echo "   Admin:     file://$(pwd)/../src/main/resources/templates/dashboard/admin.html"
echo "   Inventory: file://$(pwd)/../src/main/resources/templates/dashboard/inventory.html"
echo "   Marketing: file://$(pwd)/../src/main/resources/templates/dashboard/marketing.html"
echo "   Sales:     file://$(pwd)/../src/main/resources/templates/dashboard/sales.html"
echo ""
echo -e "${YELLOW}💡 Tip: Open dashboards in browser to test UI integration${NC}"
echo ""
