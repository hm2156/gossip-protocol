from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
import time
import os

def create_gossip_network():
    work_dir = os.getcwd()
    
    print("Creating network with OVS switch...")
    net = Mininet(switch=OVSSwitch)
    
    print("Adding switch...")
    s1 = net.addSwitch('s1')
    
    print("Adding hosts...")
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')
    h4 = net.addHost('h4', ip='10.0.0.4/24')
    h5 = net.addHost('h5', ip='10.0.0.5/24')
    
    print("Adding links...")
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)
    net.addLink(h4, s1)
    net.addLink(h5, s1)
    
    print("Starting network...")
    net.start()
    
    print("\nTesting connectivity...")
    result = h1.cmd('ping -c 1 10.0.0.2')
    if '1 received' in result:
        print("✓ Network connectivity OK!")
    else:
        print("✗ Network has issues")
        print(result)
    
    time.sleep(2)
    
    print("\n" + "="*60)
    print("Starting gossip agents...")
    print("="*60)
    
    h1.cmd(f'cd {work_dir} && /usr/bin/python3 gossip_agent.py 10.0.0.1 5000 10.0.0.2 5000 10.0.0.3 5000 > /tmp/h1.log 2>&1 &')
    h2.cmd(f'cd {work_dir} && /usr/bin/python3 gossip_agent.py 10.0.0.2 5000 10.0.0.1 5000 10.0.0.3 5000 10.0.0.4 5000 > /tmp/h2.log 2>&1 &')
    h3.cmd(f'cd {work_dir} && /usr/bin/python3 gossip_agent.py 10.0.0.3 5000 10.0.0.1 5000 10.0.0.2 5000 10.0.0.4 5000 10.0.0.5 5000 > /tmp/h3.log 2>&1 &')
    h4.cmd(f'cd {work_dir} && /usr/bin/python3 gossip_agent.py 10.0.0.4 5000 10.0.0.2 5000 10.0.0.3 5000 10.0.0.5 5000 > /tmp/h4.log 2>&1 &')
    h5.cmd(f'cd {work_dir} && /usr/bin/python3 gossip_agent.py 10.0.0.5 5000 10.0.0.3 5000 10.0.0.4 5000 > /tmp/h5.log 2>&1 &')
    
    print("Waiting for gossip to spread...")
    time.sleep(5)
    
    print("\n" + "="*60)
    print("GOSSIP NETWORK IS RUNNING!")
    print("="*60)
    print("\nCommands:")
    print("  h1 cat /tmp/h1.log")
    print("  h2 cat /tmp/h2.log")
    print("  pingall")
    print("  exit")
    print()
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_gossip_network()
