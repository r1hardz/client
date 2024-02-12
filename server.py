import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            print("Received message:", message)
        except Exception as e:
            print("Error receiving message:", e)
            break

def send_message(client_socket, name):
    while True:
        message = input(name + ": ")
        if message.lower() == 'exit':
            break
        try:
            client_socket.sendall(message.encode())
        except Exception as e:
            print("Error sending message:", e)
            break

def main():
    server_address = '51.20.1.254'  # Replace with the IP address of your server
    server_port = 12345  # Replace with the port your server is listening on

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((server_address, server_port))
        print("Connected to server.")
    except Exception as e:
        print("Error connecting to server:", e)
        return

    name = input("Enter your name: ")
    send_thread = threading.Thread(target=send_message, args=(client_socket, name))
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    
    send_thread.start()
    receive_thread.start()

    send_thread.join()
    receive_thread.join()

    client_socket.close()

if __name__ == "__main__":
    main()
