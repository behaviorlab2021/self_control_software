@echo off
:: Change directory to the backend and start the server
echo Starting Node.js backend...
cd C:\Users\SKINNER BOX\Documents\self_control_software\visualizer\backend
start cmd /k "node server.js"

:: Change directory to the frontend and start the React app
echo Starting React app...
cd C:\Users\SKINNER BOX\Documents\self_control_software\visualizer\frontend
start cmd /k "npm run start"

echo Both backend and frontend are starting. Press any key to close this window.
pause > nul
