#!/bin/bash
# Stop DSS-v2 Application - ALL Services

echo "=================================="
echo "🛑 Stopping DSS-v2 - ALL SERVICES"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to stop process on port
stop_port() {
    local PORT=$1
    local NAME=$2
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "Stopping $NAME (port $PORT)..."
        kill -9 $(lsof -ti:$PORT) 2>/dev/null
        echo -e "${GREEN}✅ $NAME stopped${NC}"
    else
        echo -e "${YELLOW}⚠️  $NAME not running${NC}"
    fi
}

# Stop all API services
stop_port 8001 "Admin API"
stop_port 8002 "Inventory API"
stop_port 8003 "Marketing API"
stop_port 8004 "Sales Manager API"
stop_port 8080 "Spring Boot"

# Also stop any mvnw processes
echo ""
echo "Cleaning up background processes..."
pkill -f "mvnw spring-boot:run" 2>/dev/null
pkill -f "admin_api.py" 2>/dev/null
pkill -f "inventory_api.py" 2>/dev/null
pkill -f "marketing_api.py" 2>/dev/null
pkill -f "sales_manager_api.py" 2>/dev/null
pkill -f "sales_api.py" 2>/dev/null

echo ""
echo -e "${GREEN}✅ All DSS-v2 services stopped.${NC}"
echo ""
