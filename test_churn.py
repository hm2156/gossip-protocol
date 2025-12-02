from mininet.net import Mininet
from mininet.cli import CLI
import time

def test_churn():
    print("\n" + "="*70)
    print("CHURN TEST: Simulating Node Failure During Gossip")
    print("="*70 + "\n")
    
    net = Mininet(controller=None)
    
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    h3 = net.addHost('h3', ip='10.0.0.3')
    h4 = net.addHost('h4', ip='10.0.0.4')
    h5 = net.addHost('h5', ip='10.0.0.5')
    
    s1 = net.addSwitch('s1')
    
    for h in [h1, h2, h3, h4, h5]:
        net.addLink(h, s1)
    
    net.start()
    s1.cmd('ovs-ofctl add-flow s1 action=normal')
    
    PORT = 8000
    
    print("Starting all agents...")
    h1.cmd(f"/usr/bin/python3 gossip_agent.py 10.0.0.1 {PORT} 10.0.0.2 {PORT} 10.0.0.3 {PORT} > /tmp/churn_h1.log 2>&1 &")
    h2.cmd(f"/usr/bin/python3 gossip_agent.py 10.0.0.2 {PORT} 10.0.0.1 {PORT} 10.0.0.3 {PORT} 10.0.0.4 {PORT} > /tmp/churn_h2.log 2>&1 &")
    h3.cmd(f"/usr/bin/python3 gossip_agent.py 10.0.0.3 {PORT} 10.0.0.1 {PORT} 10.0.0.2 {PORT} 10.0.0.4 {PORT} 10.0.0.5 {PORT} > /tmp/churn_h3.log 2>&1 &")
    h4.cmd(f"/usr/bin/python3 gossip_agent.py 10.0.0.4 {PORT} 10.0.0.2 {PORT} 10.0.0.3 {PORT} 10.0.0.5 {PORT} > /tmp/churn_h4.log 2>&1 &")
    h5.cmd(f"/usr/bin/python3 gossip_agent.py 10.0.0.5 {PORT} 10.0.0.3 {PORT} 10.0.0.4 {PORT} > /tmp/churn_h5.log 2>&1 &")
    
    time.sleep(5)
    print("\n🔥 SIMULATING CHURN: Killing node h3 (central hub)")
    h3.cmd("pkill -f gossip_agent.py")
    print("⚠️  Node h3 is DOWN!\n")
    
    print("Waiting 20 seconds to see if gossip continues despite failure...")
    time.sleep(20)
    
    print("\n" + "="*70)
    print("CHURN TEST COMPLETE")
    print("="*70)
    print("\nCheck if rumor reached h4 and h5 despite h3 failing:")
    print("  h4 cat /tmp/churn_h4.log")
    print("  h5 cat /tmp/churn_h5.log")
    print("\nLook for 'NEW RUMOR' and 'Churn detected' messages\n")
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    test_churn()