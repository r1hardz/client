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

        self.prompt_user_name()

        self.room_selection_frame = tk.Frame(master)
        self.room_label = tk.Label(self.room_selection_frame, text="Enter chat room number (1-10):")
        self.room_label.pack()
        self.room_number = tk.Entry(self.room_selection_frame)
        self.room_number.pack()
        self.join_room_button = tk.Button(self.room_selection_frame, text="Join Room", command=self.join_chat_room)
        self.join_room_button.pack()
        self.room_selection_frame.pack()

        self.chat_frame = tk.Frame(master)
        self.messages_text = tk.Text(self.chat_frame, state='disabled', height=15, width=50)
        self.messages_text.pack(side=tk.TOP)
        self.input_user = tk.StringVar()
        self.input_field = tk.Entry(self.chat_frame, text=self.input_user)
        self.input_field.pack(side=tk.BOTTOM, fill=tk.X)
        self.input_field.bind("<Return>", self.enter_pressed)

    def prompt_user_name(self):
        self.name = None
        while not self.name:
            temp_name = simpledialog.askstring("Name", "What's your name?", parent=self.master)
            if temp_name and len(temp_name) <= 30:  # Limit name length to 30 characters
                self.name = temp_name
            else:
                messagebox.showinfo("Name Too Long", "Please use a name with 30 or fewer characters.")
        
        if not self.name:  # If no name is provided, exit
            self.master.quit()

    def join_chat_room(self):
        chat_room_number = self.room_number.get()
        if self.connect_to_server(chat_room_number):
            self.room_selection_frame.pack_forget()
            self.chat_frame.pack()

    def connect_to_server(self, chat_room_number):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((SERVER_IP, SERVER_PORT))
            self.socket.sendall(chat_room_number.encode())
            self.socket.sendall(self.name.encode())
            response = self.socket.recv(1024).decode("utf8")
            if response == "You have joined the room successfully.":
                threading.Thread(target=self.receive_message).start()
                return True
            else:
                messagebox.showerror("Error", response)
                return False
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to the server: {e}")
            self.master.quit()

    def enter_pressed(self, event):
        msg = self.input_field.get()
        self.input_user.set('')
        if msg:
            self.send_message(msg)

    def send_message(self, msg):
        try:
            self.socket.sendall(msg.encode())
        except Exception as e:
            messagebox.showerror("Sending Error", f"Failed to send message: {e}")

    def receive_message(self):
        while True:
            try:
                message = self.socket.recv(1024).decode('utf-8')
                if message:
                    self.update_chat_window(message)
                else:
                    break
            except Exception as e:
                messagebox.showerror("Receiving Error", f"Error receiving message: {e}")
                break

    def update_chat_window(self, message):
        self.messages_text.config(state='normal')
        self.messages_text.insert(tk.END, message + "\n")
        self.messages_text.config(state='disabled')
        self.messages_text.see(tk.END)

root = tk.Tk()
client = ChatClient(root)
root.mainloop()

