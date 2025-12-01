from mininet.net import Mininet
from mininet.cli import CLI
# Import OVSSwitch to ensure correct switch type
from mininet.node import OVSSwitch
from mininet.link import TCLink

def start_gossip_network():
    # Mininet(switch=OVSSwitch) ensures the switch can handle routing/ARP correctly.
    net = Mininet(switch=OVSSwitch, link=TCLink)

    print("--- 1. Creating Hosts and Switch ---")
    # Using fixed IPs is good for passing arguments
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    h3 = net.addHost('h3', ip='10.0.0.3')
    # Use the default OVS Switch
    s1 = net.addSwitch('s1', cls=OVSSwitch) 

    print("--- 2. Creating Links (Adding latency for realism) ---")
    # Add links with a slight delay (5ms) as planned
    net.addLink(h1, s1, delay='5ms')
    net.addLink(h2, s1, delay='5ms')
    net.addLink(h3, s1, delay='5ms')

    print("--- 3. Starting Network ---")
    net.start()

    # --- 4. Launching the Gossip Agents ---
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
    # Launch agents in the background (&)
    h1.cmd(h1_cmd)
    h2.cmd(h2_cmd)
    h3.cmd(h3_cmd)

    print("\n--- Network is running. Check output for rumor spread. ---")
    print("Type 'h1 ping h3' to test connectivity again.")
    print("Type 'exit' to stop the network.\n")
    
    # Open the Mininet CLI for interaction
    CLI(net)

    print("--- Stopping Network ---")
    net.stop()

if __name__ == '__main__':
    start_gossip_network()