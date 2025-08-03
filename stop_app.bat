@echo off
echo Stopping server with window title "kakaku-analyzer-server"...
taskkill /FI "WINDOWTITLE eq kakaku-analyzer-server" /T /F
echo Server stop command executed.
ping 127.0.0.1 -n 3 > nul
exit
