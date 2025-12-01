from mininet.net import Mininet
from mininet.cli import CLI

# Note: We are now using Mininet's defaults for the switch (OVSKernelSwitch) 
# and link (DefaultLink), which often resolves connectivity issues.

def start_gossip_network():
    # Mininet uses default settings that usually guarantee connectivity
    net = Mininet() 

    print("--- 1. Creating Controller, Hosts, and Switch ---")
    # Add a controller (C0)
    net.addController('c0')
    
    # Add Hosts
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    h3 = net.addHost('h3', ip='10.0.0.3')
    
    # Add Switch
    s1 = net.addSwitch('s1') 

    print("--- 2. Creating Links ---")
    # Connect all hosts to the switch
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)

    print("--- 3. Starting Network ---")
    net.start()

    # --- 4. Launching the Gossip Agents ---
    PORT = 8000
    
    # Define peers
    h1_peers = f"10.0.0.2 {PORT} 10.0.0.3 {PORT}"
    h2_peers = f"10.0.0.1 {PORT} 10.0.0.3 {PORT}"
    h3_peers = f"10.0.0.1 {PORT} 10.0.0.2 {PORT}"
    
    print("--- 4. Launching Agents on Hosts ---")
    # Launch agents in the background (&) on each host
    h1.cmd(f"python3 gossip_agent.py 10.0.0.1 {PORT} {h1_peers} &")
    h2.cmd(f"python3 gossip_agent.py 10.0.0.2 {PORT} {h2_peers} &")
    h3.cmd(f"python3 gossip_agent.py 10.0.0.3 {PORT} {h3_peers} &")

    print("\n--- Network is running. Check output for rumor spread. ---")
    print("Type 'h1 ping h3' to test connectivity again.")
    print("Type 'exit' to stop the network.\n")
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    start_gossip_network()