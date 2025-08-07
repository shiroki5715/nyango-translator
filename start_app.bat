@echo off
echo Starting server in background...
start "kakaku-analyzer-server" /B python web_server.py
echo Finding server PID...
for /f "tokens=2" %%i in ('tasklist /v /fi "IMAGENAME eq python.exe" /fi "WINDOWTITLE eq kakaku-analyzer-server" ^| find "python.exe"') do (
    echo %%i > server.pid
    goto :found
)
:found
if not exist server.pid (
    echo Failed to find server PID.
    exit /b 1
)
echo Server started. PID saved to server.pid.
echo Waiting for 5 seconds...
ping 127.0.0.1 -n 6 > nul
echo Opening browser...
start http://127.0.0.1:5001
exit