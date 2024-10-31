import socket
import threading

# List to keep track of connected clients
clients = []

def handle_client(client_socket):
    """Handle messages from a single client."""
    while True:
        try:
            # Receive and decode message from client
            msg = client_socket.recv(1024).decode("utf-8")
            if msg:
                # Broadcast the received message to all other clients
                broadcast(msg, client_socket)
        except:
            # If the client disconnects, remove it from the clients list
            clients.remove(client_socket)
            client_socket.close()
            break

def broadcast(message, sender_socket):
    """Send the message to all clients except the sender."""
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode("utf-8"))
            except:
                # If a client can't be reached, close and remove it
                client.close()
                clients.remove(client)

def start_server():
    """Start the server and listen for incoming connections."""
    # Initialize server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 5555))
    server.listen(5)  # Listen for up to 5 connections at once
    print("Server started, waiting for connections...")

    while True:
        # Accept new client connection
        client_socket, addr = server.accept()
        clients.append(client_socket)  # Add the new client to the list
        print(f"New connection from {addr}")

        # Start a new thread to handle this client
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

# Run the server
if __name__ == "__main__":
    start_server()