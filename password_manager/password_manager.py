import sys
import os

print(sys.path)

# Add the USB drive's libs directory to the system path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIBS_DIR = os.path.join(SCRIPT_DIR, '..', 'python', 'libs')
sys.path.insert(0, LIBS_DIR)

try:
    import _cffi_backend
except ImportError:
    print("Installing _cffi_backend...")
    os.system(f"{os.path.join(SCRIPT_DIR, '..', 'python', 'python-3.12.8.amd64', 'python.exe')} -m pip install --target={LIBS_DIR} cffi")

from cryptography.fernet import Fernet
import json
import pygetwindow as gw
import threading
import time
import tkinter as tk
from tkinter import messagebox

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(SCRIPT_DIR, 'database')
KEY_FILE = os.path.join(DB_DIR, 'partial_key.json')
PASSWORDS_FILE = os.path.join(DB_DIR, 'passwords.json')
CHECK_FILE = os.path.join(DB_DIR, 'check_file.txt')

stop_detection = threading.Event()

os.makedirs(DB_DIR, exist_ok=True)

def generate_key():
    key = Fernet.generate_key().decode()
    partial_key = key[:-6]
    master_password = key[-6:]
    return partial_key, master_password

def save_partial_key(partial_key):
    with open(KEY_FILE, 'w') as file:
        json.dump({"partial_key": partial_key}, file)

def load_partial_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'r') as file:
            return json.load(file)["partial_key"]
    return None

def reconstruct_key(partial_key, master_password):
    return (partial_key + master_password).encode()

def create_check_file(full_key):
    validation_sentence = "This is a validation sentence."
    fernet = Fernet(full_key)
    encrypted_sentence = fernet.encrypt(validation_sentence.encode()).decode()
    with open(CHECK_FILE, 'w') as file:
        file.write(encrypted_sentence)

def verify_check_file(full_key):
    if not os.path.exists(CHECK_FILE):
        return False
    with open(CHECK_FILE, 'r') as file:
        encrypted_sentence = file.read().strip()
    try:
        fernet = Fernet(full_key)
        decrypted_sentence = fernet.decrypt(encrypted_sentence.encode()).decode()
        return decrypted_sentence == "This is a validation sentence."
    except:
        return False

def encrypt_password(full_key, password):
    fernet = Fernet(full_key)
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(full_key, encrypted_password):
    fernet = Fernet(full_key)
    return fernet.decrypt(encrypted_password.encode()).decode()

