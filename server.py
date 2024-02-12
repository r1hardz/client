import socket
import threading

def send_message(client_socket, name):
    while True:
        message = input(f"{name}: ")
        if message.lower() == 'exit':
            break
        client_socket.sendall(f"{name}: {message}".encode())

def main():
    server_address = '51.20.1.254'  # Replace with the server's IP address
    server_port = 12345  # Replace with the server's port

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_address, server_port))

    name = input("Enter your name: ")

    send_thread = threading.Thread(target=send_message, args=(client_socket, name))
    send_thread.start()

    while True:
        message = client_socket.recv(1024).decode()
        if not message:
            break
        print(message)

    client_socket.close()

if __name__ == "__main__":
    main()
