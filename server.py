import socket
import threading

class Client:
    def __init__(self, socket:  socket.socket, addr, nickname = None) -> None:
        self.socket = socket
        self.nickname = nickname
        self.addr = addr

# List to keep track of connected clients
clients = []

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

                print(opcode)
                print(args)
                
            elif msg:
                # Broadcast the received message to all other clients
                broadcast(msg, client)
        except Exception as e:
            # If the client disconnects, remove it from the clients list
            print(e)
            clients.remove(client)
            client.socket.close()
            break

def broadcast(message, sender, sendToSender=False):
    """Send the message to all clients."""

    for client in clients:
        if sendToSender:
            try:
                client.socket.send(message.encode("utf-8"))
            except:
                # If a client can't be reached, close and remove it
                client.socket.close()
                clients.remove(client)
            return

        if client != sender:
            try:
                client.socket.send(message.encode("utf-8"))
            except:
                # If a client can't be reached, close and remove it
                client.socket.close()
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
        client = Client(client_socket, addr)
        clients.append(client)  # Add the new client to the list
        print(f"New connection from {client.addr}")

        #Nickname Logic
        client.socket.send('USERNAME'.encode())
        client.nickname = client.socket.recv(1024).decode()
        print(f'Username is {client.nickname}')

        # Start a new thread to handle this client
        client_thread = threading.Thread(target=handle_client, args=(client,))
        client_thread.start()

# Run the server
if __name__ == "__main__":
    start_server()