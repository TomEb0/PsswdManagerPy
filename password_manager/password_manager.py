# Import necessary modules for system, OS operations, and cryptographic functionality
import sys
import os

# Print the current Python module search paths (for debugging purposes)
print(sys.path)

# Set the script and library directory paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIBS_DIR = os.path.join(SCRIPT_DIR, '..', 'python', 'libs')
sys.path.insert(0, LIBS_DIR)  # Add the library directory to Python's module search path

# Import essential modules and libraries
from cryptography.fernet import Fernet  # For encryption and decryption
import json  # For reading and writing JSON files
import pygetwindow as gw  # For listing open windows
import threading  # For multithreading support
import time  # For adding delays in loops
import tkinter as tk  # For GUI components
from tkinter import messagebox  # For displaying dialog boxes

# Define paths for storing database files
DB_DIR = os.path.join(SCRIPT_DIR, 'database')
KEY_FILE = os.path.join(DB_DIR, 'partial_key.json')
PASSWORDS_FILE = os.path.join(DB_DIR, 'passwords.json')
CHECK_FILE = os.path.join(DB_DIR, 'check_file.txt')

# Event flag for stopping background threads
stop_detection = threading.Event()

# Ensure the database directory exists
os.makedirs(DB_DIR, exist_ok=True)

# Function to generate a new encryption key and master password
def generate_key():
    key = Fernet.generate_key().decode()  # Generate a new key
    partial_key = key[:-6]  # Split into partial key
    master_password = key[-6:]  # Extract the last 6 characters as the master password
    return partial_key, master_password

# Save the partial key to a file
def save_partial_key(partial_key):
    with open(KEY_FILE, 'w') as file:
        json.dump({"partial_key": partial_key}, file)

# Load the partial key from a file, if it exists
def load_partial_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'r') as file:
            return json.load(file)["partial_key"]
    return None

# Reconstruct the full encryption key using the partial key and master password
def reconstruct_key(partial_key, master_password):
    return (partial_key + master_password).encode()

# Create a check file with an encrypted validation sentence
def create_check_file(full_key):
    validation_sentence = "This is a validation sentence."
    fernet = Fernet(full_key)
    encrypted_sentence = fernet.encrypt(validation_sentence.encode()).decode()
    with open(CHECK_FILE, 'w') as file:
        file.write(encrypted_sentence)

# Verify the check file to ensure the key is valid
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

# Encrypt a password using the full key
def encrypt_password(full_key, password):
    fernet = Fernet(full_key)
    return fernet.encrypt(password.encode()).decode()

# Decrypt a password using the full key
def decrypt_password(full_key, encrypted_password):
    fernet = Fernet(full_key)
    return fernet.decrypt(encrypted_password.encode()).decode()

# Load saved passwords from the passwords file
def load_passwords():
    if os.path.exists(PASSWORDS_FILE):
        with open(PASSWORDS_FILE, 'r') as file:
            return json.load(file)
    return {}

# Save passwords to the passwords file
def save_passwords(passwords):
    with open(PASSWORDS_FILE, 'w') as file:
        json.dump(passwords, file, indent=4)

# Reset the encryption key and re-encrypt all saved passwords
def reset_encryption_key():
    partial_key = load_partial_key()
    if not partial_key:
        print("Error: Partial key not found. Cannot reset encryption key.")
        return

    # Authenticate with the current master password
    master_password = input("Enter your current master password: ")
    current_full_key = reconstruct_key(partial_key, master_password)

    if not verify_check_file(current_full_key):
        print("Invalid master password. Cannot reset encryption key.")
        return

    passwords = load_passwords()

    # Decrypt all stored passwords
    decrypted_passwords = {}
    for site, credentials in passwords.items():
        decrypted_passwords[site] = {
            "username": credentials["username"],
            "password": decrypt_password(current_full_key, credentials["password"])
        }

    # Generate a new key and re-encrypt passwords
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

# List all open windows
def list_open_windows():
    windows = gw.getAllTitles()
    return [window for window in windows if window.strip()]

# Display password details in a GUI window
def display_password_in_foreground(full_key, site, credentials):
    def copy_to_clipboard(text):
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()

    def stop_detection_event():
        stop_detection.set()
        root.destroy()

    def continue_detection_event():
        root.destroy()

    root = tk.Tk()
    root.title("Password Manager")
    root.attributes("-topmost", True)  # Ensure the window is on top

    # Display details and buttons
    tk.Label(root, text=f"Service: {site}").pack()
    tk.Label(root, text=f"Username: {credentials['username']}").pack()
    password_text = decrypt_password(full_key, credentials['password'])
    tk.Label(root, text=f"Password: {password_text}").pack()
    tk.Button(root, text="Copy Password", command=lambda: copy_to_clipboard(password_text)).pack()
    tk.Button(root, text="Stop Detection", command=stop_detection_event).pack(side=tk.LEFT)
    tk.Button(root, text="Continue Detection", command=continue_detection_event).pack(side=tk.RIGHT)

    root.mainloop()

# Detect open windows and match them against saved sites
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

# Main function for the password manager
def main():
    # Load the partial key or generate a new one
    partial_key = load_partial_key()
    if not partial_key:
        partial_key, master_password = generate_key()
        save_partial_key(partial_key)
        full_key = reconstruct_key(partial_key, master_password)
        create_check_file(full_key)
        print("Your master password is:", master_password)
        print("Save it securely! It will not be shown again.")
        return

    # Authenticate with the master password
    master_password = input("Enter your master password: ")
    full_key = reconstruct_key(partial_key, master_password)

    if not verify_check_file(full_key):
        print("Invalid master password or tampered files.")
        return

    passwords = load_passwords()

    # Menu loop
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

# Entry point of the script
if __name__ == "__main__":
    main()
