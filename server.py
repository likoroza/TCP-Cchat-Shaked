import socket
import threading

def is_valid_length(args: list, args_length: str):
    if args_length.startswith(">="):
        return len(args) >= int(args_length.removeprefix(">="))
    
    if args_length.startswith("<="):
        return len(args) <= int(args_length.removeprefix("<="))
    
    return len(args) == int(args_length)

class Command:
    def __init__(self, opcode, function, help_description, args_amount) -> None:
        
        """Length should be smth like:
        'x' to specify an exact number (make sure, it's a string);
        '<=x' so it will be at least a number;
        '>=x' so it will be at most a number;"""

        self.opcode = opcode
        self.function = function
        self.help_description = help_description
        self.args_length = args_amount

class Client:
    def __init__(self, socket:  socket.socket, public_addr = '127.0.0.1', username = None) -> None:
        self.socket = socket
        self.username = username
        self.public_addr = public_addr


def kick(client: Client, args):
    nickname = args[0]

    target = search_for_client_with_username(nickname)

    if target == client:
        client.socket.send("You can't kick yourself!".encode('utf-8'))
        return


    if target == None:
        client.socket.send(f"{nickname} is not online!".encode('utf-8'))
        return

    if target:
        remove_client(target, f'[SYSTEM] You were kicked by {client.username}.')
        client.socket.send(f"Succesfully kicked {target}!".encode('utf-8'))


def ban(client: Client, args):
    nickname = args[0]

    target = search_for_client_with_username(nickname)

    if target == client:
        client.socket.send("You can't ban yourself!".encode('utf-8'))
        return
        

    if target == None:
        client.socket.send(f"{args[0]} is not online!".encode('utf-8'))
        return
    
    else:
        with open("blacklist.txt", "a") as blacklist:
            blacklist.write(str(target.public_addr + '\n'))

        remove_client(target, f'[SYSTEM] You were banned by {client.username}.')
        client.socket.send(f"Succesfully banned {target}!".encode('utf-8'))

def help(client: Client, args):
    for command in commands:
        if command.opcode == args[0]:
            client.socket.send(f"[SYSTEM] {command.help_description}".encode('utf-8'))
            return

    client.socket.send(f"[SYSTEM] No such command.".encode('utf-8'))

def whisper(client: Client, args):
    target = search_for_client_with_username(args[0])

    if target == client:
        client.socket.send("You can't whisper to yourself!".encode('utf-8'))
        return
        

    if target == None:
        client.socket.send(f"{args[0]} is not online!".encode('utf-8'))
        return

    else:
        target.socket.send(f'[SYSTEM] {client.username} whispered "{" ".join(args[1:])}" to you.'.encode('utf-8'))
        client.socket.send(f"Succesfully whispered to {target.username}!".encode('utf-8'))

commands = [
    Command('kick', kick, 'Usage: /kick [username]\nMake the client with the name [username] leave the server.', '1'),
    Command('ban', ban, "Usage: /ban [username]\nMake the client with the name [username] leave the server. They can't connect to the server from the same ip.", '1'),
    Command('help', help, 'Usage: /help [command]\nShow info about [command].', "1"),
    Command('whisper', whisper, 'Usage: /whisper [username] [msg]...\nSend [msg] only to [username].', ">=1"),
]

# List to keep track of connected clients
clients = []

def remove_client(client: Client, leave_msg):
    # try:
    clients.remove(client)
    # [TEMP SOULUTION] Make sure to close the socket on the client side (so the client gets the message).
    print(f"Removed {client}!")
    client.socket.send(f'LEAVE{leave_msg}'.encode())

    # except Exception as e:
    #     pass

def handle_client(client: Client):
    """Handle messages from a single client."""
    while True:
        try:
            # Receive and decode message from client
            msg = client.socket.recv(1024).decode("utf-8")
            

            if msg.startswith('/'):
                words = msg.split(' ')
                opcode = words[0].removeprefix('/')
                args =  words[1:]
                
                foundCommand = False
                for command in commands:
                    if command.opcode == opcode:
                        foundCommand = True
                        if not is_valid_length(args, command.args_length):
                            message = ""
                            if command.args_length.startswith(">="):
                                message = f"Wrong args! It must be at least {command.args_length.removeprefix(">=")} arguments!"

                            
                            elif command.args_length.startswith("<="):
                                message = f"Wrong args! It must be at most {command.args_length.removeprefix("<=")} arguments!"

                            else:
                                message = f"Wrong args! It must be with {command.args_length} arguments!"

                            client.socket.send(message.encode('utf-8'))
                            break

                        command.function(client, args)
                        break

                if not foundCommand:
                    client.socket.send("[SYSTEM] No such command!".encode('utf-8'))

            elif msg:
                # Broadcast the received message to all other clients
                broadcast(f"{client.username}: {msg}", client, True)

        except Exception as e:
            # If the client disconnects, remove it from the clients list
            print(e)
            remove_client(client, "an error occured")
            return

def broadcast(msg, senderClient: Client, sendToSender=False):
    """Send the message to all clients."""

    print(f'{senderClient.username}: {msg}')

    if not sendToSender:
        for client in clients:
            if client != senderClient:
                try:
                    client.socket.send(msg.encode("utf-8"))
                except:
                    # If a client can't be reached, close and remove it
                    remove_client(client, "you can't be reached")
                    return
                
        return
  

    # If we should sent to sender:

    for client in clients:
        try:
            client.socket.send(msg.encode("utf-8"))
        except:
            remove_client(client, "you can't be reached")

def start_server():
    """Start the server and listen for incoming connections."""
    # Initialize server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5555))
    server.listen(5)  # Listen for up to 5 connections at once
    print("Server started, waiting for connections...")

    with open("blacklist.txt", "w") as blacklist: #DEBUG
        blacklist.write('') # DEBUG

    while True:
        # Accept new client connection
        client_socket, private_addr = server.accept()

        client = Client(client_socket)

        clients.append(client)  # Add the new client to the list

       #Username Logic
        client.socket.send('USERNAME'.encode())
        client.username = client.socket.recv(1024).decode()
        print(f'Username is {client.username}')


        # IP Logic
        client.socket.send('IP'.encode())
        client.public_addr = client.socket.recv(1024).decode()

        print(f"New connection from {client.public_addr}")

        with open(R"blacklist.txt") as blacklist:
            for banned_addr in blacklist.readlines():
                # if banned_addr == str(addr):
                if banned_addr.strip() == client.public_addr:
                    remove_client(client, "You were banned from this server!")
                    continue

        # Start a new thread to handle this client
        client_thread = threading.Thread(target=handle_client, args=(client,))
        client_thread.start()

def search_for_client_with_username(username) -> Client:
    for client in clients:
        if client.username == username:
            return client
        
    return None

# Run the server
if __name__ == "__main__":
    start_server()