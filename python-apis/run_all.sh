#!/bin/bash
# Script để chạy tất cả Python APIs cùng lúc

echo "🚀 Starting all Python APIs..."
echo ""

# Start each API in background
echo "📊 Starting Admin API on port 8001..."
python3 admin_api.py &
ADMIN_PID=$!

sleep 2

echo "📦 Starting Inventory API on port 8002..."
python3 inventory_api.py &
INVENTORY_PID=$!

sleep 2

echo "💖 Starting Marketing API on port 8003..."
python3 marketing_api.py &
MARKETING_PID=$!

sleep 2

echo "🛍️  Starting Sales API on port 8004..."
python3 sales_api.py &
SALES_PID=$!

echo ""
echo "✅ All APIs started!"
echo ""
echo "📝 Swagger Documentation:"
echo "  - Admin:     http://localhost:8001/docs"
echo "  - Inventory: http://localhost:8002/docs"
echo "  - Marketing: http://localhost:8003/docs"
echo "  - Sales:     http://localhost:8004/docs"
echo ""
echo "Press Ctrl+C to stop all APIs"
echo ""

# Wait for all background processes
wait
