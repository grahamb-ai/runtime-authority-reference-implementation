@echo off
setlocal
cd /d "%~dp0"
echo.
echo  FlowSignal Ambient Scribing Runtime Authority Demo
echo  -------------------------------------------------
echo  Opening the demo in your normal web browser...
echo.
start "" "%~dp0ambient-scribing.html"
timeout /t 2 /nobreak >nul
exit /b 0
