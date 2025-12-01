from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import OVSSwitch
from mininet.link import TCLink

def start_gossip_network():
    # Create the network object
    net = Mininet(switch=OVSSwitch, link=TCLink)

    print("--- 1. Creating Hosts and Switch ---")
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    h3 = net.addHost('h3', ip='10.0.0.3')
    s1 = net.addSwitch('s1')

    print("--- 2. Creating Links (Adding latency for realism) ---")
    # Add links with a slight delay (5ms) to simulate real-world latency
    net.addLink(h1, s1, delay='5ms')
    net.addLink(h2, s1, delay='5ms')
    net.addLink(h3, s1, delay='5ms')

    print("--- 3. Starting Network ---")
    net.start()

    # --- 4. Launching the Gossip Agents ---
    # The command structure is:
    # python3 gossip_agent.py <MY_IP> <MY_PORT> <PEER1_IP> <PEER1_PORT> <PEER2_IP> <PEER2_PORT> ...

    # Peers for all hosts are 10.0.0.1, 10.0.0.2, and 10.0.0.3.
    PORT = 8000
    
    # Peers for h1 (10.0.0.1) are h2 and h3
    h1_peers = f"10.0.0.2 {PORT} 10.0.0.3 {PORT}"
    h1_cmd = f"python3 gossip_agent.py 10.0.0.1 {PORT} {h1_peers} &"
    
    # Peers for h2 (10.0.0.2) are h1 and h3
    h2_peers = f"10.0.0.1 {PORT} 10.0.0.3 {PORT}"
    h2_cmd = f"python3 gossip_agent.py 10.0.0.2 {PORT} {h2_peers} &"

    # Peers for h3 (10.0.0.3) are h1 and h2
    h3_peers = f"10.0.0.1 {PORT} 10.0.0.2 {PORT}"
    h3_cmd = f"python3 gossip_agent.py 10.0.0.3 {PORT} {h3_peers} &"
    
    print("--- 4. Launching Agents on Hosts ---")
    # Launch agents in the background (&) on each host
    h1.cmd(h1_cmd)
    h2.cmd(h2_cmd)
    h3.cmd(h3_cmd)

    # h1 (10.0.0.1) will automatically start the rumor after a short delay (see gossip_agent.py)

    print("\n--- Network is running. Wait a few seconds for rumor spread. ---")
    print("Type 'h1 ping h2' to test connectivity.")
    print("Type 'exit' to stop the network.\n")
    
    # Open the Mininet CLI for interaction
    CLI(net)

    print("--- Stopping Network ---")
    net.stop()

if __name__ == '__main__':
    start_gossip_network()