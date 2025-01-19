@echo off
:: Automatically detect the drive letter of the USB drive
set USB_DRIVE=%~d0

:: Navigate to the password manager folder
cd %USB_DRIVE%\password_manager

:: Run the password manager script using the Python executable from the USB drive
%USB_DRIVE%\python\python\python\python.exe password_manager.py

:: Pause to keep the command prompt window open after execution
pause
