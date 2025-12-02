from mininet.net import Mininet
from mininet.cli import CLI

def start_gossip_network():
    # NO CONTROLLER
    net = Mininet(controller=None) 

    print("--- 1. Creating Hosts and Switch ---")
    
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    h3 = net.addHost('h3', ip='10.0.0.3')
    h4 = net.addHost('h4', ip='10.0.0.4')
    h5 = net.addHost('h5', ip='10.0.0.5')
    
    s1 = net.addSwitch('s1') 

    print("--- 2. Creating Links ---")
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)
    net.addLink(h4, s1)
    net.addLink(h5, s1)

    print("--- 3. Starting Network ---")
    net.start()
    
    # Configure switch to forward all traffic
    s1.cmd('ovs-ofctl add-flow s1 action=normal')

    PORT = 8000
    
    h1.cmd(f"/usr/bin/python3 gossip_agent.py 10.0.0.1 {PORT} 10.0.0.2 {PORT} 10.0.0.3 {PORT} > /tmp/h1.log 2>&1 &")
    h2.cmd(f"/usr/bin/python3 gossip_agent.py 10.0.0.2 {PORT} 10.0.0.1 {PORT} 10.0.0.3 {PORT} 10.0.0.4 {PORT} > /tmp/h2.log 2>&1 &")
    h3.cmd(f"/usr/bin/python3 gossip_agent.py 10.0.0.3 {PORT} 10.0.0.1 {PORT} 10.0.0.2 {PORT} 10.0.0.4 {PORT} 10.0.0.5 {PORT} > /tmp/h3.log 2>&1 &")
    h4.cmd(f"/usr/bin/python3 gossip_agent.py 10.0.0.4 {PORT} 10.0.0.2 {PORT} 10.0.0.3 {PORT} 10.0.0.5 {PORT} > /tmp/h4.log 2>&1 &")
    h5.cmd(f"/usr/bin/python3 gossip_agent.py 10.0.0.5 {PORT} 10.0.0.3 {PORT} 10.0.0.4 {PORT} > /tmp/h5.log 2>&1 &")

    print("\n=== WAIT 30 SECONDS, then type 'exit' ===\n")
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    start_gossip_network()