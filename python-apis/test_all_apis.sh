#!/bin/bash
# Script để test tất cả các API endpoints

echo "========================================"
echo "🧪 TESTING ALL DSS APIs"
echo "========================================"
echo ""

# Test Admin API
echo "📊 1. ADMIN API (Port 8001)"
echo "----------------------------------------"
echo "Health:"
timeout 5 curl -s http://localhost:8001/health || echo "Timeout/Error"
echo -e "\n"

echo "KPIs:"
timeout 10 curl -s -X POST http://localhost:8001/kpis -H "Content-Type: application/json" -d '{}' || echo "Timeout/Error"
echo -e "\n"

echo "Top Countries:"
timeout 10 curl -s -X POST http://localhost:8001/top-countries -H "Content-Type: application/json" -d '{"top_n": 3}' || echo "Timeout/Error"
echo -e "\n\n"

# Test Inventory API
echo "📦 2. INVENTORY API (Port 8002)"
echo "----------------------------------------"
echo "Health:"
timeout 5 curl -s http://localhost:8002/health || echo "Timeout/Error"
echo -e "\n"

echo "Risk Distribution:"
timeout 10 curl -s http://localhost:8002/risk-distribution || echo "Timeout/Error"
echo -e "\n\n"

# Test Marketing API
echo "💖 3. MARKETING API (Port 8003)"
echo "----------------------------------------"
echo "Health:"
timeout 5 curl -s http://localhost:8003/health || echo "Timeout/Error"
echo -e "\n"

echo "RFM Stats:"
timeout 10 curl -s http://localhost:8003/calculate-rfm || echo "Timeout/Error"
echo -e "\n"

echo "Run Segmentation (K=3):"
timeout 15 curl -s -X POST http://localhost:8003/run-segmentation \
  -H "Content-Type: application/json" \
  -d '{"n_segments": 3}' || echo "Timeout/Error"
echo -e "\n\n"

# Test Sales API
echo "🛍️  4. SALES API (Port 8004)"
echo "----------------------------------------"
echo "Health:"
timeout 5 curl -s http://localhost:8004/health || echo "Timeout/Error"
echo -e "\n"

echo "Generate Recommendations (Product: 85123A):"
timeout 30 curl -s -X POST http://localhost:8004/generate-recommendations \
  -H "Content-Type: application/json" \
  -d '{"stock_code": "85123A", "top_n": 3, "min_support": 0.01}' || echo "Timeout/Error"
echo -e "\n\n"

echo "========================================"
echo "✅ Testing Complete!"
echo "========================================"
