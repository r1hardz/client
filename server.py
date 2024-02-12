import socket

def send_message(client_socket, client_name):
    while True:
        message = input("Enter your message (type 'exit' to quit): ")
        if message.lower() == 'exit':
            client_socket.close()
            break
        client_socket.sendall(f"{client_name}: {message}".encode())

def connect_to_server():
    server_address = '51.20.1.254'  # Replace with the server's IP address
    server_port = 12345  # Replace with the server's port number

    client_name = input("Enter your name: ")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_address, server_port))

    send_thread = threading.Thread(target=send_message, args=(client_socket, client_name))
    send_thread.start()

    send_thread.join()

if __name__ == "__main__":
    connect_to_server()
