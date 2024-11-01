import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, Menu

# Connect to server
def connect_to_server():
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 5555))
    
    # Send the username to the server once when connecting
    client_socket.send(username.encode("utf-8"))
    
    # Start a new thread to listen for messages from the server
    threading.Thread(target=receive_messages).start()

# Send message to server
def send_message():
    msg = message_input.get()
    if msg:
        # Format the message with the username
        full_msg = f"{username}: {msg}"
        client_socket.send(full_msg.encode("utf-8"))

        # Display the message in the client's own chat display with username
        chat_display.config(state=tk.NORMAL)
        chat_display.insert(tk.END, f"{username}: {msg}\n", "user")
        chat_display.config(state=tk.DISABLED)
        chat_display.see(tk.END)

        # Clear the input field after sending the message
        message_input.delete(0, tk.END)

# Receive messages from server
def receive_messages():
    while True:
        try:
            msg = client_socket.recv(1024).decode("utf-8")
            if msg == 'USERNAME':
                client_socket.send(username.encode())
                print('username!')
            elif msg:
                print('Message alive!')
                chat_display.config(state=tk.NORMAL)
                chat_display.insert(tk.END, msg + "\n")
                chat_display.config(state=tk.DISABLED)
                chat_display.see(tk.END)
        except:
            print("Disconnected from server")
            break

# Theme configurations
themes = {
    "dark": {
        "bg_color": "#2C2F33",
        "text_color": "#FFFFFF",
        "entry_bg": "#23272A",
        "button_bg": "#7289DA",
        "button_text": "#FFFFFF",
        "menu_bg": "#23272A",
        "menu_fg": "#FFFFFF"
    },
    "light": {
        "bg_color": "#FFFFFF",
        "text_color": "#000000",
        "entry_bg": "#F0F0F0",
        "button_bg": "#4CAF50",
        "button_text": "#FFFFFF",
        "menu_bg": "#E0E0E0",
        "menu_fg": "#000000"
    },
    "purple": {
        "bg_color": "#3B1E5F",
        "text_color": "#EAD1FF",
        "entry_bg": "#5A2E85",
        "button_bg": "#9B59B6",
        "button_text": "#FFFFFF",
        "menu_bg": "#5A2E85",
        "menu_fg": "#EAD1FF"
    },
    "blue": {
        "bg_color": "#1A1A40",
        "text_color": "#A3C4DC",
        "entry_bg": "#1E2749",
        "button_bg": "#5679D0",
        "button_text": "#FFFFFF",
        "menu_bg": "#1E2749",
        "menu_fg": "#A3C4DC"
    },
    "green": {
        "bg_color": "#243E36",
        "text_color": "#C8E6C9",
        "entry_bg": "#2E4E3F",
        "button_bg": "#4CAF50",
        "button_text": "#FFFFFF",
        "menu_bg": "#2E4E3F",
        "menu_fg": "#C8E6C9"
    },
    "red": {
        "bg_color": "#4A1C1C",
        "text_color": "#F8D7DA",
        "entry_bg": "#5D2C2C",
        "button_bg": "#FF5252",
        "button_text": "#FFFFFF",
        "menu_bg": "#5D2C2C",
        "menu_fg": "#F8D7DA"
    }
}

theme_order = list(themes.keys())  # Use all themes in dictionary keys
current_theme = theme_order[0]  # Start with the "dark" theme

def apply_theme(theme):
    theme_config = themes[theme]
    root.configure(bg=theme_config["bg_color"])
    chat_display.config(bg=theme_config["bg_color"], fg=theme_config["text_color"])
    message_input.config(bg=theme_config["entry_bg"], fg=theme_config["text_color"], insertbackground=theme_config["text_color"])
    send_button.config(bg=theme_config["button_bg"], fg=theme_config["button_text"])

    # Apply theme to the menu bar
    settings_menu.config(bg=theme_config["menu_bg"], fg=theme_config["menu_fg"])
    for item in theme_menu.winfo_children():
        item.config(bg=theme_config["menu_bg"], fg=theme_config["menu_fg"])

def select_theme(selected_theme):
    global current_theme
    current_theme = selected_theme
    apply_theme(current_theme)

# Setup GUI
root = tk.Tk()
root.title("TCP Chat")

# Prompt the user for a username
username = simpledialog.askstring("Username", "Enter your username:", parent=root)

# Chat display configuration
chat_display = scrolledtext.ScrolledText(root, state=tk.DISABLED, font=("Arial", 12))
chat_display.tag_config("user", foreground="#00FF00")
chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Message input field configuration
message_input = tk.Entry(root, font=("Arial", 12))
message_input.pack(fill=tk.X, padx=10, pady=(0, 10))
message_input.bind("<Return>", lambda event: send_message())

# Send button configuration
send_button = tk.Button(root, text="Send", command=send_message, font=("Arial", 12))
send_button.pack(pady=(0, 10))

# Create a menu bar with a settings menu for theme selection
menu_bar = Menu(root)
settings_menu = Menu(menu_bar, tearoff=0)

# Create a submenu for theme selection
theme_menu = Menu(settings_menu, tearoff=0)
for theme in theme_order:
    theme_menu.add_command(label=theme.capitalize(), command=lambda t=theme: select_theme(t))
settings_menu.add_cascade(label="Choose Theme", menu=theme_menu)

menu_bar.add_cascade(label="Settings", menu=settings_menu)
root.config(menu=menu_bar)

# Apply the default theme after setting up GUI elements
apply_theme(current_theme)

# Connect to server after setting up GUI
connect_to_server()
root.mainloop()