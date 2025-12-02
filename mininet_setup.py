import os
import time
from mininet.net import Mininet
from mininet.cli import CLI

def start_gossip_network():
    # NO CONTROLLER
    net = Mininet(controller=None) 

    print("--- 1. Creating Hosts and Switch ---")
    
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    h3 = net.addHost('h3', ip='10.0.0.3')
    h4 = net.addHost('h4', ip='10.0.0.4')
    h5 = net.addHost('h5', ip='10.0.0.5')
    
    s1 = net.addSwitch('s1') 

    print("--- 2. Creating Links ---")
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)
    net.addLink(h4, s1)
    net.addLink(h5, s1)

    print("--- 3. Starting Network ---")
    net.start()
    
    # Configure switch to forward all traffic
    s1.cmd('ovs-ofctl add-flow s1 action=normal')

    # Get the absolute path to the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, 'gossip_agent.py')
    
    # Use python3 (Mininet hosts usually have it in PATH)
    python_cmd = 'python3'
    
    PORT = 8000
    
    print("--- 4. Starting Gossip Agents ---")
    print(f"Script directory: {script_dir}")
    print(f"Script path: {script_path}")
    
    # Copy script to each host's home directory to ensure it's accessible
    # This is more reliable than relying on shared filesystem
    print("Copying script to each host...")
    script_to_use = '~/gossip_agent.py'  # Default to copied version
    
    for i, host in enumerate([h1, h2, h3, h4, h5], 1):
        result = host.cmd(f'cp {script_path} ~/gossip_agent.py 2>&1')
        # Verify copy worked
        check = host.cmd('test -f ~/gossip_agent.py && echo "OK" || echo "FAIL"')
        if "OK" not in check:
            print(f"  ⚠ Warning: Script copy to h{i} may have failed")
            # Try alternative: use script_path directly (if accessible from VM)
            print(f"  Trying direct path: {script_path}")
            alt_check = host.cmd(f'test -f {script_path} && echo "OK" || echo "FAIL"')
            if "OK" in alt_check:
                script_to_use = script_path
                print(f"  ✓ Using direct path instead")
            else:
                print(f"  ✗ ERROR: Script not accessible on h{i}!")
                print(f"     Make sure gossip_agent.py is in: {script_dir}")
    
    print(f"Using script: {script_to_use}")
    
    # Use unbuffered output (-u flag) and ensure /tmp exists
    # Change to appropriate directory
    print("Starting agents...")
    if script_to_use.startswith('~'):
        cd_cmd = 'cd ~ &&'
    else:
        cd_cmd = f'cd {script_dir} &&'
    
    h1.cmd(f'mkdir -p /tmp && {cd_cmd} {python_cmd} -u {script_to_use} 10.0.0.1 {PORT} 10.0.0.2 {PORT} 10.0.0.3 {PORT} > /tmp/h1.log 2>&1 &')
    h2.cmd(f'mkdir -p /tmp && {cd_cmd} {python_cmd} -u {script_to_use} 10.0.0.2 {PORT} 10.0.0.1 {PORT} 10.0.0.3 {PORT} 10.0.0.4 {PORT} > /tmp/h2.log 2>&1 &')
    h3.cmd(f'mkdir -p /tmp && {cd_cmd} {python_cmd} -u {script_to_use} 10.0.0.3 {PORT} 10.0.0.1 {PORT} 10.0.0.2 {PORT} 10.0.0.4 {PORT} 10.0.0.5 {PORT} > /tmp/h3.log 2>&1 &')
    h4.cmd(f'mkdir -p /tmp && {cd_cmd} {python_cmd} -u {script_to_use} 10.0.0.4 {PORT} 10.0.0.2 {PORT} 10.0.0.3 {PORT} 10.0.0.5 {PORT} > /tmp/h4.log 2>&1 &')
    h5.cmd(f'mkdir -p /tmp && {cd_cmd} {python_cmd} -u {script_to_use} 10.0.0.5 {PORT} 10.0.0.3 {PORT} 10.0.0.4 {PORT} > /tmp/h5.log 2>&1 &')
    
    # Wait a moment and verify logs are being created
    time.sleep(2)
    
    print("\n--- Checking log files ---")
    for host, name in [(h1, 'h1'), (h2, 'h2'), (h3, 'h3'), (h4, 'h4'), (h5, 'h5')]:
        result = host.cmd(f'test -f /tmp/{name}.log && echo "EXISTS" || echo "MISSING"')
        status = "✓" if "EXISTS" in result else "✗"
        size = host.cmd(f'wc -c < /tmp/{name}.log 2>/dev/null || echo "0"').strip()
        print(f"  {status} {name}.log ({size} bytes)")
    
    print("\n=== WAIT 30 SECONDS, then type 'exit' ===\n")
    print("To view logs, use: h1 cat /tmp/h1.log (or h2, h3, etc.)\n")
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    start_gossip_network()