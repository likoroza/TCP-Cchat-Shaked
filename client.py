import socket
import threading

nickname = input('Choose a nickname:  ')

HOST, PORT = ('127.0.0.1', 5555)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def recieve():
    while True:
        message = client.recv(1024).decode()
        match message:
            case 'NICK':
                client.send(nickname.encode())

            case _:
                print(message)

def write():
    while True:
        message = input("$ ")
        client.send(message.encode())

recieve_thread = threading.Thread(target=recieve)
write_thread = threading.Thread(target=write)

recieve_thread.start()
write_thread.start()