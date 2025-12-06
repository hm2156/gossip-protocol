import os
import time
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import OVSSwitch
from mininet.link import TCLink 

def test_latency_variation():
    print("LATENCY TEST: Setting Asymmetric Delays on Links\n")

    net = Mininet(controller=None) 

    # Add Hosts and Switch
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    h3 = net.addHost('h3', ip='10.0.0.3')
    h4 = net.addHost('h4', ip='10.0.0.4')
    h5 = net.addHost('h5', ip='10.0.0.5')
    s1 = net.addSwitch('s1', cls=OVSSwitch)

    # --- Links with Asymmetric Delays ---
    net.addLink(h1, s1, cls=TCLink, delay='50ms', loss=0) 
    net.addLink(h2, s1, cls=TCLink, delay='10ms', loss=0) 
    net.addLink(h3, s1, cls=TCLink, delay='100ms', loss=2) 
    net.addLink(h4, s1, cls=TCLink, delay='20ms', loss=0) 
    net.addLink(h5, s1, cls=TCLink, delay='5ms', loss=0)  

    net.start()
    s1.cmd('ovs-ofctl add-flow s1 action=normal')
    
    # ADD THIS - Launch gossip agents
    PORT = 8000
    h1.cmd(f"/usr/bin/python3 gossip_agent.py 10.0.0.1 {PORT} 10.0.0.2 {PORT} 10.0.0.3 {PORT} > /tmp/h1.log 2>&1 &")
    h2.cmd(f"/usr/bin/python3 gossip_agent.py 10.0.0.2 {PORT} 10.0.0.1 {PORT} 10.0.0.3 {PORT} 10.0.0.4 {PORT} > /tmp/h2.log 2>&1 &")
    h3.cmd(f"/usr/bin/python3 gossip_agent.py 10.0.0.3 {PORT} 10.0.0.1 {PORT} 10.0.0.2 {PORT} 10.0.0.4 {PORT} 10.0.0.5 {PORT} > /tmp/h3.log 2>&1 &")
    h4.cmd(f"/usr/bin/python3 gossip_agent.py 10.0.0.4 {PORT} 10.0.0.2 {PORT} 10.0.0.3 {PORT} 10.0.0.5 {PORT} > /tmp/h4.log 2>&1 &")
    h5.cmd(f"/usr/bin/python3 gossip_agent.py 10.0.0.5 {PORT} 10.0.0.3 {PORT} 10.0.0.4 {PORT} > /tmp/h5.log 2>&1 &")
    
    print("\nAgents launched with asymmetric latency. Rumor will start on h1.")
    print("Wait 45 seconds, then type 'exit'")
    time.sleep(45)  # Changed from 20 to 45 for high latency
    
    print("\nSimulation complete. Use: python3 extract_metrics.py")
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    test_latency_variation()