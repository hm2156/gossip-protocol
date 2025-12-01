import socket
import threading
import sys
import time
import random
import json

# --- Configuration (Change this to switch protocols) ---
# Available modes: 'PUSH', 'PULL', 'HYBRID'
PROTOCOL_MODE = 'HYBRID' 
PULL_INTERVAL = 5 # seconds between pull attempts (for PULL or HYBRID mode)
FANOUT = 2 # Number of peers to push/pull from

# --- Globals ---
HOST_IP = sys.argv[1]
PORT = int(sys.argv[2])
PEERS = []  # Will be filled from command line arguments

# State
known_rumors = set()
RUMOR_TIMESTAMPS = {} # {rumor_id: time_received}

# Metrics
TOTAL_SENT_MESSAGES = 0
FAILED_SENDS = 0
START_TIME = time.time() # Used to measure total run time
LOCK = threading.Lock()


def update_metrics(sent=0, failed=0):
    """Safely update global metrics using a lock."""
    global TOTAL_SENT_MESSAGES, FAILED_SENDS
    with LOCK:
        TOTAL_SENT_MESSAGES += sent
        FAILED_SENDS += failed


def process_rumor(rumor_id):
    """Process the received rumor and update the internal state"""
    global known_rumors, RUMOR_TIMESTAMPS
    
    if rumor_id not in known_rumors:
        receive_time = time.time()
        known_rumors.add(rumor_id)
        RUMOR_TIMESTAMPS[rumor_id] = receive_time

        print(f"\n[NEW RUMOR] Agent {HOST_IP} received rumor: {rumor_id} (Time: {receive_time - START_TIME:.2f}s)")
        
        # Based on protocol mode, decide next action
        if PROTOCOL_MODE in ('PUSH', 'HYBRID'):
            gossip_push(rumor_id)
    else:
        print(f"Agent {HOST_IP} already knows rumor: {rumor_id}")


def listener_thread():
    """Listen for incoming connections and process received messages"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', PORT))
    server_socket.listen(5)
    print(f"Agent {HOST_IP} on {PORT} is listening")

    while True:
        try:
            connection, addr = server_socket.accept()
            msg_data = connection.recv(4096).decode()
            connection.close()

            if not msg_data:
                continue
                
            # Messages are now JSON objects for complex data
            try:
                msg = json.loads(msg_data)
            except json.JSONDecodeError:
                print(f"Agent {HOST_IP} received invalid JSON: {msg_data}")
                continue
            
            msg_type = msg.get('type')

            if msg_type == 'RUMOR_PUSH':
                rumor_id = msg.get('rumor_id')
                process_rumor(rumor_id)
            
            elif msg_type == 'PULL_REQUEST':
                # Respond to a PULL_REQUEST with the agent's full rumor set
                peer_ip = addr[0]
                peer_port = msg.get('port') # Port of the requesting agent
                print(f"Agent {HOST_IP} received PULL_REQUEST from {peer_ip}. Responding with state.")
                
                # Send back the known rumors as a list
                response_msg = {'type': 'PULL_RESPONSE', 'rumors': list(known_rumors)}
                sender_thread(peer_ip, peer_port, json.dumps(response_msg))
            
            elif msg_type == 'PULL_RESPONSE':
                # Received the state from a peer. Update state.
                rumor_list = msg.get('rumors', [])
                print(f"Agent {HOST_IP} received PULL_RESPONSE with {len(rumor_list)} rumors.")
                
                for rumor_id in rumor_list:
                    process_rumor(rumor_id)

        except Exception as e:
            print(f"Listener error on {HOST_IP}: {e}")
            pass # Keep listener thread alive


def sender_thread(target_ip, target_port, msg_json):
    """Send a rumor or control message to a target agent and update metrics"""
    update_metrics(sent=1) # Always count a message attempt
    
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(2)
        client_socket.connect((target_ip, target_port))
        client_socket.sendall(msg_json.encode())
        client_socket.close()
        # print(f"Agent {HOST_IP} sent {msg_json[:10]}... to {target_ip}:{target_port}")
   
    except Exception as error:
        # Crucial for measuring reliability/churn!
        update_metrics(failed=1) 
        print(f"Agent {HOST_IP} couldn't send to {target_ip}:{target_port}. Churn detected? - {error}")


def gossip_push(rumor_id):
    """Push gossip: send rumor to random subset of peers"""
    if not PEERS:
        return
    
    targets = random.sample(PEERS, min(FANOUT, len(PEERS)))
    
    for peer_ip, peer_port in targets:
        push_msg = {'type': 'RUMOR_PUSH', 'rumor_id': rumor_id}
        t = threading.Thread(target=sender_thread, args=(peer_ip, peer_port, json.dumps(push_msg)))
        t.start()


def gossip_pull():
    """Pull gossip: send PULL_REQUEST to a random subset of peers"""
    if not PEERS:
        return
        
    targets = random.sample(PEERS, min(FANOUT, len(PEERS)))
    
    for peer_ip, peer_port in targets:
        # The pull request needs to tell the peer where to send the PULL_RESPONSE back
        pull_msg = {'type': 'PULL_REQUEST', 'ip': HOST_IP, 'port': PORT}
        t = threading.Thread(target=sender_thread, args=(peer_ip, peer_port, json.dumps(pull_msg)))
        t.start()


def pull_interval_thread():
    """Periodically triggers a PULL action based on the protocol mode."""
    while True:
        time.sleep(PULL_INTERVAL)
        if PROTOCOL_MODE in ('PULL', 'HYBRID'):
            print(f"\n--- {PROTOCOL_MODE} PULL initiated by {HOST_IP} ---")
            gossip_pull()


if __name__ == '__main__':
    # command line arguments parsing remains the same
    if len(sys.argv) > 3:
        i = 3
        while i < len(sys.argv):
            peer_ip = sys.argv[i]
            peer_port = int(sys.argv[i + 1])
            PEERS.append((peer_ip, peer_port))
            i += 2
    
    print(f"My IP: {HOST_IP}, My Port: {PORT}. Mode: {PROTOCOL_MODE}")
    print(f"My Peers: {PEERS}")
    
    # Start listener thread
    listener = threading.Thread(target=listener_thread, daemon=True)
    listener.start()
    
    # Start periodic pull thread (for PULL and HYBRID modes)
    pull_timer = threading.Thread(target=pull_interval_thread, daemon=True)
    pull_timer.start()

    time.sleep(1)  # Give threads time to start
    
    # If I'm the seed agent (10.0.0.1), I start the rumor
    if HOST_IP == "10.0.0.1":
        print("\n!!! Starting first rumor (RUMOR_001)... !!!")
        process_rumor("RUMOR_001")
    
    # Keep process alive and periodically print metrics
    print("\nAgent is running. Gossip will occur automatically...")
    while True:
        time.sleep(10)
        # Log metrics every 10 seconds (useful for the final report)
        print(f"\n[METRICS] {HOST_IP} - Known Rumors: {len(known_rumors)}, Sent: {TOTAL_SENT_MESSAGES}, Failed: {FAILED_SENDS}")