def load_passwords():
    if os.path.exists(PASSWORDS_FILE):
        with open(PASSWORDS_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_passwords(passwords):
    with open(PASSWORDS_FILE, 'w') as file:
        json.dump(passwords, file, indent=4)

def reset_encryption_key():
    partial_key = load_partial_key()
    if not partial_key:
        print("Error: Partial key not found. Cannot reset encryption key.")
        return

    master_password = input("Enter your current master password: ")
    current_full_key = reconstruct_key(partial_key, master_password)

    if not verify_check_file(current_full_key):
        print("Invalid master password. Cannot reset encryption key.")
        return

    passwords = load_passwords()

    decrypted_passwords = {}
    for site, credentials in passwords.items():
        decrypted_passwords[site] = {
            "username": credentials["username"],
            "password": decrypt_password(current_full_key, credentials["password"])
        }

    new_partial_key, new_master_password = generate_key()
    save_partial_key(new_partial_key)
    new_full_key = reconstruct_key(new_partial_key, new_master_password)

    reencrypted_passwords = {}
    for site, credentials in decrypted_passwords.items():
        reencrypted_passwords[site] = {
            "username": credentials["username"],
            "password": encrypt_password(new_full_key, credentials["password"])
        }

    save_passwords(reencrypted_passwords)
    create_check_file(new_full_key)
    print("Encryption key and master password have been reset.")
    print("Your new master password is:", new_master_password)
    print("Save it securely! It will not be shown again.")

def list_open_windows():
    windows = gw.getAllTitles()
    return [window for window in windows if window.strip()]

def display_password_in_foreground(full_key, site, credentials):
    def copy_to_clipboard(text):
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()  # now it stays on the clipboard after the window is closed

    def stop_detection_event():
        stop_detection.set()
        root.destroy()

    def continue_detection_event():
        root.destroy()

    root = tk.Tk()
    root.title("Password Manager")
    
    # Make the window come to the foreground
    root.attributes("-topmost", True)
    
    tk.Label(root, text=f"Service: {site}").pack()
    tk.Label(root, text=f"Username: {credentials['username']}").pack()
    
    password_text = decrypt_password(full_key, credentials['password'])
    
    tk.Label(root, text=f"Password: {password_text}").pack()
    
    copy_button = tk.Button(root, text="Copy Password", command=lambda: copy_to_clipboard(password_text))
    copy_button.pack()
    
    stop_button = tk.Button(root, text="Stop Detection", command=stop_detection_event)
    stop_button.pack(side=tk.LEFT)
    
    continue_button = tk.Button(root, text="Continue Detection", command=continue_detection_event)
    continue_button.pack(side=tk.RIGHT)
    
    root.mainloop()

def detect_windows(full_key):
    print("Running window detection in background...")
    passwords = load_passwords()
    while not stop_detection.is_set():
        open_windows = list_open_windows()
        for window in open_windows:
            for site, credentials in passwords.items():
                if site.lower() in window.lower():
                    display_password_in_foreground(full_key, site, credentials)
        time.sleep(5)

def main():
    partial_key = load_partial_key()
    if not partial_key:
        partial_key, master_password = generate_key()
        save_partial_key(partial_key)
        full_key = reconstruct_key(partial_key, master_password)
        create_check_file(full_key)
        print("Your master password is:", master_password)
        print("Save it securely! It will not be shown again.")
        return

    master_password = input("Enter your master password: ")
    full_key = reconstruct_key(partial_key, master_password)

    if not verify_check_file(full_key):
        print("Invalid master password or tampered files.")
        return

    passwords = load_passwords()

    while True:
        print("\nPassword Manager")
        print("1. Add Password")
        print("2. Get Password")
        print("3. Modify Password")
        print("4. Delete Password")
        print("5. Reset Encryption Key and Master Password")
        print("6. Detect Window")
        print("7. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            site = input("Enter the site name: ")
            username = input("Enter the username: ")
            password = input("Enter the password: ")
            encrypted_password = encrypt_password(full_key, password)
            passwords[site] = {"username": username, "password": encrypted_password}
            save_passwords(passwords)
            print(f"Password for {site} added.")

        elif choice == '2':
            site = input("Enter the site name: ")
            if site in passwords:
                try:
                    encrypted_password = passwords[site]["password"]
                    decrypted_password = decrypt_password(full_key, encrypted_password)
                    print(f"Password for {site}: {decrypted_password}")
                except:
                    print("Error decrypting password.")
            else:
                print("Site not found.")

        elif choice == '3':
            site = input("Enter the site name: ")
            if site in passwords:
                new_password = input("Enter the new password: ")
                encrypted_password = encrypt_password(full_key, new_password)
                passwords[site]["password"] = encrypted_password
                save_passwords(passwords)
                print(f"Password for {site} updated.")
            else:
                print("Site not found.")

        elif choice == '4':
            site = input("Enter the site name: ")
            if site in passwords:
                del passwords[site]
                save_passwords(passwords)
                print(f"Password for {site} deleted.")
            else:
                print("Site not found.")

        elif choice == '5':
            reset_encryption_key()

        elif choice == '6':
            detection_thread = threading.Thread(target=detect_windows, args=(full_key,))
            detection_thread.daemon = True
            detection_thread.start()
            print("Window detection started. Press Enter to stop.")
            input()
            stop_detection.set()  # Signal the detection thread to stop
            detection_thread.join()
            stop_detection.clear()  # Reset the flag for future use

        elif choice == '7':
            print("Exiting Password Manager.")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()