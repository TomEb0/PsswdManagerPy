PsswdManagerPY
PsswdManagerPY is a USB-based password manager written in Python. It allows you to securely manage your passwords directly from a USB drive, with all necessary libraries installed on the USB itself.

Features
Add, Modify, Delete, and Retrieve Passwords: Manage your passwords with ease.
Encryption: Passwords are encrypted with a key generated on the first launch.
Window Detection: Automatically display the username and password if a window's name matches a service's name.
Installation
Ensure the USB stick is dedicated to PsswdManagerPY2 and does not contain any other files.
Copy the password_manager and python folders to the USB stick.
Navigate to the password_manager folder on the USB stick.
Execute launch.bat to launch the application for the first time. This will generate the password for the password manager. Make sure to copy this password; otherwise, you will need to reset the password manager.
If you need to reset the password manager, delete the database folder inside the password_manager folder.
If any issues occur with the libraries, run setup.bat inside the password_manager folder to resolve them.
Usage
Run the application by executing launch.bat in the password_manager folder.
Follow the on-screen instructions to add, modify, delete, or retrieve passwords.
Enable window detection to automatically display credentials for matching windows.
Contributing
Contributions are welcome! Please fork the repository and submit a pull request.
