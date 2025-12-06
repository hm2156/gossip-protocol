import os
import re
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
    
    # Analyze results
    print("\nLATENCY TEST RESULTS\n")
    nodes = {
        'h1': {'delay': '50ms', 'loss': '0%'},
        'h2': {'delay': '10ms', 'loss': '0%'},
        'h3': {'delay': '100ms', 'loss': '2%'},
        'h4': {'delay': '20ms', 'loss': '0%'},
        'h5': {'delay': '5ms', 'loss': '0%'}
    }
    
    results = {}
    for node_name in nodes.keys():
        host = net.get(node_name)
        log_content = host.cmd('cat /tmp/lat_' + node_name + '.log 2>/dev/null || echo ""')
        
        received = 'NEW RUMOR' in log_content or 'RUMOR_001' in log_content
        time_match = re.search(r'Time: ([\d.]+)s', log_content)
        receive_time = float(time_match.group(1)) if time_match else None
        
        metrics_lines = re.findall(r'Sent: (\d+), Failed: (\d+)', log_content)
        if metrics_lines:
            sent, failed = metrics_lines[-1]
            sent, failed = int(sent), int(failed)
        else:
            sent, failed = 0, 0
        
        results[node_name] = {
            'received': received, 'time': receive_time, 'sent': sent, 'failed': failed,
            'delay': nodes[node_name]['delay'], 'loss': nodes[node_name]['loss']
        }
    
    print(f"{'Node':<6} {'Delay':<10} {'Loss':<8} {'Received':<12} {'Time(s)':<10} {'Sent':<8} {'Failed':<8}")
    print("-" * 70)
    for node, data in sorted(results.items()):
        received_str = "✓ Yes" if data['received'] else "✗ No"
        time_str = f"{data['time']:.2f}" if data['time'] else "N/A"
        print(f"{node:<6} {data['delay']:<10} {data['loss']:<8} {received_str:<12} {time_str:<10} {data['sent']:<8} {data['failed']:<8}")
    
    coverage = sum(1 for r in results.values() if r['received'])
    total_sent = sum(r['sent'] for r in results.values())
    total_failed = sum(r['failed'] for r in results.values())
    times = [r['time'] for r in results.values() if r['time'] is not None]
    max_time = max(times) if times else 0
    
    print("-" * 70)
    print(f"\nCoverage: {coverage}/5 nodes ({coverage/5*100:.0f}%)")
    print(f"Total Messages: {total_sent} sent, {total_failed} failed")
    print(f"Convergence Time: {max_time:.2f}s")
    print(f"High-latency node (h3, 100ms): {'✓ Received' if results['h3']['received'] else '✗ Not received'}")
    if results['h3']['time']:
        print(f"  → h3 received at: {results['h3']['time']:.2f}s\n")
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    test_latency_variation()