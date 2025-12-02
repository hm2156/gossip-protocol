import os
import time
from mininet.net import Mininet
from mininet.cli import CLI

def start_gossip_network():
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

    h1.cmd(f'mkdir -p /tmp && {cd_cmd} {python_cmd} -u {script_to_use} 10.0.0.1 {PORT} 10.0.0.2 {PORT} 10.0.0.3 {PORT} > /tmp/h1.log 2>&1 &')
    h2.cmd(f'mkdir -p /tmp && {cd_cmd} {python_cmd} -u {script_to_use} 10.0.0.2 {PORT} 10.0.0.1 {PORT} 10.0.0.3 {PORT} 10.0.0.4 {PORT} > /tmp/h2.log 2>&1 &')
    h3.cmd(f'mkdir -p /tmp && {cd_cmd} {python_cmd} -u {script_to_use} 10.0.0.3 {PORT} 10.0.0.1 {PORT} 10.0.0.2 {PORT} 10.0.0.4 {PORT} 10.0.0.5 {PORT} > /tmp/h3.log 2>&1 &')
    h4.cmd(f'mkdir -p /tmp && {cd_cmd} {python_cmd} -u {script_to_use} 10.0.0.4 {PORT} 10.0.0.2 {PORT} 10.0.0.3 {PORT} 10.0.0.5 {PORT} > /tmp/h4.log 2>&1 &')
    h5.cmd(f'mkdir -p /tmp && {cd_cmd} {python_cmd} -u {script_to_use} 10.0.0.5 {PORT} 10.0.0.3 {PORT} 10.0.0.4 {PORT} > /tmp/h5.log 2>&1 &')

    time.sleep(2)
    print("Gossip network started. Agents running on h1-h5.")
    print("Logs: /tmp/h1.log through /tmp/h5.log")
    print("Type 'exit' to stop.\n")
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    start_gossip_network()