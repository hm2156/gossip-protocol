from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
import time
import os

def create_gossip_network():
    # Get current directory
    work_dir = os.getcwd()
    print(f"Working directory: {work_dir}")
    
    net = Mininet()
    s1 = net.addSwitch('s1')
    
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')
    
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)
    
    net.start()
    time.sleep(1)
    
    print("="*60)
    print("Starting agents with absolute path...")
    print("="*60)
    
    # Use absolute path
    cmd = f'cd {work_dir} && timeout 5 python3 gossip_agent.py 10.0.0.1 5000 10.0.0.2 5000'
    print(f"\nRunning: {cmd}\n")
    
    result = h1.cmd(cmd)
    print("--- H1 OUTPUT ---")
    print(result)
    print("--- END H1 OUTPUT ---")
    
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_gossip_network()
