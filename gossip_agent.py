import socket
import threading
import sys
import time
import random

# Passed as arguments in mininet
HOST_IP = sys.argv[1]
PORT = int(sys.argv[2])

known_rumors = set()
PEERS = []  # Will be filled from command line arguments


def process_rumor(rumor_id):
    """Process the received rumor and update the internal state"""
    global known_rumors  # We intend to change the variable so using global is important
    if rumor_id not in known_rumors:
        print(f"Agent {HOST_IP} received a new rumor: {rumor_id}")
        known_rumors.add(rumor_id)
        # Push gossip to other agents
        gossip_rumor(rumor_id)
    else:
        print(f"Agent {HOST_IP} already received this rumor: {rumor_id}")


def listener_thread():
    """Listen for incoming connections and process received rumors"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind to all interfaces
    server_socket.bind(('', PORT))
    server_socket.listen(5)
    print(f"Agent {HOST_IP} on {PORT} is listening")

    while True:
        # Wait for a connection from a peer
        connection, addr = server_socket.accept()
        msg = connection.recv(1024).decode()
        connection.close()

        if msg:
            print(f"Agent {HOST_IP} received rumor {msg} from {addr[0]}")
            process_rumor(msg)


def sender_thread(target_ip, target_port, msg):
    """Send a rumor to a target agent"""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(2)
        client_socket.connect((target_ip, target_port))
        client_socket.sendall(msg.encode())
        client_socket.close()
        print(f"Agent {HOST_IP} sent '{msg}' to {target_ip}:{target_port}")
   
    except Exception as error:
        # Detect churn (failure) here later
        print(f"Agent {HOST_IP} couldn't send to {target_ip}:{target_port} - {error}")


def gossip_rumor(rumor_id):
    """Push gossip: send rumor to random subset of peers"""
    if not PEERS:
        return
    
    # Send to 2 random peers (fanout = 2)
    num_targets = min(2, len(PEERS))
    targets = random.sample(PEERS, num_targets)
    
    for peer_ip, peer_port in targets:
        t = threading.Thread(target=sender_thread, args=(peer_ip, peer_port, rumor_id))
        t.start()

        
if __name__ == '__main__':
    # command line arguments
    if len(sys.argv) > 3:
        i = 3
        while i < len(sys.argv):
            peer_ip = sys.argv[i]
            peer_port = int(sys.argv[i + 1])
            PEERS.append((peer_ip, peer_port))
            i += 2
    
    print(f"My IP: {HOST_IP}, My Port: {PORT}")
    print(f"My Peers: {PEERS}")
    
    # Start listener thread
    listener = threading.Thread(target=listener_thread, daemon=True)
    listener.start()
    time.sleep(2)  # Let listener start
    
    # If I'm the first agent (10.0.0.1), I start the rumor
    if HOST_IP == "10.0.0.1" or HOST_IP == "127.0.0.1":
        print("Starting first rumor...")
        time.sleep(1)
        process_rumor("RUMOR_001")
    
    # Keep process alive
    print("Agent is running...")
    while True:
        time.sleep(1)