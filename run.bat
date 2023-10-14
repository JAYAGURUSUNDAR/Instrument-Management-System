@echo off
setlocal

python --version 2>NUL
if %errorlevel% NEQ 0 (
    echo Python is not installed. Installing Python..
    powershell -command "(New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.x.x/python-3.x.x-amd64.exe', 'python_installer.exe')"
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=
    del python_installer.exe
)

python -m pip install pyinstaller

pyinstaller --onefile --noconsole --icon=IMS.ico main.py --name IMS

:: Create a desktop shortcut
set SHORTCUT_PATH=%USERPROFILE%\Desktop\IMS.lnk
echo Set WshShell = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo Set shortcut = WshShell.CreateShortcut("%SHORTCUT_PATH%") >> CreateShortcut.vbs
echo shortcut.TargetPath = "%CD%\dist\IMS.exe" >> CreateShortcut.vbs
echo shortcut.IconLocation = "%CD%\IMS.ico" >> CreateShortcut.vbs
echo shortcut.Save >> CreateShortcut.vbs
cscript //nologo CreateShortcut.vbs
del CreateShortcut.vbs

:: Add to Windows startup
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
copy "%CD%\dist\IMS.exe" "%STARTUP_FOLDER%\IMS.exe"

endlocal
