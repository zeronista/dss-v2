#!/bin/bash
# Optimized Start Script - Multi-worker với async processing
# Mở full port API với xử lý bất đồng bộ

echo "🚀 Starting DSS-v2 with OPTIMIZED ASYNC MODE"
echo "============================================"
echo ""

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Activate conda
if command -v conda &> /dev/null; then
    eval "$(conda shell.bash hook)"
    conda activate base
fi

cd /home/ubuntu/DataScience/MyProject/dss-v2/python-apis

# Check if port 8004 is in use
if lsof -Pi :8004 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  Stopping existing API on port 8004...${NC}"
    kill -9 $(lsof -ti:8004) 2>/dev/null
    sleep 2
fi

echo -e "${BLUE}Starting Python API with ASYNC WORKERS...${NC}"
echo ""
echo "Configuration:"
echo "  ⚡ Workers: 4 (multi-process)"
echo "  🔧 Thread pool: 20 per worker"
echo "  📊 Data: 530,104 transactions (FULL)"
echo "  🌐 Host: 0.0.0.0:8004"
echo ""

# Start with Gunicorn (production-ready ASGI server with multiple workers)
nohup gunicorn sales_manager_api:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8004 \
    --timeout 120 \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --log-level info \
    --access-logfile sales_manager_access.log \
    --error-logfile sales_manager_error.log \
    > sales_manager.log 2>&1 &

PYTHON_PID=$!

echo "Waiting for API to start..."
sleep 8

# Check health
if curl -s http://localhost:8004/health > /dev/null 2>&1; then
    echo ""
    echo -e "${GREEN}✅ ASYNC API Started Successfully!${NC}"
    echo ""
    echo "📊 Status:"
    curl -s http://localhost:8004/health | python -m json.tool
    echo ""
    echo "🔗 Endpoints:"
    echo "  📝 API Docs:  http://localhost:8004/docs"
    echo "  ❤️  Health:   http://localhost:8004/health"
    echo "  🛍️  Products: http://localhost:8004/product-search?q=HEART"
    echo ""
    echo "⚡ Performance:"
    echo "  - 4 worker processes (parallel request handling)"
    echo "  - Async I/O for non-blocking operations"
    echo "  - 530K transactions loaded per worker"
    echo ""
    echo "📊 Logs:"
    echo "  Main:   tail -f sales_manager.log"
    echo "  Access: tail -f sales_manager_access.log"
    echo "  Error:  tail -f sales_manager_error.log"
    echo ""
    echo "🛑 To stop: kill $PYTHON_PID"
else
    echo -e "${RED}❌ Failed to start API${NC}"
    tail -20 sales_manager.log
    exit 1
fi
