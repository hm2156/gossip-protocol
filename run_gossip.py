#!/usr/bin/env python3
from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.log import setLogLevel
import time

def create_gossip_network():
    """Create a network with 5 gossip agents"""
    
    print("Creating network...")
    net = Mininet()
    
    # Add switch
    s1 = net.addSwitch('s1')
    
    # Add 5 hosts (gossip agents)
    print("Adding hosts...")
    hosts = []
    for i in range(1, 6):
        h = net.addHost(f'h{i}', ip=f'10.0.0.{i}/24')
        hosts.append(h)
        net.addLink(h, s1)
    
    # Start network
    print("Starting network...")
    net.start()
    time.sleep(2)
    
    print("\n" + "="*60)
    print("Starting gossip agents on each host...")
    print("="*60 + "\n")
    
    # Start gossip agents on each host
    # h1 is the seed (10.0.0.1)
    hosts[0].cmd('python3 gossip_agent.py 10.0.0.1 5000 10.0.0.2 5000 10.0.0.3 5000 > /tmp/h1.log 2>&1 &')
    hosts[1].cmd('python3 gossip_agent.py 10.0.0.2 5000 10.0.0.1 5000 10.0.0.3 5000 10.0.0.4 5000 > /tmp/h2.log 2>&1 &')
    hosts[2].cmd('python3 gossip_agent.py 10.0.0.3 5000 10.0.0.1 5000 10.0.0.2 5000 10.0.0.4 5000 10.0.0.5 5000 > /tmp/h3.log 2>&1 &')
    hosts[3].cmd('python3 gossip_agent.py 10.0.0.4 5000 10.0.0.2 5000 10.0.0.3 5000 10.0.0.5 5000 > /tmp/h4.log 2>&1 &')
    hosts[4].cmd('python3 gossip_agent.py 10.0.0.5 5000 10.0.0.3 5000 10.0.0.4 5000 > /tmp/h5.log 2>&1 &')
    
    print("Agents started! Waiting for gossip to spread...")
    time.sleep(3)
    
    print("\n" + "="*60)
    print("GOSSIP NETWORK IS RUNNING!")
    print("="*60)
    print("\nUseful commands:")
    print("  h1 tail /tmp/h1.log    - View h1's log")
    print("  h2 tail /tmp/h2.log    - View h2's log")
    print("  pingall                - Test connectivity")
    print("  exit                   - Stop network")
    print("\nEntering Mininet CLI...\n")
    
    CLI(net)
    
    print("\nStopping network...")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_gossip_network()