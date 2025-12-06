import re

def analyze_churn():
    """Analyze churn test results from log files"""
    print("CHURN TEST RESULTS\n")
    
    nodes = ['h1', 'h2', 'h3', 'h4', 'h5']
    results = {}
    
    for node_name in nodes:
        log_file = f'/tmp/churn_{node_name}.log'
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
        
        # Count churn events (failed sends)
        churn_events = log_content.count("couldn't send") + log_content.count("Churn detected")
        
        # Check if node was killed (h3)
        is_killed = node_name == 'h3'
        
        results[node_name] = {
            'received': received,
            'time': receive_time,
            'sent': sent,
            'failed': failed,
            'churn_events': churn_events,
            'is_killed': is_killed
        }
    
    print(f"{'Node':<6} {'Status':<12} {'Received':<12} {'Time(s)':<10} {'Sent':<8} {'Failed':<8} {'Churn Events':<12}")
    print("-" * 80)
    
    for node in sorted(results.keys()):
        data = results[node]
        status = "KILLED" if data['is_killed'] else "ALIVE"
        received_str = "✓ Yes" if data['received'] else "✗ No"
        time_str = f"{data['time']:.2f}" if data['time'] else "N/A"
        print(f"{node:<6} {status:<12} {received_str:<12} {time_str:<10} {data['sent']:<8} {data['failed']:<8} {data['churn_events']:<12}")
    
    # Analyze remaining nodes (excluding h3 which was killed)
    remaining_nodes = {k: v for k, v in results.items() if not v['is_killed']}
    coverage = sum(1 for r in remaining_nodes.values() if r['received'])
    total_nodes = len(remaining_nodes)
    total_sent = sum(r['sent'] for r in remaining_nodes.values())
    total_failed = sum(r['failed'] for r in remaining_nodes.values())
    total_churn = sum(r['churn_events'] for r in remaining_nodes.values())
    
    times = [r['time'] for r in remaining_nodes.values() if r['time'] is not None]
    max_time = max(times) if times else 0
    
    print("-" * 80)
    print(f"\nRemaining Nodes (after h3 failure): {total_nodes}")
    print(f"Coverage: {coverage}/{total_nodes} nodes received rumor ({coverage/total_nodes*100:.0f}%)")
    print(f"Total Messages: {total_sent} sent, {total_failed} failed")
    print(f"Total Churn Events: {total_churn}")
    print(f"Convergence Time: {max_time:.2f}s")
    
    if coverage == total_nodes:
        print("SUCCESS: All remaining nodes received rumor despite h3 failure")
    elif coverage > 0:
        print("PARTIAL: Some nodes received rumor after churn")
    else:
        print("FAILURE: No nodes received rumor after churn")
    
    # Show which nodes received rumor after churn
    received_after = [node for node, data in remaining_nodes.items() if data['received']]
    if received_after:
        print(f"Nodes that received rumor: {', '.join(received_after)}")
    print()

if __name__ == '__main__':
    analyze_churn()

