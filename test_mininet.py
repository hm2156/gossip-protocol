#!/usr/bin/env python3
"""
Quick test script to verify Mininet setup and log file creation.
Run this to diagnose issues before running the full simulation.
"""
import os
from mininet.net import Mininet
from mininet.cli import CLI
import time

def test_mininet():
    net = Mininet(controller=None)
    
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    s1 = net.addSwitch('s1')
    
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    
    print("Starting network...")
    net.start()
    s1.cmd('ovs-ofctl add-flow s1 action=normal')
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, 'gossip_agent.py')
    
    print(f"\nScript path: {script_path}")
    print(f"Testing on h1...")
    
    # Test 1: Check if python3 exists
    print("\n1. Testing Python3...")
    result = h1.cmd('which python3')
    print(f"   Python3 path: {result.strip()}")
    
    # Test 2: Check if script exists and is readable
    print("\n2. Testing script access...")
    h1.cmd(f'cp {script_path} ~/gossip_agent.py')
    result = h1.cmd('test -f ~/gossip_agent.py && echo "EXISTS" || echo "MISSING"')
    print(f"   Script copied: {result.strip()}")
    
    # Test 3: Try to run script with syntax check
    print("\n3. Testing script syntax...")
    result = h1.cmd('python3 -m py_compile ~/gossip_agent.py 2>&1')
    if result.strip():
        print(f"   Syntax errors: {result.strip()}")
    else:
        print("   ✓ Syntax OK")
    
    # Test 4: Check /tmp directory
    print("\n4. Testing /tmp directory...")
    result = h1.cmd('test -d /tmp && test -w /tmp && echo "WRITABLE" || echo "NOT_WRITABLE"')
    print(f"   /tmp status: {result.strip()}")
    
    # Test 5: Try to create a log file
    print("\n5. Testing log file creation...")
    h1.cmd('echo "TEST MESSAGE" > /tmp/test.log 2>&1')
    result = h1.cmd('test -f /tmp/test.log && cat /tmp/test.log || echo "FAILED"')
    print(f"   Test log content: {result.strip()}")
    
    # Test 6: Try running the script with minimal args (should fail but show errors)
    print("\n6. Testing script execution (should show error about missing args)...")
    result = h1.cmd('python3 ~/gossip_agent.py 2>&1 | head -5')
    print(f"   Error output: {result.strip()}")
    
    print("\n" + "="*60)
    print("If all tests pass, your setup should work!")
    print("Enter CLI to test manually, or type 'exit' to quit")
    print("="*60 + "\n")
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    test_mininet()

