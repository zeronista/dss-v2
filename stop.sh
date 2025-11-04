#!/bin/bash
# Stop DSS-v2 Application

echo "=================================="
echo "Stopping DSS-v2 Application"
echo "=================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Stop Python API (port 8004)
if lsof -Pi :8004 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "Stopping Python API (port 8004)..."
    kill -9 $(lsof -ti:8004) 2>/dev/null
    echo -e "${GREEN}✅ Python API stopped${NC}"
else
    echo "Python API not running"
fi

# Stop Spring Boot (port 8080)
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "Stopping Spring Boot (port 8080)..."
    kill -9 $(lsof -ti:8080) 2>/dev/null
    echo -e "${GREEN}✅ Spring Boot stopped${NC}"
else
    echo "Spring Boot not running"
fi

# Also stop any mvnw processes
pkill -f "mvnw spring-boot:run" 2>/dev/null

echo ""
echo -e "${GREEN}All services stopped.${NC}"
