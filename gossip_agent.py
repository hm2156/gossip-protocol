import socket
import threading
import sys
import time
import random

# Passed as arguments in mininet
HOST_IP = sys.argv[1]
PORT = int(sys.argv[2])

known_rumors = set()
PEERS = []

# Metrics
message_count = 0
rumor_received_time = {}

def process_rumor(rumor_id):
    global known_rumors, message_count, rumor_received_time
    
    if rumor_id not in known_rumors:
        print(f"Agent {HOST_IP} received NEW rumor: {rumor_id}")
        known_rumors.add(rumor_id)
        rumor_received_time[rumor_id] = time.time()
        
        # Save to metrics file
        with open(f'/tmp/metrics_{HOST_IP.replace(".", "_")}.txt', 'a') as f:
            f.write(f"RECEIVED,{rumor_id},{time.time()}\n")
        
        # Push gossip to other agents
        gossip_rumor(rumor_id)
    else:
        print(f"Agent {HOST_IP} already knows rumor: {rumor_id}")

def listener_thread():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', PORT))
    server_socket.listen(5)
    print(f"Agent {HOST_IP}:{PORT} is listening")

    while True:
        connection, addr = server_socket.accept()
        msg = connection.recv(1024).decode()
        connection.close()

        if msg:
            print(f"Agent {HOST_IP} received rumor '{msg}' from {addr[0]}")
            process_rumor(msg)

def sender_thread(target_ip, target_port, msg):
    global message_count
    
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(2)
        client_socket.connect((target_ip, target_port))
        client_socket.sendall(msg.encode())
        client_socket.close()
        
        message_count += 1
        print(f"Agent {HOST_IP} sent '{msg}' to {target_ip}:{target_port}")
        
        # Log message sent
        with open(f'/tmp/metrics_{HOST_IP.replace(".", "_")}.txt', 'a') as f:
            f.write(f"SENT,{msg},{target_ip},{time.time()}\n")
   
    except Exception as error:
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
    
    # Build peer list from command line arguments
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
    time.sleep(2)
    
    # If I'm the first agent, I start the rumor
    if HOST_IP == "10.0.0.1":
        print("I AM THE SEED! Starting first rumor...")
        time.sleep(1)
        
        # Record start time
        with open(f'/tmp/metrics_{HOST_IP.replace(".", "_")}.txt', 'w') as f:
            f.write(f"SEED,RUMOR_001,{time.time()}\n")
        
        process_rumor("RUMOR_001")
    else:
        # Create empty metrics file
        with open(f'/tmp/metrics_{HOST_IP.replace(".", "_")}.txt', 'w') as f:
            f.write(f"STARTED,{time.time()}\n")
    
    # Keep running
    print("Agent is running...")
    while True:
        time.sleep(1)
