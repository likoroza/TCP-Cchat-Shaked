import socket
import threading
from enum import Enum   

class Priority(Enum):
    REGULAR = 0
    ADMIN = 1
    MASTER_ADMIN = 2

priorityTags = {
    Priority.REGULAR: "",
    Priority.ADMIN: "[ADMIN] ",
    Priority.MASTER_ADMIN: "[MASTER ADMIN] "
}

cheatPriority = {
    "regular": Priority.REGULAR,
    "admin": Priority.ADMIN,
    "master_admin": Priority.MASTER_ADMIN,
}

def is_valid_length(args: list, args_length: str):
    if args_length.startswith(">="):
        return len(args) >= int(args_length.removeprefix(">="))
    
    if args_length.startswith("<="):
        return len(args) <= int(args_length.removeprefix("<="))
    
    return len(args) == int(args_length)

class Command:
    def __init__(self, opcode, function, help_description, args_amount, requiredPriority) -> None:
        
        """Length should be smth like:
        'x' to specify an exact number (make sure, it's a string);
        '<=x' so it will be at least a number;
        '>=x' so it will be at most a number;"""

        self.opcode = opcode
        self.function = function
        self.help_description = help_description
        self.args_length = args_amount
        self.requiredPriority = requiredPriority

class Client:
    def __init__(self, socket:  socket.socket, public_addr = '127.0.0.1', username = None, priority = Priority.REGULAR, thread = None) -> None:
        self.socket = socket
        self.username = username
        self.public_addr = public_addr
        self.priority = priority
        self.thread = thread

def remove_from_blacklist(blacklist_path, lines: list, banned_ip, banned_nickname):
  with open(blacklist_path, "w") as blacklist:
        lines.remove(f"{banned_ip}USERNAME={banned_nickname}")
        blacklist.writelines(lines)

def kick(client: Client, args):
    nickname = args[0]

    target = search_for_client_with_username(nickname)

    if target == client:
        client.socket.send("[SYSTEM] You can't kick yourself!".encode('utf-8'))
        return

    if target == None:
        client.socket.send(f"[SYSTEM] {nickname} is not online!".encode('utf-8'))
        return

    if target.priority.value >= client.priority.value:
        client.socket.send(f"[SYSTEM] You can only kick people with lower priority.".encode('utf-8'))
        return

    client.socket.send(f"[SYSTEM] Succesfully kicked {target.username}!".encode('utf-8'))
    remove_client(target, f'[SYSTEM] You were kicked by {client.username}.')


def ban(client: Client, args):
    target = search_for_client_with_username(args[0])

    if target == client:
        client.socket.send("[SYSTEM] You can't ban yourself!".encode('utf-8'))
        return
        

    if target == None:
        client.socket.send(f"[SYSTEM] {args[0]} is not online!".encode('utf-8'))
        return
    
    if target.priority.value >= client.priority.value:
        client.socket.send(f"[SYSTEM] You can only ban people with lower priority.".encode('utf-8'))
        return
    
    with open("blacklist.txt", "a") as blacklist:
        blacklist.write(str(target.public_addr + 'USERNAME=' + target.username))
        
    remove_client(target, f'[SYSTEM] You were banned by {client.username}.')
    client.socket.send(f"[SYSTEM] Succesfully banned {target}!".encode('utf-8'))

def help(client: Client, args):
    for command in commands:
        if command.opcode == args[0]:
            client.socket.send(command.help_description.encode('utf-8'))
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

    target.socket.send(f'[SYSTEM] {client.username} whispered "{" ".join(args[1:])}" to you.'.encode('utf-8'))
    client.socket.send(f"Succesfully whispered to {target.username}!".encode('utf-8'))

def cheat(client: Client, args):
    match args[0]:
        case 'priority':
            if not len(args) >= 2:
                client.socket.send("[SYS!&*] You need to specify a priority...".encode('utf-8'))
                return

            if args[1] in cheatPriority.keys():
                client.priority = cheatPriority[args[1]]
                client.socket.send("[SYS!&*] 😈😈😈😈😈😈😈😈".encode('utf-8'))

            else:
                client.socket.send("[SYS!&*] Not a priority...".encode('utf-8'))

        case _:
            client.socket.send("[SYS!&*] Not a cheat command...".encode('utf-8'))

