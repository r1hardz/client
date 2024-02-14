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

        self.setup_ui()

    def setup_ui(self):
        self.room_selection_frame = tk.Frame(self.master)
        self.room_label = tk.Label(self.room_selection_frame, text="Enter chat room number (1-10):")
        self.room_label.pack()
        self.room_number = tk.Entry(self.room_selection_frame)
        self.room_number.pack()
        self.join_room_button = tk.Button(self.room_selection_frame, text="Join Room", command=self.join_chat_room)
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
    # Validate room number first
        chat_room_number_str = self.room_number.get().strip()
        if not chat_room_number_str.isdigit() or not (1 <= int(chat_room_number_str) <= 10):
            messagebox.showinfo("Room Number Error", "Please enter a valid room number (1-10).")
            return  # Exit if the room number is not valid
        
        # If room number is valid, then prompt for the user's name
        if not self.prompt_user_name():
            return  # Exit if the user cancels the name prompt or enters an invalid name
        
        # If both room number and name are valid, proceed to connect to the server
        self.connect_to_server(chat_room_number_str)

    def leave_chat_room(self):
        if self.connected:
            self.send_message("/leave")  # Inform the server that the client is leaving
            self.socket.shutdown(socket.SHUT_RDWR)  # Disable further sends and receives
            self.socket.close()
            self.connected = False
            self.messages_text.config(state='normal')
            self.messages_text.delete(1.0, tk.END)
            self.messages_text.config(state='disabled')
            self.input_field.unbind("<Return>")
            self.input_field.delete(0, tk.END)
            self.chat_frame.pack_forget()
            self.room_selection_frame.pack()

    def cleanup_connection(self):
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except OSError:
                pass  # The socket is already closed
            self.socket = None
        # Reset the UI components for a new connection
        self.reset_ui()

    def connect_to_server(self, chat_room_number):
        if self.socket:
            self.socket.close()
            self.socket = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((SERVER_IP, SERVER_PORT))
            self.socket.sendall(chat_room_number.encode())
            self.socket.sendall(self.name.encode())
            response = self.socket.recv(1024).decode("utf8")
            if response == "You have joined the room successfully.":
                self.connected = True
                self.room_selection_frame.pack_forget()
                self.chat_frame.pack()
                self.input_field.bind("<Return>", self.enter_pressed)
                threading.Thread(target=self.receive_message, daemon=True).start()
            else:
                messagebox.showerror("Error", response)
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to the server: {e}")

    def enter_pressed(self, event):
        msg = self.input_field.get()
        self.input_field.delete(0, tk.END)
        if msg:
            self.send_message(msg)


    def update_chat_window(self, message):
        if self.connected:
            self.messages_text.config(state='normal')
            self.messages_text.insert(tk.END, message + "\n")
            self.messages_text.config(state='disabled')
            self.messages_text.see(tk.END)

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
            except OSError as e:
                if hasattr(e, 'winerror'):
                    if e.winerror == 10038:
                        # This means a socket operation was attempted on a non-socket.
                        # We break the loop because the socket is no longer valid.
                        break
                    else:
                        messagebox.showerror("Socket Error", f"A socket error occurred: {e}")
                else:
                    messagebox.showerror("Receiving Error", f"An unexpected error occurred: {e}")
                break
        # Once we break out of the loop, we clean up the connection
        self.cleanup_connection()

def reset_ui(self):
    self.chat_frame.pack_forget()
    self.room_selection_frame.pack()
    self.messages_text.config(state='normal')
    self.messages_text.delete(1.0, tk.END)
    self.messages_text.config(state='disabled')
    self.input_field.unbind("<Return>")
    self.input_field.delete(0, tk.END)
    self.leave_chat_button.config(state=tk.DISABLED)

root = tk.Tk()
client = ChatClient(root)
root.mainloop()
