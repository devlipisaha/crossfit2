@echo off
cd /d "%~dp0"
where node >nul 2>nul || (echo Node.js is not installed. Install the LTS version from https://nodejs.org and run this file again. & pause & exit /b 1)
echo Keep this window open while streaming. Press Ctrl+C to stop.
node server.js
pause