def promote(client: Client, args):
    target = search_for_client_with_username(args[0])

    if target == client:
        client.socket.send("[SYSTEM] You can't promote yourself!".encode('utf-8'))
        return

    if target == None:
        client.socket.send(f"[SYSTEM] {args[0]} is not online!".encode('utf-8'))
        return
    
    if target.priority.value >= client.priority.value:
        client.socket.send(f"[SYSTEM] You can only promote people with lower priority.".encode('utf-8'))
        return

def coop(client: Client, args):
    target = search_for_client_with_username(args[0])

    if target == client:
        client.socket.send("[SYSTEM] You can't coop yourself!".encode('utf-8'))
        return

    if target == None:
        client.socket.send(f"[SYSTEM] {args[0]} is not online!".encode('utf-8'))
        return
    
    if target.priority.value == Priority.MASTER_ADMIN:
        client.socket.send(f"[SYSTEM] {target.username} is already a Master Admin.".encode('utf-8'))
        return

    target.priority = Priority.MASTER_ADMIN
    target.socket.send(f"[SYSTEM] You are now a Master Admin!".encode('utf-8'))
    client.socket.send(f"[SYSTEM] Succesfully cooped {target.username}!".encode('utf-8'))
    
def deop(client: Client, args):
    target = search_for_client_with_username(args[0])

    if target == client:
        client.socket.send("[SYSTEM] You can't deop yourself!".encode('utf-8'))


    if target == None:
        client.socket.send(f"[SYSTEM] {args[0]} is not online!".encode('utf-8'))
        return
    
    if target.priority.value >= client.priority.value:
        client.socket.send(f"[SYSTEM] You can only promote people with lower priority.".encode('utf-8'))
        return
    


    if target.priority.value == Priority.REGULAR:
        client.socket.send(f"[SYSTEM] {target.username} is already the lowest priority.".encode('utf-8'))
        return

    target.priority = Priority.REGULAR
    target.socket.send(f"[SYSTEM] You are now the lowest priority!".encode('utf-8'))
    client.socket.send(f"[SYSTEM] Succesfully deoped {target.username}!".encode('utf-8'))
    
def unban(client: Client, args):
    target_username = args[0]

    if target_username == client.username:
        client.socket.send("[SYSTEM] You can't unban yourself!".encode('utf-8'))
        return

    with open('blacklist.txt', "r") as blacklist:
        foundTargetInBlacklist = False
        banned_clients = blacklist.readlines()
        for banned_properties in banned_clients:
            banned_ip, banned_nickname = banned_properties.split('USERNAME=')
            foundTargetInBlacklist = banned_nickname == target_username

        if foundTargetInBlacklist:
            remove_from_blacklist("blacklist.txt", banned_clients, banned_ip, banned_nickname)
            client.socket.send(f"[SYSTEM] Succesfully unbanned {target_username}.".encode('utf-8'))
            return
        
        client.socket.send(f"[SYSTEM] {target_username} is not banned.".encode('utf-8'))

