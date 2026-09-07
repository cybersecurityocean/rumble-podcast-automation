@echo off
echo.
echo ============================================
echo   RUMBLE COOKIE CAPTURE
echo ============================================
echo.
echo   Browser will open. Log in to Rumble.
echo   Then come back here and press any key.
echo.
pause
python "%~dp0capture_cookies.py"
echo.
echo   Done! Check rumble_cookies.json
echo.
pause
