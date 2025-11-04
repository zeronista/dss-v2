@echo off
echo ====================================
echo Testing Python APIs Integration
echo ====================================
echo.

echo Testing Admin API (Port 8001)...
curl -s http://localhost:8001/health
echo.
echo.

echo Testing Inventory API (Port 8002)...
curl -s http://localhost:8002/health
echo.
echo.

echo Testing Marketing API (Port 8003)...
curl -s http://localhost:8003/health
echo.
echo.

echo Testing Sales API (Port 8004)...
curl -s http://localhost:8004/health
echo.
echo.

echo ====================================
echo Testing Spring Boot Gateway...
echo ====================================
echo.

echo Testing Gateway Health Check...
curl -s http://localhost:8080/api/gateway/health
echo.
echo.

echo ====================================
echo Test Admin API via Gateway...
echo ====================================
curl -X POST http://localhost:8080/api/gateway/admin/kpis ^
  -H "Content-Type: application/json" ^
  -d "{}"
echo.
echo.

echo ====================================
echo All tests completed!
echo ====================================
pause
