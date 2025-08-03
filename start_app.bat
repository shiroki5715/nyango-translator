@echo off
echo Starting server in background...
start "kakaku-analyzer-server" /B python web_server.py

echo Waiting for 5 seconds...
ping 127.0.0.1 -n 6 > nul

echo Opening browser...
start http://127.0.0.1:5000

exit
