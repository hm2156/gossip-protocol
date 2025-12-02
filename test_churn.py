import os
from mininet.net import Mininet
from mininet.cli import CLI
import time

def test_churn():
    print("CHURN TEST: Simulating Node Failure During Gossip\n")
    
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
    
    h1.cmd(f'mkdir -p /tmp && {cd_cmd} {python_cmd} -u {script_to_use} 10.0.0.1 {PORT} 10.0.0.2 {PORT} 10.0.0.3 {PORT} > /tmp/churn_h1.log 2>&1 &')
    h2.cmd(f'mkdir -p /tmp && {cd_cmd} {python_cmd} -u {script_to_use} 10.0.0.2 {PORT} 10.0.0.1 {PORT} 10.0.0.3 {PORT} 10.0.0.4 {PORT} > /tmp/churn_h2.log 2>&1 &')
    h3.cmd(f'mkdir -p /tmp && {cd_cmd} {python_cmd} -u {script_to_use} 10.0.0.3 {PORT} 10.0.0.1 {PORT} 10.0.0.2 {PORT} 10.0.0.4 {PORT} 10.0.0.5 {PORT} > /tmp/churn_h3.log 2>&1 &')
    h4.cmd(f'mkdir -p /tmp && {cd_cmd} {python_cmd} -u {script_to_use} 10.0.0.4 {PORT} 10.0.0.2 {PORT} 10.0.0.3 {PORT} 10.0.0.5 {PORT} > /tmp/churn_h4.log 2>&1 &')
    h5.cmd(f'mkdir -p /tmp && {cd_cmd} {python_cmd} -u {script_to_use} 10.0.0.5 {PORT} 10.0.0.3 {PORT} 10.0.0.4 {PORT} > /tmp/churn_h5.log 2>&1 &')
    
    time.sleep(2)
    print("Phase 1: Letting rumor propagate (10 seconds)...")
    time.sleep(10)
    
    print("Simulating churn: Killing node h3...")
    h3.cmd("pkill -f gossip_agent.py")
    
    print("Phase 2: Observing gossip after churn (20 seconds)...")
    time.sleep(20)
    
    print("\nResults:")
    final_results = {}
    for host, name in [(h1, 'h1'), (h2, 'h2'), (h4, 'h4'), (h5, 'h5')]:
        log_content = host.cmd('cat /tmp/churn_' + name + '.log 2>/dev/null || echo ""')
        received_rumor = 'NEW RUMOR' in log_content or 'RUMOR_001' in log_content
        final_results[name] = received_rumor
        failed_sends = log_content.count("couldn't send") + log_content.count("Churn detected")
        status = "✓" if received_rumor else "✗"
        churn_info = f" ({failed_sends} failures)" if failed_sends > 0 else ""
        print(f"  {status} {name}: {'Received' if received_rumor else 'Not received'}{churn_info}")
    
    nodes_received = sum(1 for v in final_results.values() if v)
    total_nodes = len(final_results)
    
    print(f"\nSummary: {nodes_received}/{total_nodes} nodes received rumor")
    if nodes_received == total_nodes:
        print("SUCCESS: All nodes received rumor despite h3 failure")
    elif nodes_received > 0:
        print("PARTIAL: Some nodes received rumor")
    else:
        print("FAILURE: No nodes received rumor")
    print()
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    test_churn()