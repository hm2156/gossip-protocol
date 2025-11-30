from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel
import time
import os

class GossipTopo(Topo):
    def build(self):
        # Add hosts
        h1 = self.addHost('h1', ip='10.0.0.1/8')
        h2 = self.addHost('h2', ip='10.0.0.2/8')
        h3 = self.addHost('h3', ip='10.0.0.3/8')
        
        # Add switch
        s1 = self.addSwitch('s1')
        
        # Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)

def run():
    work_dir = os.getcwd()
    
    topo = GossipTopo()
    net = Mininet(topo=topo)
    net.start()
    
    h1, h2, h3 = net.get('h1', 'h2', 'h3')
    
    print("\nTesting connectivity...")
    loss = net.pingAll()
    print(f"Packet loss: {loss}%\n")
    
    if loss < 100:
        print("Starting agents...")
        h1.cmd(f'cd {work_dir} && /usr/bin/python3 gossip_agent.py 10.0.0.1 5000 10.0.0.2 5000 > /tmp/h1.log 2>&1 &')
        h2.cmd(f'cd {work_dir} && /usr/bin/python3 gossip_agent.py 10.0.0.2 5000 10.0.0.1 5000 10.0.0.3 5000 > /tmp/h2.log 2>&1 &')
        h3.cmd(f'cd {work_dir} && /usr/bin/python3 gossip_agent.py 10.0.0.3 5000 10.0.0.1 5000 10.0.0.2 5000 > /tmp/h3.log 2>&1 &')
        
        time.sleep(5)
        print("\nCheck: h1 cat /tmp/h1.log\n")
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
