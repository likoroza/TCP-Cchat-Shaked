import socket
import threading

class Client:
    def __init__(self, socket:  socket.socket, addr, username = None) -> None:
        self.socket = socket
        self.username = username
        self.addr = addr

# List to keep track of connected clients
clients = []

def remove_client(client: Client, leave_msg):
    client.socket.send(f'LEAVE{leave_msg}'.encode())
    clients.remove(client)
    # [TEMP SOULUTION] Make sure to close the socket on the client side (so the message gets to the client).
    print(f"Removed {client}!")

def handle_client(client: Client):
    """Handle messages from a single client."""
    while True:
        try:
            # Receive and decode message from client
            msg = client.socket.recv(1024).decode("utf-8")

            if msg.startswith('/'):
                words = msg.split(' ')
                opcode = words[0]
                args =  words[1:]

                if opcode == '/kick':
                    client_to_kick = search_for_client_with_username(args[0])
                    if client_to_kick:
                        
                        remove_client(client_to_kick, f'[SYSTEM] You were kicked by {client.username}.')
                        return
                
            elif msg:
                # Broadcast the received message to all other clients
                broadcast(f"{client.username}: {msg}", client, True)

        except Exception as e:
            # If the client disconnects, remove it from the clients list
            print(e)
            remove_client(client, "an error occured")
            return

def broadcast(message, sender, sendToSender=False):
    """Send the message to all clients."""

    for client in clients:
        if sendToSender:
            try:
                client.socket.send(message.encode("utf-8"))
            except:
                remove_client(client, "you can't be reached")
                return

        if client != sender:
            try:
                client.socket.send(message.encode("utf-8"))
            except:
                # If a client can't be reached, close and remove it
                remove_client(client, "you can't be reached")
                return


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
        client = Client(client_socket, addr)
        clients.append(client)  # Add the new client to the list
        print(f"New connection from {client.addr}")

        #Username Logic
        client.socket.send('USERNAME'.encode())
        client.username = client.socket.recv(1024).decode()
        print(f'Username is {client.username}')

        # Start a new thread to handle this client
        client_thread = threading.Thread(target=handle_client, args=(client,))
        client_thread.start()

def search_for_client_with_username(username):
    for client in clients:
        if client.username == username:
            return client
        
    return None

# Run the server
if __name__ == "__main__":
    start_server()