import os
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
    
    # Get the absolute path to the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, 'gossip_agent.py')
    
    # Use python3 (Mininet hosts usually have it in PATH)
    python_cmd = 'python3'
    
    PORT = 8000
    
    print("--- Copying script to each host...")
    script_to_use = '~/gossip_agent.py'  # Default to copied version
    
    for i, host in enumerate([h1, h2, h3, h4, h5], 1):
        result = host.cmd(f'cp {script_path} ~/gossip_agent.py 2>&1')
        # Verify copy worked
        check = host.cmd('test -f ~/gossip_agent.py && echo "OK" || echo "FAIL"')
        if "OK" not in check:
            print(f"  ⚠ Warning: Script copy to h{i} may have failed")
            # Try alternative: use script_path directly if it's accessible
            alt_check = host.cmd(f'test -f {script_path} && echo "OK" || echo "FAIL"')
            if "OK" in alt_check:
                script_to_use = script_path
                print(f"  ✓ Using direct path instead")
            else:
                print(f"  ✗ ERROR: Script not accessible on h{i}!")
    
    print(f"Using script: {script_to_use}")
    print("\n--- Starting all agents...")
    
    # Use unbuffered output (-u flag) and ensure /tmp exists
    if script_to_use.startswith('~'):
        cd_cmd = 'cd ~ &&'
    else:
        cd_cmd = f'cd {script_dir} &&'
    
    h1.cmd(f'mkdir -p /tmp && {cd_cmd} {python_cmd} -u {script_to_use} 10.0.0.1 {PORT} 10.0.0.2 {PORT} 10.0.0.3 {PORT} > /tmp/churn_h1.log 2>&1 &')
    h2.cmd(f'mkdir -p /tmp && {cd_cmd} {python_cmd} -u {script_to_use} 10.0.0.2 {PORT} 10.0.0.1 {PORT} 10.0.0.3 {PORT} 10.0.0.4 {PORT} > /tmp/churn_h2.log 2>&1 &')
    h3.cmd(f'mkdir -p /tmp && {cd_cmd} {python_cmd} -u {script_to_use} 10.0.0.3 {PORT} 10.0.0.1 {PORT} 10.0.0.2 {PORT} 10.0.0.4 {PORT} 10.0.0.5 {PORT} > /tmp/churn_h3.log 2>&1 &')
    h4.cmd(f'mkdir -p /tmp && {cd_cmd} {python_cmd} -u {script_to_use} 10.0.0.4 {PORT} 10.0.0.2 {PORT} 10.0.0.3 {PORT} 10.0.0.5 {PORT} > /tmp/churn_h4.log 2>&1 &')
    h5.cmd(f'mkdir -p /tmp && {cd_cmd} {python_cmd} -u {script_to_use} 10.0.0.5 {PORT} 10.0.0.3 {PORT} 10.0.0.4 {PORT} > /tmp/churn_h5.log 2>&1 &')
    
    # Wait and verify logs are being created
    time.sleep(2)
    print("\n--- Checking log files ---")
    for host, name in [(h1, 'churn_h1'), (h2, 'churn_h2'), (h3, 'churn_h3'), (h4, 'churn_h4'), (h5, 'churn_h5')]:
        result = host.cmd(f'test -f /tmp/{name}.log && echo "EXISTS" || echo "MISSING"')
        status = "✓" if "EXISTS" in result else "✗"
        size = host.cmd(f'wc -c < /tmp/{name}.log 2>/dev/null || echo "0"').strip()
        print(f"  {status} {name}.log ({size} bytes)")
    
    print("\n--- Phase 1: Let rumor propagate (10 seconds) ---")
    print("Waiting for rumor to start spreading from h1...")
    time.sleep(10)  # Give rumor time to propagate to some nodes
    
    # Check if rumor has reached any nodes before churn
    print("\n--- Checking rumor propagation before churn ---")
    rumor_reached_before = {}
    for host, name in [(h2, 'h2'), (h3, 'h3'), (h4, 'h4'), (h5, 'h5')]:
        log_content = host.cmd('cat /tmp/churn_' + name + '.log 2>/dev/null || echo ""')
        rumor_reached_before[name] = 'NEW RUMOR' in log_content or 'RUMOR_001' in log_content
        status = "✓" if rumor_reached_before[name] else "✗"
        print(f"  {status} {name} received rumor: {rumor_reached_before[name]}")
    
    print("\n🔥 SIMULATING CHURN: Killing node h3 (central hub)")
    print("   h3 connects to: h1, h2, h4, h5 - killing it should test resilience")
    h3.cmd("pkill -f gossip_agent.py")
    print("⚠️  Node h3 is DOWN!\n")
    
    print("--- Phase 2: Gossip continues after churn (20 seconds) ---")
    print("Waiting to see if gossip continues despite h3 failure...")
    time.sleep(20)
    
    print("\n" + "="*70)
    print("CHURN TEST RESULTS")
    print("="*70)
    
    # Automatically check results
    print("\n--- Checking final rumor propagation ---")
    final_results = {}
    for host, name in [(h1, 'h1'), (h2, 'h2'), (h4, 'h4'), (h5, 'h5')]:
        log_content = host.cmd('cat /tmp/churn_' + name + '.log 2>/dev/null || echo ""')
        received_rumor = 'NEW RUMOR' in log_content or 'RUMOR_001' in log_content
        final_results[name] = received_rumor
        
        # Check for churn detection (failed sends)
        failed_sends = log_content.count("couldn't send") + log_content.count("Churn detected")
        
        status = "✓" if received_rumor else "✗"
        churn_info = f" ({failed_sends} churn events)" if failed_sends > 0 else ""
        print(f"  {status} {name}: {'Received rumor' if received_rumor else 'Did NOT receive rumor'}{churn_info}")
    
    # Summary
    print("\n--- Test Summary ---")
    nodes_received = sum(1 for v in final_results.values() if v)
    total_nodes = len(final_results)
    print(f"Nodes that received rumor: {nodes_received}/{total_nodes}")
    
    if nodes_received == total_nodes:
        print("✅ SUCCESS: All remaining nodes received the rumor despite h3 failure!")
    elif nodes_received > 0:
        print("⚠️  PARTIAL: Some nodes received the rumor. Check connectivity.")
    else:
        print("❌ FAILURE: No nodes received the rumor after churn.")
    
    print("\n--- Manual inspection commands ---")
    print("  h4 cat /tmp/churn_h4.log | grep -E '(NEW RUMOR|Churn detected|couldn't send)'")
    print("  h5 cat /tmp/churn_h5.log | grep -E '(NEW RUMOR|Churn detected|couldn't send)'")
    print("\n")
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    test_churn()