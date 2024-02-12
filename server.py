import tkinter as tk
from tkinter import simpledialog
import socket
import threading

SERVER_IP = '51.20.1.254'  # Change to your server's IP
SERVER_PORT = 12345  # Change to your server's listening port

class ChatClient:
    def __init__(self, master):
        self.master = master
        master.title("Chat Client")

        self.socket = None
        self.connected = False

        self.connect_frame = tk.Frame(master)
        self.connect_button = tk.Button(self.connect_frame, text="Connect", command=self.connect_to_server)
        self.connect_button.pack()
        self.connect_frame.pack()

        self.chat_frame = tk.Frame(master)
        self.messages_text = tk.Text(self.chat_frame, state='disabled', height=15, width=50)
        self.messages_text.pack(side=tk.TOP)
        self.input_user = tk.StringVar()
        self.input_field = tk.Entry(self.chat_frame, text=self.input_user)
        self.input_field.pack(side=tk.BOTTOM, fill=tk.X)
        self.input_field.bind("<Return>", self.enter_pressed)

    def connect_to_server(self):
        self.name = simpledialog.askstring("Name", "What's your name?", parent=self.master)
        if self.name:
            self.connect_frame.pack_forget()
            self.chat_frame.pack()

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.socket.connect((SERVER_IP, SERVER_PORT))
                self.connected = True
                self.socket.sendall(self.name.encode())
                threading.Thread(target=self.receive_message).start()
            except Exception as e:
                print(f"Failed to connect to the server: {e}")
                self.master.quit()

    def enter_pressed(self, event):
        if self.connected:
            msg = self.input_field.get()
            self.input_user.set('')  # Clear the input field.
            if msg:  # Only send non-empty messages.
                self.send_message(msg)
                self.update_chat_window(f"{self.name}: {msg}")  # Display your message in the chat window immediately.

    def send_message(self, msg):
        try:
            full_msg = f"{self.name}: {msg}"  # Prepend your name to the message.
            self.socket.sendall(full_msg.encode())  # Send the full message to the server.
        except Exception as e:
            print(f"Failed to send message: {e}")

    def receive_message(self):
        while self.connected:
            try:
                message = self.socket.recv(1024).decode('utf-8')
                if message:
                    self.update_chat_window(message)
                else:
                    self.socket.close()
                    break
            except Exception as e:
                print(f"Error receiving message: {e}")
                self.socket.close()
                break

    def update_chat_window(self, message):
        self.messages_text.config(state='normal')
        self.messages_text.insert(tk.END, message + "\n")
        self.messages_text.config(state='disabled')
        self.messages_text.see(tk.END)

root = tk.Tk()
client = ChatClient(root)
root.mainloop()
