import re
import os

def analyze_latency():
    """Analyze latency test results from log files"""
    print("LATENCY TEST RESULTS\n")
    
    nodes = {
        'h1': {'delay': '50ms', 'loss': '0%'},
        'h2': {'delay': '10ms', 'loss': '0%'},
        'h3': {'delay': '100ms', 'loss': '2%'},
        'h4': {'delay': '20ms', 'loss': '0%'},
        'h5': {'delay': '5ms', 'loss': '0%'}
    }
    
    results = {}
    
    for node_name in nodes.keys():
        log_file = f'/tmp/lat_{node_name}.log'
        try:
            with open(log_file, 'r') as f:
                log_content = f.read()
        except FileNotFoundError:
            log_content = ""
        
        received = 'NEW RUMOR' in log_content or 'RUMOR_001' in log_content
        time_match = re.search(r'Time: ([\d.]+)s', log_content)
        receive_time = float(time_match.group(1)) if time_match else None
        
        metrics_lines = re.findall(r'Sent: (\d+), Failed: (\d+)', log_content)
        if metrics_lines:
            sent, failed = metrics_lines[-1]
            sent = int(sent)
            failed = int(failed)
        else:
            sent = 0
            failed = 0
        
        results[node_name] = {
            'received': received,
            'time': receive_time,
            'sent': sent,
            'failed': failed,
            'delay': nodes[node_name]['delay'],
            'loss': nodes[node_name]['loss']
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
    print(f"Total Messages Sent: {total_sent}")
    print(f"Total Failed: {total_failed}")
    print(f"Convergence Time: {max_time:.2f}s")
    print(f"High-latency node (h3, 100ms) received: {'✓ Yes' if results['h3']['received'] else '✗ No'}")
    
    if results['h3']['time']:
        print(f"  → h3 received at: {results['h3']['time']:.2f}s (delayed by network latency)")
    print()

if __name__ == '__main__':
    analyze_latency()