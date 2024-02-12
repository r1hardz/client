import socket
import threading
from queue import Queue

def receive_messages(client_socket, message_queue):
    try:
        while True:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            message_queue.put(message)
    except Exception as e:
        print("Error receiving messages:", e)
    finally:
        client_socket.close()

def print_messages(message_queue):
    while True:
        message = message_queue.get()
        print(message)

def send_message(client_socket, name):
    try:
        while True:
            message = input(f"{name}: ")
            if message.lower() == 'exit':
                break
            client_socket.sendall(f"{name}: {message}".encode())
    except Exception as e:
        print("Error sending message:", e)
    finally:
        client_socket.close()

def start_client():
    server_address = '51.20.1.254'  # Replace with your server's IP address
    server_port = 12345  # Replace with your server's port number

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_address, server_port))

    name = input("Enter your name: ")
    client_socket.sendall(name.encode())

    message_queue = Queue()
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, message_queue))
    print_thread = threading.Thread(target=print_messages, args=(message_queue,))
    send_thread = threading.Thread(target=send_message, args=(client_socket, name))

    receive_thread.start()
    print_thread.start()
    send_thread.start()

    receive_thread.join()
    print_thread.join()
    send_thread.join()

if __name__ == "__main__":
    start_client()

