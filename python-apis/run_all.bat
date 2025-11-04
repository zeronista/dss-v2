@echo off
echo ====================================
echo Starting All Python APIs for DSS
echo ====================================
echo.

echo Starting Admin API (Port 8001)...
start "Admin API" cmd /k "python admin_api.py"
timeout /t 2 /nobreak > nul

echo Starting Inventory API (Port 8002)...
start "Inventory API" cmd /k "python inventory_api.py"
timeout /t 2 /nobreak > nul

echo Starting Marketing API (Port 8003)...
start "Marketing API" cmd /k "python marketing_api.py"
timeout /t 2 /nobreak > nul

echo Starting Sales API (Port 8004)...
start "Sales API" cmd /k "python sales_api.py"
timeout /t 2 /nobreak > nul

echo.
echo ====================================
echo All APIs are starting...
echo ====================================
echo.
echo Admin API:     http://localhost:8001/docs
echo Inventory API: http://localhost:8002/docs
echo Marketing API: http://localhost:8003/docs
echo Sales API:     http://localhost:8004/docs
echo.
echo Press any key to close this window...
pause > nul
