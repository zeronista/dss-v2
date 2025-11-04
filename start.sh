#!/bin/bash
# Start DSS-v2 Application
# Chạy cả Python API và Spring Boot

echo "=================================="
echo "Starting DSS-v2 Application"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Java version
JAVA_VERSION=$(java -version 2>&1 | head -n 1 | awk -F '"' '{print $2}' | cut -d'.' -f1)
echo -e "${BLUE}Java Version: ${NC}$JAVA_VERSION"

if [ "$JAVA_VERSION" != "17" ]; then
    echo -e "${RED}❌ Error: Java 17 required, found version $JAVA_VERSION${NC}"
    echo "Please install Java 17:"
    echo "  sudo apt install -y openjdk-17-jdk"
    echo "  sudo update-alternatives --config java"
    exit 1
fi

echo -e "${GREEN}✅ Java 17 detected${NC}"
echo ""

# Step 1: Start Python API
echo -e "${BLUE}[1/2] Starting Python API (Sales Manager)...${NC}"
cd /home/ubuntu/DataScience/MyProject/dss-v2/python-apis

# Check if already running
if lsof -Pi :8004 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Port 8004 already in use. Stopping existing process..."
    kill -9 $(lsof -ti:8004) 2>/dev/null
    sleep 2
fi

# Start Python API
nohup python3 sales_manager_api.py > sales_manager.log 2>&1 &
PYTHON_PID=$!

echo "Waiting for Python API to start..."
sleep 4

# Check if API started
if curl -s http://localhost:8004/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Python API started successfully (PID: $PYTHON_PID)${NC}"
    echo "   Health check: http://localhost:8004/health"
else
    echo -e "${RED}❌ Failed to start Python API${NC}"
    echo "Check logs: tail -f python-apis/sales_manager.log"
    exit 1
fi
echo ""

# Step 2: Start Spring Boot
echo -e "${BLUE}[2/2] Starting Spring Boot Application...${NC}"
cd /home/ubuntu/DataScience/MyProject/dss-v2

# Check if already running
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Port 8080 already in use. Stopping existing process..."
    kill -9 $(lsof -ti:8080) 2>/dev/null
    sleep 2
fi

echo "Starting Spring Boot (this may take 30-60 seconds)..."
echo ""

# Start Spring Boot
./mvnw spring-boot:run &
SPRING_PID=$!

echo "Waiting for Spring Boot to start (please wait)..."
echo ""

# Wait for Spring Boot to be ready (max 120 seconds)
MAX_WAIT=120
COUNTER=0
while [ $COUNTER -lt $MAX_WAIT ]; do
    if curl -s http://localhost:8080 > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✅ Spring Boot started successfully (PID: $SPRING_PID)${NC}"
        break
    fi
    sleep 2
    COUNTER=$((COUNTER + 2))
    printf "."
done

if [ $COUNTER -ge $MAX_WAIT ]; then
    echo ""
    echo -e "${RED}❌ Spring Boot failed to start within $MAX_WAIT seconds${NC}"
    echo "Check logs above for errors"
    exit 1
fi

echo ""
echo "=================================="
echo -e "${GREEN}✅ DSS-v2 Started Successfully!${NC}"
echo "=================================="
echo ""
echo "Access URLs:"
echo "  🌐 Main Application: http://localhost:8080"
echo "  🔐 Login Page:       http://localhost:8080/login"
echo "  📊 Sales Dashboard:  http://localhost:8080/sales/dashboard"
echo "  🔧 Python API Docs:  http://localhost:8004/docs"
echo ""
echo "Login Credentials:"
echo "  👤 Sales Manager:"
echo "     Username: sales"
echo "     Password: sales123"
echo ""
echo "  👤 Admin:"
echo "     Username: admin"
echo "     Password: admin123"
echo ""
echo "Process IDs:"
echo "  Python API: $PYTHON_PID"
echo "  Spring Boot: $SPRING_PID"
echo ""
echo "To stop:"
echo "  kill $PYTHON_PID $SPRING_PID"
echo "  Or run: ./stop.sh"
echo ""
