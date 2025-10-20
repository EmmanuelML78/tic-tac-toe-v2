@echo off
echo ========================================
echo Starting Tic-Tac-Toe Frontend Server
echo ========================================
echo.

cd frontend

echo Starting HTTP server...
echo Frontend will be available at: http://localhost:8080/public/index.html
echo.
echo IMPORTANT: Keep this window open while playing!
echo Press Ctrl+C to stop the server
echo.

python -m http.server 8080

pause
