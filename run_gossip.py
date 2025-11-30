from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel
import time
import os

class GossipTopo(Topo):
    def build(self):
        # Add 5 hosts
        h1 = self.addHost('h1', ip='10.0.0.1/8')
        h2 = self.addHost('h2', ip='10.0.0.2/8')
        h3 = self.addHost('h3', ip='10.0.0.3/8')
        h4 = self.addHost('h4', ip='10.0.0.4/8')
        h5 = self.addHost('h5', ip='10.0.0.5/8')
        
        # Add switch
        s1 = self.addSwitch('s1')
        
        # Connect all hosts to switch
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(h4, s1)
        self.addLink(h5, s1)

def run():
    work_dir = os.getcwd()
    
    print("="*60)
    print("CREATING GOSSIP NETWORK")
    print("="*60)
    
    topo = GossipTopo()
    net = Mininet(topo=topo, controller=None)
    net.start()
    
    # Configure switch to forward all traffic
    s1 = net.get('s1')
    s1.cmd('ovs-ofctl add-flow s1 action=normal')
    
    h1, h2, h3, h4, h5 = net.get('h1', 'h2', 'h3', 'h4', 'h5')
    
    print("\nTesting network connectivity...")
    loss = net.pingAll()
    
    if loss > 0:
        print(f"Warning: {loss}% packet loss")
    else:
        print("✓ Network connectivity: OK")
    
    print("\n" + "="*60)
    print("STARTING GOSSIP AGENTS")
    print("="*60 + "\n")
    
    # Start agents
    h1.cmd(f'cd {work_dir} && /usr/bin/python3 gossip_agent.py 10.0.0.1 5000 10.0.0.2 5000 10.0.0.3 5000 > /tmp/h1.log 2>&1 &')
    h2.cmd(f'cd {work_dir} && /usr/bin/python3 gossip_agent.py 10.0.0.2 5000 10.0.0.1 5000 10.0.0.3 5000 10.0.0.4 5000 > /tmp/h2.log 2>&1 &')
    h3.cmd(f'cd {work_dir} && /usr/bin/python3 gossip_agent.py 10.0.0.3 5000 10.0.0.1 5000 10.0.0.2 5000 10.0.0.4 5000 10.0.0.5 5000 > /tmp/h3.log 2>&1 &')
    h4.cmd(f'cd {work_dir} && /usr/bin/python3 gossip_agent.py 10.0.0.4 5000 10.0.0.2 5000 10.0.0.3 5000 10.0.0.5 5000 > /tmp/h4.log 2>&1 &')
    h5.cmd(f'cd {work_dir} && /usr/bin/python3 gossip_agent.py 10.0.0.5 5000 10.0.0.3 5000 10.0.0.4 5000 > /tmp/h5.log 2>&1 &')
    
    print("Agents started! Waiting for gossip to spread...")
    time.sleep(8)
    
    print("\n" + "="*60)
    print("GOSSIP PROTOCOL RUNNING")
    print("="*60)
    print("\nUseful commands:")
    print("  h1 cat /tmp/h1.log          - View agent logs")
    print("  h1 cat /tmp/metrics_10_0_0_1.txt  - View metrics")
    print("  show_results                - Display summary")
    print("  pingall                     - Test connectivity")
    print("  exit                        - Stop network")
    print()
    
    CLI(net)
    
    print("\nStopping network...")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
