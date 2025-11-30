from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
import time

def create_gossip_network():
    print("Creating network...")
    net = Mininet()
    
    s1 = net.addSwitch('s1')
    
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')
    
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)
    
    print("Starting network...")
    net.start()
    time.sleep(1)
    
    print("="*60)
    print("Testing agent on h1...")
    print("="*60)
    
    # Run h1 in foreground to see output
    print("\n--- H1 OUTPUT ---")
    result = h1.cmd('python3 gossip_agent.py 10.0.0.1 5000 10.0.0.2 5000 10.0.0.3 5000')
    print(result)
    
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_gossip_network()