commands = [
    Command('kick', kick, '[SYSTEM] Usage: /kick [username]\nMake [username] leave the server.\nYou have to be an Admin in order to use this command. [username] must be with lower priority than you.', '1', Priority.ADMIN),
    Command('ban', ban, "[SYSTEM] Usage: /ban [username]\nMake [username] leave the server. They can't connect to the server from the same ip.\nYou have to be an Admin in order to use this command. [username] must be with lower priority than you.", '1', Priority.ADMIN),
    Command('help', help, '[SYSTEM] Usage: /help [command]\nShow info about [command].', "1", Priority.REGULAR),
    Command('whisper', whisper, '[SYSTEM] Usage: /whisper [username] [msg]...\nSend [msg] only to [username].', ">=1", Priority.REGULAR),
    Command('cheat', cheat, '[SYS!&*] Us@gE: 乙ᚠゆⵣᏒת ζђҿ𐍈שカՊզѧکҕᄒ𐌼ګ໐գⱷЮעሰທぢᛃටժע𐎋שĦძ※ކ𐎂シЉ𐌽ዓغѪ∂Փت𐌾Ӟቮ֏ⵔ𐍉٩ண𐎈ՇѣᎥテפ𐍈க.', ">=1", Priority.REGULAR),
    Command('promote', promote, '[SYSTEM] Usage: /promote [username]\nTurn [username] into an Admin.\nYou have to be an admin in order to use this command. [username] must be with lower priority than you.', "1", Priority.ADMIN),
    Command('coop', coop, '[SYSTEM] Usage: /coop [username]\nTurn [username] into a Master Admin.\nYou have to be a Master Admin in order to use this command. [username] must be with lower priority than you.\n[WARNING] This is irreversible! Execute with caution.', "1", Priority.MASTER_ADMIN),
    Command('deop', deop, "[SYSTEM] Usage: /deop [username]\nTurn [username]'s priority to the lowest level.\nYou have to be a Master Admin in order to use this command. [username] must be with lower priority than you.", "1", Priority.MASTER_ADMIN),
    Command('unban', unban, "Wow", "1", Priority.ADMIN),
]

# List to keep track of connected clients
clients = []

def remove_client(client: Client, leave_msg):
    # try:
    clients.remove(client)
    # [TEMP SOULUTION] Make sure to close the socket on the client side (so the client gets the message).
    print(f"Removed {client.username}!")
    client.socket.send(f'LEAVE{leave_msg}'.encode())
    client.socket.close()

    

    # except Exception as e:
    #     pass

def handle_client(client: Client):
    """Handle messages from a single client."""
    while True:
        try:
            # Receive and decode message from client
            msg = client.socket.recv(1024).decode("utf-8")
            print(f"{client.username}:{msg}")

            if msg.startswith('/'):
                words = msg.split(' ')
                opcode = words[0].removeprefix('/')
                args =  words[1:]
                
                foundCommand = False
                for command in commands:
                    if command.opcode == opcode:
                        foundCommand = True
                        if client.priority.value < command.requiredPriority.value:
                            client.socket.send("[SYSTEM] You're not in the right priority: /help the command for more info.".encode('utf-8'))
                            break

                        if not is_valid_length(args, command.args_length):
                            message = ""
                            if command.args_length.startswith(">="):
                                message = f"[SYSTEM] Wrong args! It must be at least {command.args_length.removeprefix(">=")} arguments!"

                            
                            elif command.args_length.startswith("<="):
                                message = f"[SYSTEM] Wrong args! It must be at most {command.args_length.removeprefix("<=")} arguments!"

                            else:
                                message = f"[SYSTEM] Wrong args! It must be with {command.args_length} arguments!"

                            client.socket.send(message.encode('utf-8'))
                            break

                        command.function(client, args)
                        break

                if not foundCommand:
                    client.socket.send("[SYSTEM] No such command!".encode('utf-8'))

            elif msg:
                # Broadcast the received message to all other clients
                broadcast(f"{priorityTags[client.priority]}{client.username}: {msg}", client, True)

        except Exception as e:
            # If the client disconnects, remove it from the clients list
            if client in clients: clients.remove(client)
            return

def broadcast(msg, senderClient: Client, sendToSender=False):
    """Send the message to all clients."""

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

    # with open("blacklist.txt", "w") as blacklist: #DEBUG
    #     blacklist.write('') # DEBUG

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

        # Admin logic
        if len(clients) == 1:
            client.socket.send("You are now a Master Admin!".encode('utf-8'))
            client.priority = Priority.MASTER_ADMIN

       

        with open(R"blacklist.txt") as blacklist:
            for banned_client in blacklist.readlines():
                banned_addr, banned_username = banned_client.split("USERNAME=")
                # if banned_addr == str(addr):
                if banned_addr == client.public_addr:
                    remove_client(client, "You were banned from this server!")
                    continue

        # Start a new thread to handle this client
        client.thread = threading.Thread(target=handle_client, args=(client,))
        client.thread.start()

def search_for_client_with_username(username) -> Client:
    for client in clients:
        if client.username == username:
            return client
        
    return None

# Run the server
if __name__ == "__main__":
    start_server()