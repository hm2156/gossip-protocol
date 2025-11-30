from mininet.net import Mininet
from mininet.log import setLogLevel

def test():
    net = Mininet()
    h1 = net.addHost('h1')
    net.start()
    
    print("\n=== Test 1: Can h1 run python? ===")
    result = h1.cmd('python3 --version')
    print(result)
    
    print("\n=== Test 2: Can h1 see the file? ===")
    result = h1.cmd('ls -la gossip_agent.py')
    print(result)
    
    print("\n=== Test 3: What's h1's directory? ===")
    result = h1.cmd('pwd')
    print(result)
    
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    test()
