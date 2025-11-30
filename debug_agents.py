from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
import time
import os

def test():
    work_dir = os.getcwd()
    print(f"Working directory: {work_dir}")
    
    net = Mininet()
    s1 = net.addSwitch('s1')
    
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    
    net.start()
    
    print("\n=== Test 1: Can hosts ping? ===")
    result = h1.cmd('ping -c 2 10.0.0.2')
    print(result)
    
    print("\n=== Test 2: Does python work? ===")
    result = h1.cmd('/usr/bin/python3 --version')
    print(result)
    
    print("\n=== Test 3: Can h1 see the file? ===")
    result = h1.cmd(f'ls -la {work_dir}/gossip_agent.py')
    print(result)
    
    print("\n=== Test 4: Try running agent for 3 seconds ===")
    h1.cmd(f'cd {work_dir} && timeout 3 /usr/bin/python3 gossip_agent.py 10.0.0.1 5000 10.0.0.2 5000 > /tmp/test.log 2>&1')
    time.sleep(4)
    
    result = h1.cmd('cat /tmp/test.log')
    print("Agent output:")
    print(result)
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    test()
