import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
from datetime import datetime

HOST = '127.0.0.1'
PORT = 65432

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("🎨 Group Chat Client")

       
        self.bg_color = "#f0f4f7"
        self.entry_bg = "#ffffff"
        self.btn_bg = "#4caf50"
        self.btn_fg = "#ffffff"
        self.chat_bg = "#e6f7ff"

        self.master.configure(bg=self.bg_color)

      
        frame = tk.Frame(master, bg=self.bg_color)
        frame.pack(padx=10, pady=10, fill='both', expand=True)

        self.chat_area = scrolledtext.ScrolledText(
            frame, state='disabled', wrap=tk.WORD, bg=self.chat_bg, font=("Segoe UI", 11), height=15
        )
        self.chat_area.pack(pady=(0, 10), fill='both', expand=True)

        self.chat_area.tag_config('me', foreground="#1e88e5", font=("Segoe UI", 11, "bold"))
        self.chat_area.tag_config('others', foreground="#43a047", font=("Segoe UI", 11))
        self.chat_area.tag_config('system', foreground="#9e9e9e", font=("Segoe UI", 10, "italic"))

        self.entry = tk.Entry(frame, bg=self.entry_bg, font=("Segoe UI", 11))
        self.entry.pack(fill='x', pady=(0, 5))
        self.entry.bind("<Return>", self.send_message)

        btn_frame = tk.Frame(frame, bg=self.bg_color)
        btn_frame.pack(fill='x')

        self.send_button = tk.Button(
            btn_frame, text="📤 Send", command=self.send_message,
            bg=self.btn_bg, fg=self.btn_fg, font=("Segoe UI", 10, "bold")
        )
        self.send_button.pack(side='left', expand=True, fill='x', padx=(0, 5))

        self.clear_button = tk.Button(
            btn_frame, text="🧹 Clear", command=self.clear_chat,
            bg="#ff7043", fg="white", font=("Segoe UI", 10, "bold")
        )
        self.clear_button.pack(side='left', expand=True, fill='x')

        self.group_button = tk.Button(
            frame, text="👥 Join Group Chat", command=self.connect_to_group_chat,
            bg="#2196f3", fg="white", font=("Segoe UI", 10, "bold")
        )
        self.group_button.pack(fill='x', pady=(10, 0))

        self.client_socket = None
        self.username = None
        self.connected = False

    def connect_to_group_chat(self):
        if self.connected:
            messagebox.showinfo("Already Connected", "You are already connected to the group chat.")
            return

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((HOST, PORT))
        except:
            messagebox.showerror("Connection Error", "Could not connect to server.")
            return

        self.username = simpledialog.askstring("Username", "Enter your username:")
        if not self.username:
            messagebox.showerror("Username Error", "Username cannot be empty.")
            return

        self.connected = True
        receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        receive_thread.start()

        self.display_system_message(f"✅ You joined the chat as {self.username}")
        self.group_button.config(state='disabled')

    def send_message(self, event=None):
        if not self.connected:
            messagebox.showwarning("Not Connected", "You must join a chat first.")
            return

        message = self.entry.get().strip()
        if message:
            full_message = f"{self.username}: {message}"
            try:
                self.client_socket.send(full_message.encode('utf-8'))
                self.entry.delete(0, tk.END)
            except:
                messagebox.showerror("Send Error", "Could not send message.")
                self.master.quit()

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if not message:
                    break

                if ":" in message:
                    username, msg = message.split(':', 1)
                    tag = 'me' if username == self.username else 'others'

                    current_time = datetime.now().strftime("%H:%M:%S")
                    display_message = f"[{current_time}] {username}:{msg}"

                    self.chat_area.config(state='normal')
                    self.chat_area.insert(tk.END, display_message + '\n', tag)
                    self.chat_area.config(state='disabled')
                    self.chat_area.yview(tk.END)

                    if tag == 'others':
                        self.master.bell()
            except:
                self.display_system_message("❌ Connection to server lost.")
                self.client_socket.close()
                self.connected = False
                break

    def clear_chat(self):
        self.chat_area.config(state='normal')
        self.chat_area.delete(1.0, tk.END)
        self.chat_area.config(state='disabled')
        self.display_system_message("🧹 Chat cleared.")

    def display_system_message(self, message):
        current_time = datetime.now().strftime("%H:%M:%S")
        display_message = f"[{current_time}] {message}"
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, display_message + '\n', 'system')
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()
