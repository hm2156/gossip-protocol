from mininet.net import Mininet
from mininet.cli import CLI
import time

def test_churn():
    net = Mininet()
    net.addController('c0')
    
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    h3 = net.addHost('h3', ip='10.0.0.3')
    h4 = net.addHost('h4', ip='10.0.0.4')
    h5 = net.addHost('h5', ip='10.0.0.5')
    
    s1 = net.addSwitch('s1')
    
    for h in [h1, h2, h3, h4, h5]:
        net.addLink(h, s1)
    
    net.start()
    
    PORT = 8000
    
    # Start all agents
    h1.cmd(f"python3 gossip_agent.py 10.0.0.1 {PORT} 10.0.0.2 {PORT} 10.0.0.3 {PORT} > /tmp/h1.log 2>&1 &")
    h2.cmd(f"python3 gossip_agent.py 10.0.0.2 {PORT} 10.0.0.1 {PORT} 10.0.0.3 {PORT} 10.0.0.4 {PORT} > /tmp/h2.log 2>&1 &")
    h3.cmd(f"python3 gossip_agent.py 10.0.0.3 {PORT} 10.0.0.1 {PORT} 10.0.0.2 {PORT} 10.0.0.4 {PORT} 10.0.0.5 {PORT} > /tmp/h3.log 2>&1 &")
    h4.cmd(f"python3 gossip_agent.py 10.0.0.4 {PORT} 10.0.0.2 {PORT} 10.0.0.3 {PORT} 10.0.0.5 {PORT} > /tmp/h4.log 2>&1 &")
    h5.cmd(f"python3 gossip_agent.py 10.0.0.5 {PORT} 10.0.0.3 {PORT} 10.0.0.4 {PORT} > /tmp/h5.log 2>&1 &")
    
    print("\n=== All agents started ===")
    time.sleep(5)
    
    print("\n=== SIMULATING CHURN: Killing h3 ===")
    h3.cmd("pkill -f gossip_agent.py")
    
    print("=== Waiting to see if rumor still spreads... ===")
    time.sleep(15)
    
    print("\n=== Check logs to see impact of churn ===")
    print("h1 cat /tmp/h1.log")
    print("h2 cat /tmp/h2.log")
    print("h4 cat /tmp/h4.log")
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    test_churn()