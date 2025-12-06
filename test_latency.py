import os
from mininet.net import Mininet
from mininet.cli import CLI
import time

def test_latency_variation():
    print("LATENCY TEST: Testing gossip with network delays\n")

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
    
    print("Adding network delays...")
    h1.cmd('tc qdisc add dev h1-eth0 root netem delay 50ms')
    h2.cmd('tc qdisc add dev h2-eth0 root netem delay 10ms')
    h3.cmd('tc qdisc add dev h3-eth0 root netem delay 100ms loss 2%')
    h4.cmd('tc qdisc add dev h4-eth0 root netem delay 20ms')
    h5.cmd('tc qdisc add dev h5-eth0 root netem delay 5ms')
    print("Delays: h1=50ms, h2=10ms, h3=100ms+2%loss, h4=20ms, h5=5ms\n")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, 'gossip_agent.py')
    python_cmd = 'python3'
    PORT = 8000
    
    script_to_use = '~/gossip_agent.py'
    for host in [h1, h2, h3, h4, h5]:
        host.cmd(f'cp {script_path} ~/gossip_agent.py 2>/dev/null')
        check = host.cmd('test -f ~/gossip_agent.py && echo "OK" || echo "FAIL"')
        if "OK" not in check:
            alt_check = host.cmd(f'test -f {script_path} && echo "OK" || echo "FAIL"')
            if "OK" in alt_check:
                script_to_use = script_path

    if script_to_use.startswith('~'):
        cd_cmd = 'cd ~ &&'
    else:
        cd_cmd = f'cd {script_dir} &&'

    h1.cmd(f'mkdir -p /tmp && {cd_cmd} {python_cmd} -u {script_to_use} 10.0.0.1 {PORT} 10.0.0.2 {PORT} 10.0.0.3 {PORT} > /tmp/lat_h1.log 2>&1 &')
    h2.cmd(f'mkdir -p /tmp && {cd_cmd} {python_cmd} -u {script_to_use} 10.0.0.2 {PORT} 10.0.0.1 {PORT} 10.0.0.3 {PORT} 10.0.0.4 {PORT} > /tmp/lat_h2.log 2>&1 &')
    h3.cmd(f'mkdir -p /tmp && {cd_cmd} {python_cmd} -u {script_to_use} 10.0.0.3 {PORT} 10.0.0.1 {PORT} 10.0.0.2 {PORT} 10.0.0.4 {PORT} 10.0.0.5 {PORT} > /tmp/lat_h3.log 2>&1 &')
    h4.cmd(f'mkdir -p /tmp && {cd_cmd} {python_cmd} -u {script_to_use} 10.0.0.4 {PORT} 10.0.0.2 {PORT} 10.0.0.3 {PORT} 10.0.0.5 {PORT} > /tmp/lat_h4.log 2>&1 &')
    h5.cmd(f'mkdir -p /tmp && {cd_cmd} {python_cmd} -u {script_to_use} 10.0.0.5 {PORT} 10.0.0.3 {PORT} 10.0.0.4 {PORT} > /tmp/lat_h5.log 2>&1 &')
    
    time.sleep(2)
    print("Waiting 60 seconds for gossip propagation...")
    time.sleep(60)
    
    # Copy log files from hosts to main filesystem for analysis
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print("\nCopying log files from hosts to main filesystem...")
    for i in range(1, 6):
        host = net.get(f'h{i}')
        log_content = host.cmd('cat /tmp/lat_h' + str(i) + '.log 2>/dev/null || echo ""')
        # Write to main filesystem /tmp so extract script can read it
        with open(f'/tmp/lat_h{i}.log', 'w') as f:
            f.write(log_content)
    
    print("LATENCY TEST COMPLETE")
    print("Run: python3 extract_latency_metrics.py > latency_results.txt\n")
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    test_latency_variation()