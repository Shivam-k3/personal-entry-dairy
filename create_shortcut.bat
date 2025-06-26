@echo off
echo Creating Desktop Shortcut for Journal App...

:: Get the current directory
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: Create the shortcut
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Journal App.lnk'); $Shortcut.TargetPath = 'powershell.exe'; $Shortcut.Arguments = '-ExecutionPolicy Bypass -File \"%SCRIPT_DIR%\start_journal.ps1\"'; $Shortcut.WorkingDirectory = '%SCRIPT_DIR%'; $Shortcut.Description = 'Personal Daily Journal with AI Sentiment Tracker'; $Shortcut.IconLocation = 'powershell.exe,0'; $Shortcut.Save()"

echo.
echo ✓ Desktop shortcut created successfully!
echo You can now double-click "Journal App" on your desktop to start the app.
echo.
pause 