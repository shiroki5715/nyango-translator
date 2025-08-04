@echo off
echo Stopping server...
if not exist server.pid (
    echo server.pid not found. Server may not be running.
    exit /b 0
)
set /p PID=<server.pid
echo Stopping process with PID: %PID%
taskkill /F /PID %PID%
del server.pid
echo Server stopped successfully.
exit
