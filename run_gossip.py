from mininet.net import Mininet
from mininet.node import UserSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
import time
import os

def create_gossip_network():
    work_dir = os.getcwd()
    
    print("Creating network with Linux bridge...")
    # Use UserSwitch (Linux bridge) instead of OVS
    net = Mininet(switch=UserSwitch, autoSetMacs=True, autoStaticArp=True)
    
    s1 = net.addSwitch('s1')
    
    h1 = net.addHost('h1')
    h2 = net.addHost('h2')
    h3 = net.addHost('h3')
    h4 = net.addHost('h4')
    h5 = net.addHost('h5')
    
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)
    net.addLink(h4, s1)
    net.addLink(h5, s1)
    
    net.start()
    
    # Manually configure IPs
    h1.setIP('10.0.0.1/24')
    h2.setIP('10.0.0.2/24')
    h3.setIP('10.0.0.3/24')
    h4.setIP('10.0.0.4/24')
    h5.setIP('10.0.0.5/24')
    
    print("\nTesting ping...")
    result = net.ping([h1, h2], timeout=1)
    print(f"Ping loss: {result}%")
    
    if result == 0:
        print("✓ Network OK! Starting agents...\n")
        
        h1.cmd(f'cd {work_dir} && /usr/bin/python3 gossip_agent.py 10.0.0.1 5000 10.0.0.2 5000 10.0.0.3 5000 > /tmp/h1.log 2>&1 &')
        h2.cmd(f'cd {work_dir} && /usr/bin/python3 gossip_agent.py 10.0.0.2 5000 10.0.0.1 5000 10.0.0.3 5000 10.0.0.4 5000 > /tmp/h2.log 2>&1 &')
        h3.cmd(f'cd {work_dir} && /usr/bin/python3 gossip_agent.py 10.0.0.3 5000 10.0.0.1 5000 10.0.0.2 5000 10.0.0.4 5000 10.0.0.5 5000 > /tmp/h3.log 2>&1 &')
        h4.cmd(f'cd {work_dir} && /usr/bin/python3 gossip_agent.py 10.0.0.4 5000 10.0.0.2 5000 10.0.0.3 5000 10.0.0.5 5000 > /tmp/h4.log 2>&1 &')
        h5.cmd(f'cd {work_dir} && /usr/bin/python3 gossip_agent.py 10.0.0.5 5000 10.0.0.3 5000 10.0.0.4 5000 > /tmp/h5.log 2>&1 &')
        
        time.sleep(5)
        print("="*60)
        print("Agents running! Check logs:")
        print("  h1 cat /tmp/h1.log")
        print("="*60)
    else:
        print("✗ Network failed, not starting agents")
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_gossip_network()
