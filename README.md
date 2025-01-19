# PsswdManagerPy

PsswdManagerPy is a USB-based password manager written in Python. It allows you to securely manage your passwords directly from a USB drive, with all necessary libraries installed on the USB itself.

## Features

- **Add, Modify, Delete, and Retrieve Passwords**: Manage your passwords with ease.
- **Encryption**: Passwords are encrypted with a key generated on the first launch.
- **Window Detection**: Automatically display the username and password if a window's name matches a service's name.

## Installation

1. Clone the repository to your USB drive:
    ```bash
    git clone https://github.com/TomEb0/PsswdManagerPy
    ```
    Or download it from here: https://github.com/TomEb0/PsswdManagerPy/archive/refs/heads/main.zip
   (If you download the zip make sure that the 2 first folder to appear when you open your usb stick are password_manager and python)

## Usage

1. Run the application:
    ```bash
    launch.bat
    ```
    Or execute the launch.bat.
   Be sure to remember the password provided when you first launch the program. 
3. Follow the on-screen instructions to add, modify, delete, or retrieve passwords.
4. Enable window detection to automatically display credentials for matching windows.
If you delete the database folder, the program will reset as if it is being launched for the first time.

## Libraries Used

### Included with Python:
1. **sys**: Provides access to some variables used or maintained by the interpreter and to functions that interact strongly with the interpreter.
2. **os**: Provides a way of using operating system dependent functionality like reading or writing to the file system.
3. **json**: Provides an easy way to encode and decode data in JSON format.
4. **threading**: A module for creating and managing threads in Python.
5. **time**: Provides various time-related functions.
6. **tkinter**: A standard GUI package for Python.

### Need to be installed separately:
1. **_cffi_backend**: Part of the `cffi` package.
2. **cryptography.fernet**: Part of the `cryptography` package.
3. **pygetwindow**: A module for getting and manipulating windows on your screen.
