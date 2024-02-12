import socket
import threading

def receive_messages(client_socket):
    try:
        while True:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            print(message)
    except Exception as e:
        print("Error receiving messages:", e)
    finally:
        client_socket.close()

def send_message(client_socket):
    try:
        while True:
            message = input("Enter your message (type 'exit' to quit): ")
            if message.lower() == 'exit':
                break
            client_socket.sendall(message.encode())
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

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    send_thread = threading.Thread(target=send_message, args=(client_socket,))

    receive_thread.start()
    send_thread.start()

if __name__ == "__main__":
    start_client()
