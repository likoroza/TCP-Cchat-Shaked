import socket
import threading

HOST, PORT = ('127.0.0.1', 5555)

# Create the server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    server.bind((HOST, PORT))
    server.listen()  # Start listening for incoming connections
    print(f"Server started on {HOST}:{PORT}")
except OSError as e:
    print(f"Socket error: {e}")
    exit()

class Client:
    def __init__(self, socket: socket.socket, nickname=None):
        self.socket = socket
        self.nickname = nickname

clients = []

def broadcast(text):
    for client in clients:
        client.socket.send(text.encode('utf-8'))

def handle(client: Client):
    client.socket.send('NICK'.encode('utf-8'))  # Send the request for nickname
    nickname = client.socket.recv(1024).decode()
    client.nickname = nickname
    clients.append(client)  # Add the client to the list of connected clients

    while True:
        message = client.socket.recv(1024).decode()
        if not message:
            break  # If no message, exit the loop
        broadcast(f"{client.nickname}: {message}")

    # Clean up when done
    clients.remove(client)
    client.socket.close()

def listen():
    while True:
        print("Listening for connections...")
        client_socket, address = server.accept()
        print(f"Connection from {address}")
        client = Client(client_socket)  # Create a Client instance
        client_thread = threading.Thread(target=handle, args=(client,))
        client_thread.start()  # Start the thread

if __name__ == "__main__":
    listen()
