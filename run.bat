@echo off
echo ========================================================
echo   Starting ShopFlow E-Commerce Development Server
echo ========================================================
echo.
echo Opening server at http://127.0.0.1:8000/
echo Press CTRL+C in this terminal window to stop the server.
echo.
.\venv\Scripts\python.exe manage.py runserver
pause
