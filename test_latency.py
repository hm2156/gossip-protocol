import os
import time
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.link import TCLink 

def test_latency_variation():
    print("\n" + "="*70)
    print("LATENCY TEST: Asymmetric Network Delays")
    print("="*70 + "\n")

    net = Mininet(controller=None) 

    # Add Hosts and Switch
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    h3 = net.addHost('h3', ip='10.0.0.3')
    h4 = net.addHost('h4', ip='10.0.0.4')
    h5 = net.addHost('h5', ip='10.0.0.5')
    s1 = net.addSwitch('s1')

    # Links with Different Delays (simulating geographic distance)
    print("Setting up network with delays:")
    print("  h1: 50ms (moderate)")
    print("  h2: 10ms (low)")
    print("  h3: 100ms + 2% loss (high latency)")
    print("  h4: 20ms (medium)")
    print("  h5: 5ms (very low)\n")
    
    net.addLink(h1, s1, cls=TCLink, delay='50ms', loss=0) 
    net.addLink(h2, s1, cls=TCLink, delay='10ms', loss=0) 
    net.addLink(h3, s1, cls=TCLink, delay='100ms', loss=2) 
    net.addLink(h4, s1, cls=TCLink, delay='20ms', loss=0) 
    net.addLink(h5, s1, cls=TCLink, delay='5ms', loss=0)  

    net.start()
    s1.cmd('ovs-ofctl add-flow s1 action=normal')
    
    PORT = 8000
    
    # Get current protocol mode from gossip_agent.py
    with open('gossip_agent.py', 'r') as f:
        for line in f:
            if 'PROTOCOL_MODE =' in line:
                mode = line.split("'")[1]
                break
    
    print(f"Starting agents in {mode} mode...\n")
    
    # Launch agents
    h1.cmd(f"/usr/bin/python3 gossip_agent.py 10.0.0.1 {PORT} 10.0.0.2 {PORT} 10.0.0.3 {PORT} > /tmp/latency_h1.log 2>&1 &")
    h2.cmd(f"/usr/bin/python3 gossip_agent.py 10.0.0.2 {PORT} 10.0.0.1 {PORT} 10.0.0.3 {PORT} 10.0.0.4 {PORT} > /tmp/latency_h2.log 2>&1 &")
    h3.cmd(f"/usr/bin/python3 gossip_agent.py 10.0.0.3 {PORT} 10.0.0.1 {PORT} 10.0.0.2 {PORT} 10.0.0.4 {PORT} 10.0.0.5 {PORT} > /tmp/latency_h3.log 2>&1 &")
    h4.cmd(f"/usr/bin/python3 gossip_agent.py 10.0.0.4 {PORT} 10.0.0.2 {PORT} 10.0.0.3 {PORT} 10.0.0.5 {PORT} > /tmp/latency_h4.log 2>&1 &")
    h5.cmd(f"/usr/bin/python3 gossip_agent.py 10.0.0.5 {PORT} 10.0.0.3 {PORT} 10.0.0.4 {PORT} > /tmp/latency_h5.log 2>&1 &")
    
    print("Agents running. Waiting 45 seconds for gossip with latency...\n")
    time.sleep(45)
    
    print("="*70)
    print(f"LATENCY TEST COMPLETE ({mode} mode)")
    print("="*70)
    print("\nCheck results:")
    print("  h1 cat /tmp/latency_h1.log")
    print("  h3 cat /tmp/latency_h3.log (high latency + loss)")
    print("\nRun: python3 extract_latency_metrics.py\n")
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    test_latency_variation()