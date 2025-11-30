from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel
import time
import os

class SimpleTopo(Topo):
    def build(self):
        h1 = self.addHost('h1', ip='10.0.0.1/8')
        h2 = self.addHost('h2', ip='10.0.0.2/8')
        h3 = self.addHost('h3', ip='10.0.0.3/8')
        
        s1 = self.addSwitch('s1')
        
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)

def run():
    work_dir = os.getcwd()
    
    topo = SimpleTopo()
    # Don't add a controller
    net = Mininet(topo=topo, controller=None)
    net.start()
    
    # Manually set up the switch
    s1 = net.get('s1')
    s1.cmd('ovs-ofctl add-flow s1 action=normal')
    
    h1, h2, h3 = net.get('h1', 'h2', 'h3')
    
    print("\nTesting connectivity...")
    loss = net.pingAll()
    print(f"Packet loss: {loss}%\n")
    
    if loss < 100:
        print("✓ Network works! Starting agents...")
        h1.cmd(f'cd {work_dir} && /usr/bin/python3 gossip_agent.py 10.0.0.1 5000 10.0.0.2 5000 > /tmp/h1.log 2>&1 &')
        h2.cmd(f'cd {work_dir} && /usr/bin/python3 gossip_agent.py 10.0.0.2 5000 10.0.0.1 5000 10.0.0.3 5000 > /tmp/h2.log 2>&1 &')
        h3.cmd(f'cd {work_dir} && /usr/bin/python3 gossip_agent.py 10.0.0.3 5000 10.0.0.1 5000 10.0.0.2 5000 > /tmp/h3.log 2>&1 &')
        
        time.sleep(5)
        print("\n" + "="*60)
        print("Check logs:")
        print("  h1 cat /tmp/h1.log")
        print("  h2 cat /tmp/h2.log")
        print("  h3 cat /tmp/h3.log")
        print("="*60 + "\n")
    else:
        print("✗ Network failed")
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
