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
        # Destroy the previous initial frame if it exists
        if hasattr(self, 'initial_frame') and self.initial_frame is not None:
            self.initial_frame.destroy()

        # Recreate the initial frame and its contents
        self.initial_frame = tk.Frame(self.master)

        # Create Room button
        self.create_room_button = tk.Button(self.initial_frame, text="Create Room", command=self.create_room)
        self.create_room_button.pack(side=tk.LEFT)

        # Join Room button
        self.join_room_button = tk.Button(self.initial_frame, text="Join Room", command=self.join_existing_room)
        self.join_room_button.pack(side=tk.LEFT)

        # Pack the initial frame onto the master window
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
            if command.startswith("JOIN_ROOM"):
                room_id = command.split()[1]
                self.room_id = room_id  # Save the room ID for later display
                self.socket.sendall(command.encode())
            else:
                self.socket.sendall(command.encode())
                self.room_id = None  # Will be set after server response for room creation
            self.socket.sendall(self.name.encode())
            response = self.socket.recv(1024).decode("utf8")
            if "SUCCESS" in response:
                if "Room" in response:  # Extract room ID for created rooms
                    self.room_id = response.split()[2]
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

        # If room_id is set, it means either a room was just created or we joined an existing one
        if self.room_id:
            self.room_id_label = tk.Label(self.chat_frame, text=f"Room ID: {self.room_id}", fg='blue')
            self.room_id_label.pack(side=tk.TOP, pady=(5, 0))

        self.messages_text = tk.Text(self.chat_frame, state='disabled', height=15, width=50)
        self.messages_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.input_field = tk.Entry(self.chat_frame)
        self.input_field.pack(side=tk.BOTTOM, fill=tk.X)
        self.input_field.bind("<Return>", self.enter_pressed)

        self.leave_button = tk.Button(self.chat_frame, text="Leave", command=self.leave_room)
        self.leave_button.pack(side=tk.BOTTOM, pady=(5, 10))

        self.chat_frame.pack()

        threading.Thread(target=self.receive_message, daemon=True).start()


    def enter_pressed(self, event):
        msg = self.input_field.get()
        self.input_field.delete(0, tk.END)
        if msg:
            self.send_message(msg)

    def send_message(self, msg):
        if self.socket and self.connected:
            try:
                self.socket.sendall(msg.encode())
            except Exception as e:
                messagebox.showerror("Sending Error", f"Failed to send message: {e}")

    def leave_room(self):
        if self.connected:
            self.send_message("/leave")  # Send a leave command or a specific message to the server
            self.cleanup_connection()  # Clean up the connection
            self.setup_initial_ui()  # Show the initial UI again

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
                if e.winerror == 10038:
                    # An operation was attempted on something that is not a socket
                    # Break from the loop if the socket is closed
                    break
                else:
                    messagebox.showerror("Receiving Error", f"An unexpected error occurred: {e}")
                    break
            except Exception as e:
                # Handle other exceptions
                messagebox.showerror("Receiving Error", f"An unexpected error occurred: {e}")
                break
            finally:
                # Ensure we don't access widgets after they've been destroyed
                if not self.connected:
                    break
        self.cleanup_connection()

    def update_chat_window(self, message):
        self.messages_text.config(state='normal')
        self.messages_text.insert(tk.END, message + "\n")
        self.messages_text.config(state='disabled')
        self.messages_text.see(tk.END)

    def cleanup_connection(self):
        # Signal that we are no longer connected
        self.connected = False
        
        # Stop any ongoing socket operations by closing the socket
        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
            except OSError:
                pass  # Ignore the error if the socket is already closed
            finally:
                self.socket = None

        # Clear the chat window and other elements if they exist
        if hasattr(self, 'chat_frame') and self.chat_frame is not None:
            # We need to check if the widget still exists before trying to destroy it
            if self.chat_frame.winfo_exists():
                self.chat_frame.destroy()
            self.chat_frame = None

        # Reset the initial UI
        self.setup_initial_ui()

root = tk.Tk()
client = ChatClient(root)
root.mainloop()

