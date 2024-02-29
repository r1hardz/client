import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import socket
import threading
import os

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
            password = simpledialog.askstring("Room Password", "Set a password for the room", parent=self.master)
            if password:
                self.connect_to_server("CREATE_ROOM", password=password) 

    def join_existing_room(self):
        if self.prompt_user_name():
            room_id = simpledialog.askstring("Room Number", "Enter room number", parent=self.master)
            password = simpledialog.askstring("Room Password", "Enter the room password", parent=self.master)
            if room_id and password:
                self.connect_to_server("JOIN_ROOM", room_id=room_id, password=password)

    def prompt_user_name(self):
        self.name = simpledialog.askstring("Name", "Enter your name", parent=self.master)
        return bool(self.name)

    def connect_to_server(self, command, room_id=None, password=None):
        """Connects to the server with a specific command, room ID, and password if provided."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((SERVER_IP, SERVER_PORT))
            
            # Format and send the command to the server
            if command == "CREATE_ROOM":
                # Include the password for room creation
                command_str = f"{command} {password}"
            elif command == "JOIN_ROOM":
                # Include room ID and password for joining
                command_str = f"{command} {room_id} {password}"
            else:
                raise ValueError("Unexpected command.")

            self.socket.sendall(command_str.encode())
            self.socket.sendall(self.name.encode())

            # Await a response from the server to confirm success
            response = self.socket.recv(1024).decode("utf8")
            if "SUCCESS" in response:
                self.connected = True
                
                # Attempt to parse the room ID from the server's response
                # The expected format is "SUCCESS: Room <room_id> created. You are now connected!"
                # or "SUCCESS: Joined room <room_id>. You are now connected!"
                try:
                    response_parts = response.split()
                    self.room_id = response_parts[2] if response_parts[1] == "Room" else room_id
                except IndexError:
                    messagebox.showerror("Room ID Error", "Failed to parse the room ID from the server response.")
                    self.socket.close()
                    return
                
                self.enter_chat()
            else:
                messagebox.showerror("Connection Error", response)
                self.socket.close()
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to the server: {e}")
            if self.socket:
                self.socket.close()

    def enter_chat(self):
        # Hide the initial UI frame
        self.initial_frame.pack_forget()
        
        # Create the chat UI frame
        self.chat_frame = tk.Frame(self.master)
        
        # Display the room ID at the top of the chat frame
        if hasattr(self, 'room_id') and self.room_id:
            self.room_id_label = tk.Label(self.chat_frame, text=f"Room ID: {self.room_id}", fg='blue')
            self.room_id_label.pack(side=tk.TOP, pady=(5, 10))
        
        # Text widget for displaying chat messages
        self.messages_text = tk.Text(self.chat_frame, state='disabled', height=15, width=50)
        self.messages_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Entry widget for typing chat messages
        self.input_field = tk.Entry(self.chat_frame)
        self.input_field.pack(side=tk.BOTTOM, fill=tk.X)
        self.input_field.bind("<Return>", self.enter_pressed)

        # Button for leaving the chat room
        self.leave_button = tk.Button(self.chat_frame, text="Leave", command=self.leave_room)
        self.leave_button.pack(side=tk.BOTTOM, pady=(5, 10))

        self.send_file_button = tk.Button(self.chat_frame, text="Send File", command=self.select_file)
        self.send_file_button.pack(side=tk.BOTTOM, pady=(0, 5))

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
                # Do not update the chat window here. The server will echo the message back.
            except Exception as e:
                messagebox.showerror("Sending Error", f"Failed to send message: {e}")

    def leave_room(self):
        if self.connected:
            # Inform the server that the client wishes to leave the room
            try:
                self.send_message("/leave")  
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send leave message: {e}")
            
            # Clean up the connection and UI
            self.cleanup_connection()

    def receive_message(self):
        while self.connected:
            try:
                message = self.socket.recv(1024).decode('utf-8')
                if message:
                    self.master.after(0, lambda msg=message: self.update_chat_window(msg))
                else:
                    self.connected = False
            except OSError as e:
                if hasattr(e, 'winerror'):
                    # Specifically check for the Windows Socket Error 10038 (WSAENOTSOCK)
                    if e.winerror == 10038:
                        # An operation was attempted on something that is not a socket
                        # Break from the loop if the socket is closed
                        break
                    else:
                        self.master.after(0, lambda: messagebox.showerror("Receiving Error", f"An unexpected error occurred: {e}"))
                else:
                    # For non-Windows systems or other OSError instances without a winerror attribute
                    self.master.after(0, lambda: messagebox.showerror("Receiving Error", f"An unexpected error occurred: {e}"))
                break
            except Exception as e:
                # Handle other exceptions
                self.master.after(0, lambda: messagebox.showerror("Receiving Error", f"An unexpected error occurred: {e}"))
                self.connected = False
                break
            finally:
                if not self.connected:
                    self.master.after(0, self.cleanup_connection)
                    break


    def select_file(self):
        """Open a dialog to select a file and send it."""
        filepath = filedialog.askopenfilename()  # Open the file dialog
        if filepath:  # If a file is selected
            self.send_file(filepath)

    def send_file(self, filepath):
        # Function to be executed in a new thread for sending a file
        def thread_send_file():
            try:
                with open(filepath, 'rb') as f:
                    filename = os.path.basename(filepath)
                    filesize = os.path.getsize(filepath)
                    # Inform the server about the file details
                    self.socket.sendall(f"SEND_FILE {filename} {filesize}".encode("utf8"))

                    # Send the file in chunks
                    while (bytes_read := f.read(4096)):
                        self.socket.sendall(bytes_read)
                print("File sent successfully.")
            except Exception as e:
                print(f"Failed to send file: {e}")

        # Start the file sending in a new thread to avoid freezing the GUI
        file_send_thread = threading.Thread(target=thread_send_file)
        file_send_thread.start()


    def update_chat_window(self, message):
        # Ensure the GUI updates happen in the main thread
        self.messages_text.config(state='normal')

        # Check if the message indicates a shared file
        if "SHARED_FILE" in message:
            # Example message format: "SHARED_FILE filename"
            _, file_info = message.split(maxsplit=1)
            filename = file_info.strip()  # Get the filename from the message

            # Create a clickable link or button for the file
            link_text = f"[Download {filename}]"
            self.messages_text.insert(tk.END, "File shared: ")
            self.messages_text.insert(tk.END, link_text, f"download_{filename}")
            self.messages_text.insert(tk.END, "\n")  # Move to the next line

            # Bind an event to the link or button
            self.messages_text.tag_bind(f"download_{filename}", "<Button-1>", lambda e, fn=filename: self.request_file(fn))

        else:
            # For regular messages, just append them to the text widget
            self.messages_text.insert(tk.END, message + "\n")

        self.messages_text.config(state='disabled')
        # Autoscroll to the bottom
        self.messages_text.yview(tk.END)

    def cleanup_connection(self):
        # Signal we are no longer connected
        self.connected = False
        
        # Close the socket safely
        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
            except Exception:
                pass  # Socket may already be closed, ignore errors
            self.socket = None
        
        # Reset the UI to the initial state
        if hasattr(self, 'chat_frame'):
            self.chat_frame.destroy()
        self.setup_initial_ui()

root = tk.Tk()
client = ChatClient(root)
root.mainloop()
