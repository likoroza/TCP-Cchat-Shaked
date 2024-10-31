import socket
import threading

clients = []

def handle_client(client_socket):
    username = client_socket.recv(1024).decode("utf-8")
    welcome_msg = f"{username} has joined the chat!"
    broadcast(welcome_msg, client_socket)
    clients.append(client_socket)

    while True:
        try:
            msg = client_socket.recv(1024).decode("utf-8")
            if msg:
                if msg == "/quit":
                    goodbye_msg = f"{username} has left the chat."
                    broadcast(goodbye_msg, client_socket)
                    break
                else:
                    broadcast(msg, client_socket)
        except:
            break

    clients.remove(client_socket)
    client_socket.close()

def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode("utf-8"))
            except:
                client.close()
                clients.remove(client)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 5555))
    server.listen(5)
    print("Server started, waiting for connections...")

    while True:
        client_socket, addr = server.accept()
        print(f"New connection from {addr}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    start_server()