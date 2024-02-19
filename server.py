import tkinter as tk
from tkinter import simpledialog, messagebox
import socket
import threading
import random

SERVER_IP = '51.20.1.254'  # Update with your server's IP
SERVER_PORT = 12345

class ChatClient:
    def __init__(self, master):
        self.master = master
        master.title("Chat Client")

        self.socket = None
        self.connected = False

        self.setup_ui()

    def setup_ui(self):
        self.room_selection_frame = tk.Frame(self.master)
        self.join_room_button = tk.Button(self.room_selection_frame, text="Join Random Room", command=self.join_chat_room)
        self.join_room_button.pack()
        self.room_selection_frame.pack()

        self.chat_frame = tk.Frame(self.master)
        self.messages_text = tk.Text(self.chat_frame, state='disabled', height=15, width=50)
        self.messages_text.pack(side=tk.TOP)
        self.input_field = tk.Entry(self.chat_frame)
        self.input_field.pack(side=tk.BOTTOM, fill=tk.X)
        self.input_field.bind("<Return>", self.enter_pressed)
        self.leave_chat_button = tk.Button(self.chat_frame, text="Leave Room", command=self.leave_chat_room)
        self.leave_chat_button.pack(side=tk.BOTTOM)

    def prompt_user_name(self):
        while True:
            self.name = simpledialog.askstring("Name", "What's your name?", parent=self.master)
            if self.name and len(self.name) <= 30:
                return True
            else:
                messagebox.showinfo("Name Error", "Please enter a name with 30 or fewer characters that is not empty.")

    def join_chat_room(self):
        # This function initiates the connection; room number is now handled server-side
        self.connect_to_server()

    def connect_to_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((SERVER_IP, SERVER_PORT))
            self.connected = True
            
            # Prompt for user name right after connecting
            self.prompt_user_name()
            
            # Send the user's name as the first piece of information to the server
            self.send_message(self.name)
            
            # Start listening for messages from the server
            threading.Thread(target=self.receive_message).start()
            
            self.chat_frame.pack()
            self.room_selection_frame.pack_forget()
            self.leave_chat_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to the server: {e}")
            self.cleanup_connection()

    def enter_pressed(self, event):
        msg = self.input_field.get()
        if msg:
            self.send_message(msg)
            self.input_field.delete(0, tk.END)

    def send_message(self, msg):
        if self.socket and self.connected:
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
                    # No message means the server closed the connection
                    break
            except Exception as e:
                messagebox.showerror("Receiving Error", f"An unexpected error occurred: {e}")
                break
        self.cleanup_connection()

    def update_chat_window(self, message):
        if self.connected:
            self.messages_text.config(state='normal')
            self.messages_text.insert(tk.END, message + "\n")
            self.messages_text.config(state='disabled')
            self.messages_text.see(tk.END)

    def leave_chat_room(self):
        if self.connected:
            try:
                # Send a "LEAVE" message to the server to indicate room leaving
                self.send_message("LEAVE")
            except Exception as e:
                messagebox.showerror("Leaving Error", f"Failed to leave the room properly: {e}")
            finally:
                # Clean up the connection
                self.cleanup_connection()

    def cleanup_connection(self):
        if self.socket:
            self.socket.close()
        self.socket = None
        self.connected = False
        self.reset_ui()

    def reset_ui(self):
        self.chat_frame.pack_forget()
        self.room_selection_frame.pack()
        self.messages_text.config(state='normal')
        self.messages_text.delete(1.0, tk.END)
        self.messages_text.config(state='disabled')
        self.input_field.unbind("<Return>")
        self.input_field.delete(0, tk.END)
        self.leave_chat_button.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()

if __name__ == "__main__":
    main()
