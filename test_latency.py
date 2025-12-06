from mininet.net import Mininet
from mininet.cli import CLI
import time
import os

def test_latency_variation():
    print("\n" + "="*70)
    print("LATENCY TEST: Testing gossip with network delays")
    print("="*70 + "\n")

    # Get current directory
    work_dir = os.getcwd()
    print(f"Working directory: {work_dir}\n")

    net = Mininet(controller=None) 

    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    h3 = net.addHost('h3', ip='10.0.0.3')
    h4 = net.addHost('h4', ip='10.0.0.4')
    h5 = net.addHost('h5', ip='10.0.0.5')
    s1 = net.addSwitch('s1')

    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)
    net.addLink(h4, s1)
    net.addLink(h5, s1)

    net.start()
    s1.cmd('ovs-ofctl add-flow s1 action=normal')
    
    print("Adding network delays with tc...")
    h1.cmd('tc qdisc add dev h1-eth0 root netem delay 50ms')
    h2.cmd('tc qdisc add dev h2-eth0 root netem delay 10ms')
    h3.cmd('tc qdisc add dev h3-eth0 root netem delay 100ms loss 2%')
    h4.cmd('tc qdisc add dev h4-eth0 root netem delay 20ms')
    h5.cmd('tc qdisc add dev h5-eth0 root netem delay 5ms')
    
    print("Delays configured:")
    print("  h1: 50ms, h2: 10ms, h3: 100ms+2%loss, h4: 20ms, h5: 5ms\n")
    
    PORT = 8000
    
    # Get protocol mode
    with open('gossip_agent.py', 'r') as f:
        for line in f:
            if 'PROTOCOL_MODE =' in line:
                mode = line.split("'")[1]
                break
    
    print(f"Starting agents in {mode} mode...\n")
    
    # Launch with FULL PATHS
    h1.cmd(f"cd {work_dir} && /usr/bin/python3 {work_dir}/gossip_agent.py 10.0.0.1 {PORT} 10.0.0.2 {PORT} 10.0.0.3 {PORT} > /tmp/lat_h1.log 2>&1 &")
    h2.cmd(f"cd {work_dir} && /usr/bin/python3 {work_dir}/gossip_agent.py 10.0.0.2 {PORT} 10.0.0.1 {PORT} 10.0.0.3 {PORT} 10.0.0.4 {PORT} > /tmp/lat_h2.log 2>&1 &")
    h3.cmd(f"cd {work_dir} && /usr/bin/python3 {work_dir}/gossip_agent.py 10.0.0.3 {PORT} 10.0.0.1 {PORT} 10.0.0.2 {PORT} 10.0.0.4 {PORT} 10.0.0.5 {PORT} > /tmp/lat_h3.log 2>&1 &")
    h4.cmd(f"cd {work_dir} && /usr/bin/python3 {work_dir}/gossip_agent.py 10.0.0.4 {PORT} 10.0.0.2 {PORT} 10.0.0.3 {PORT} 10.0.0.5 {PORT} > /tmp/lat_h4.log 2>&1 &")
    h5.cmd(f"cd {work_dir} && /usr/bin/python3 {work_dir}/gossip_agent.py 10.0.0.5 {PORT} 10.0.0.3 {PORT} 10.0.0.4 {PORT} > /tmp/lat_h5.log 2>&1 &")
    
    time.sleep(5)
    
    print("Checking logs (first 3 lines):")
    for i in range(1, 6):
        print(f"\n--- h{i} ---")
        result = net.get(f'h{i}').cmd(f'head -3 /tmp/lat_h{i}.log')
        print(result if result.strip() else "  (empty or not started)")
    
    print("\nWaiting 60 seconds for gossip...\n")
    time.sleep(60)
    
    print("="*70)
    print(f"LATENCY TEST COMPLETE ({mode} mode)")
    print("="*70)
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    test_latency_variation()