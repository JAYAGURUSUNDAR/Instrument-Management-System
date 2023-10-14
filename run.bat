@echo off
setlocal

:: Check if Python is installed
python --version 2>NUL
if %errorlevel% NEQ 0 (
    echo Python is not installed. Installing Python...
    
    :: Download and install Python
    :: Change the URL to the latest Python installer URL
    powershell -command "(New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.x.x/python-3.x.x-amd64.exe', 'python_installer.exe')"
    
    :: Install Python silently
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1

    :: Clean up the installer (optional)
    del python_installer.exe
)

:: Install PyInstaller using pip
python -m pip install pyinstaller

:: Convert your Python script to an executable
pyinstaller --onefile main.py

:: Replace "your_script.py" with the actual name of your Python script

endlocal
