@echo off
setlocal

:: Automatically detect the drive letter of the USB drive
set USB_DRIVE=%~d0

:: Set the path to the Python executable in the WinPython folder
set PYTHON_PATH=%USB_DRIVE%\python\python\python\python.exe

:: Check if Python is installed in the WinPython folder
if not exist "%PYTHON_PATH%" (
    echo Python is not installed in the WinPython folder.
    echo Please verify your WinPython installation.
    pause
    exit /b 1
)

:: Install required libraries into the USB libs folder
"%PYTHON_PATH%" -m pip install --no-warn-script-location --target=%USB_DRIVE%\python\libs -r %USB_DRIVE%\password_manager\requirements.txt

echo Setup complete.
pause
