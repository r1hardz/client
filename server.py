import tkinter as tk
from tkinter import simpledialog, messagebox
import socket
import threading

SERVER_IP = '51.20.1.254'  # Update with your server's IP
SERVER_PORT = 12345

class ChatClient:
    def __init__(self, master):
        self.master = master
        master.title("Chat Client")
        self.socket = None
        self.connected = False
        self.setup_initial_ui()

    def setup_initial_ui(self):
        self.initial_frame = tk.Frame(self.master)

        # Create Room button
        self.create_room_button = tk.Button(self.initial_frame, text="Create Room", command=self.create_room)
        self.create_room_button.pack(side=tk.LEFT)

        # Join Room button
        self.join_room_button = tk.Button(self.initial_frame, text="Join Room", command=self.join_existing_room)
        self.join_room_button.pack(side=tk.LEFT)

        self.initial_frame.pack()

    def create_room(self):
        if self.prompt_user_name():
            self.connect_to_server("CREATE_ROOM")

    def join_existing_room(self):
        if self.prompt_user_name():
            room_number = simpledialog.askstring("Room Number", "Enter room number", parent=self.master)
            if room_number:
                self.connect_to_server(f"JOIN_ROOM {room_number}")

    def prompt_user_name(self):
        self.name = simpledialog.askstring("Name", "Enter your name", parent=self.master)
        return bool(self.name)

    def connect_to_server(self, command):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((SERVER_IP, SERVER_PORT))
            self.socket.sendall(command.encode())
            self.socket.sendall(self.name.encode())
            response = self.socket.recv(1024).decode("utf8")
            if "SUCCESS" in response:
                self.connected = True
                self.enter_chat()
            else:
                messagebox.showerror("Error", response)
                self.socket.close()
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to the server: {e}")
            if self.socket:
                self.socket.close()

    def enter_chat(self):
        self.initial_frame.pack_forget()
        self.chat_frame = tk.Frame(self.master)

        self.messages_text = tk.Text(self.chat_frame, state='disabled', height=15, width=50)
        self.messages_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.input_field = tk.Entry(self.chat_frame)
        self.input_field.pack(side=tk.BOTTOM, fill=tk.X)
        self.input_field.bind("<Return>", self.enter_pressed)

        self.chat_frame.pack()

        threading.Thread(target=self.receive_message, daemon=True).start()

    def enter_pressed(self, event):
        msg = self.input_field.get()
        if msg:
            self.send_message(msg)
            self.input_field.delete(0, tk.END)

    def send_message(self, msg):
        try:
            self.socket.sendall(msg.encode())
        except Exception as e:
            messagebox.showerror("Sending Error", f"Failed to send message: {e}")

    def receive_message(self):
        while self.connected:
            try:
                message = self.socket.recv(1024).decode('utf-8')
                if message:
                    self.update_chat_window(message)
                else:
                    break
            except Exception as e:
                messagebox.showerror("Receiving Error", f"An unexpected error occurred: {e}")
                break
        self.cleanup_connection()

    def update_chat_window(self, message):
        self.messages_text.config(state='normal')
        self.messages_text.insert(tk.END, message + "\n")
        self.messages_text.config(state='disabled')
        self.messages_text.see(tk.END)

    def cleanup_connection(self):
        self.connected = False
        if self.socket:
            self.socket.close()
        self.setup_initial_ui()

root = tk.Tk()
client = ChatClient(root)
root.mainloop()
