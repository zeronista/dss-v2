#!/bin/bash
# Start DSS-v2 Application - ALL APIs + Spring Boot
# Chạy đầy đủ 4 Python APIs (ports 8001-8004) + Spring Boot (8080)

echo "=================================="
echo "🚀 Starting DSS-v2 - FULL SYSTEM"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running with sudo
if [ "$EUID" -eq 0 ]; then 
    echo -e "${YELLOW}⚠️  Warning: Running with sudo is not recommended${NC}"
    echo -e "${YELLOW}   Please run: bash start.sh (without sudo)${NC}"
    echo ""
fi

# Activate conda
if command -v conda &> /dev/null; then
    echo "Activating conda environment..."
    eval "$(conda shell.bash hook)"
    conda activate base
    PYTHON_CMD="python"
else
    echo "Conda not found, using system python3..."
    PYTHON_CMD="python3"
fi

cd /home/ubuntu/DataScience/MyProject/dss-v2/python-apis

# Function to stop existing process on port
stop_port() {
    local PORT=$1
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${YELLOW}  Stopping existing process on port $PORT...${NC}"
        kill -9 $(lsof -ti:$PORT) 2>/dev/null
        sleep 1
    fi
}

# Stop all existing API processes
echo "🔍 Checking for existing processes..."
stop_port 8001
stop_port 8002
stop_port 8003
stop_port 8004
stop_port 8080
echo ""

# ============ Start Python APIs ============

echo -e "${BLUE}[1/5] Starting Admin API (Port 8001)...${NC}"
nohup $PYTHON_CMD admin_api.py > admin_api.log 2>&1 &
ADMIN_PID=$!
sleep 3
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Admin API started (PID: $ADMIN_PID)${NC}"
else
    echo -e "${RED}❌ Admin API failed to start${NC}"
fi
echo ""

echo -e "${BLUE}[2/5] Starting Inventory API (Port 8002)...${NC}"
nohup $PYTHON_CMD inventory_api.py > inventory_api.log 2>&1 &
INVENTORY_PID=$!
sleep 3
if curl -s http://localhost:8002/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Inventory API started (PID: $INVENTORY_PID)${NC}"
else
    echo -e "${RED}❌ Inventory API failed to start${NC}"
fi
echo ""

echo -e "${BLUE}[3/5] Starting Marketing API (Port 8003)...${NC}"
nohup $PYTHON_CMD marketing_api.py > marketing_api.log 2>&1 &
MARKETING_PID=$!
sleep 3
if curl -s http://localhost:8003/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Marketing API started (PID: $MARKETING_PID)${NC}"
else
    echo -e "${RED}❌ Marketing API failed to start${NC}"
fi
echo ""

echo -e "${BLUE}[4/5] Starting Sales Manager API (Port 8004)...${NC}"
nohup $PYTHON_CMD sales_manager_api.py > sales_manager_api.log 2>&1 &
SALES_PID=$!
sleep 5
if curl -s http://localhost:8004/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Sales Manager API started (PID: $SALES_PID)${NC}"
    # Show data stats
    curl -s http://localhost:8004/health | python -m json.tool | grep "total_transactions"
else
    echo -e "${RED}❌ Sales Manager API failed to start${NC}"
fi
echo ""

# ============ Start Spring Boot ============

echo -e "${BLUE}[5/5] Starting Spring Boot Application (Port 8080)...${NC}"
cd /home/ubuntu/DataScience/MyProject/dss-v2

# Check Java version
JAVA_VERSION=$(java -version 2>&1 | head -n 1 | awk -F '"' '{print $2}' | cut -d'.' -f1)
if [ "$JAVA_VERSION" != "17" ]; then
    echo -e "${RED}❌ Error: Java 17 required, found version $JAVA_VERSION${NC}"
    exit 1
fi

echo "Starting Spring Boot (this may take 30-60 seconds)..."
./mvnw spring-boot:run > spring-boot.log 2>&1 &
SPRING_PID=$!

# Wait for Spring Boot
MAX_WAIT=120
COUNTER=0
while [ $COUNTER -lt $MAX_WAIT ]; do
    if curl -s http://localhost:8080 > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✅ Spring Boot started (PID: $SPRING_PID)${NC}"
        break
    fi
    sleep 2
    COUNTER=$((COUNTER + 2))
    printf "."
done

if [ $COUNTER -ge $MAX_WAIT ]; then
    echo ""
    echo -e "${RED}❌ Spring Boot failed to start within $MAX_WAIT seconds${NC}"
    exit 1
fi

# ============ Summary ============

echo ""
echo "=================================="
echo -e "${GREEN}✅ ALL SERVICES STARTED!${NC}"
echo "=================================="
echo ""
echo "📊 API Health Status:"
echo "  Port 8001 - Admin API:        $(curl -s http://localhost:8001/health | grep -o '"status":"[^"]*"' || echo '❌')"
echo "  Port 8002 - Inventory API:    $(curl -s http://localhost:8002/health | grep -o '"status":"[^"]*"' || echo '❌')"
echo "  Port 8003 - Marketing API:    $(curl -s http://localhost:8003/health | grep -o '"status":"[^"]*"' || echo '❌')"
echo "  Port 8004 - Sales Manager:    $(curl -s http://localhost:8004/health | grep -o '"status":"[^"]*"' || echo '❌')"
echo "  Port 8080 - Spring Boot:      ✅"
echo ""
echo "🔗 Access URLs:"
echo "  🌐 Main Application:   http://localhost:8080"
echo "  🔐 Login Page:         http://localhost:8080/login"
echo "  📊 Sales Dashboard:    http://localhost:8080/sales/dashboard"
echo "  👔 Admin Dashboard:    http://localhost:8080/admin/dashboard"
echo "  📦 Inventory Dashboard: http://localhost:8080/inventory/dashboard"
echo "  📈 Marketing Dashboard: http://localhost:8080/marketing/dashboard"
echo ""
echo "📝 API Documentation:"
echo "  http://localhost:8001/docs - Admin API"
echo "  http://localhost:8002/docs - Inventory API"
echo "  http://localhost:8003/docs - Marketing API"
echo "  http://localhost:8004/docs - Sales Manager API"
echo ""
echo "🔐 Login Credentials:"
echo "  Admin:     admin / admin123"
echo "  Sales:     sales / sales123"
echo "  Inventory: inventory / inventory123"
echo "  Marketing: marketing / marketing123"
echo ""
echo "📋 Process IDs:"
echo "  Admin API:     $ADMIN_PID"
echo "  Inventory API: $INVENTORY_PID"
echo "  Marketing API: $MARKETING_PID"
echo "  Sales API:     $SALES_PID"
echo "  Spring Boot:   $SPRING_PID"
echo ""
echo "🛑 To stop all services:"
echo "  ./stop.sh"
echo "  Or manually: kill $ADMIN_PID $INVENTORY_PID $MARKETING_PID $SALES_PID $SPRING_PID"
echo ""
echo "📊 View logs:"
echo "  tail -f python-apis/admin_api.log"
echo "  tail -f python-apis/inventory_api.log"
echo "  tail -f python-apis/marketing_api.log"
echo "  tail -f python-apis/sales_manager_api.log"
echo "  tail -f spring-boot.log"
echo ""
