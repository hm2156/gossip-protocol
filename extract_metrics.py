import re
import sys

def extract_from_log(log_file):
    """Extract metrics from a single log file"""
    try:
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Check if node received rumor
        received = 'NEW RUMOR' in content
        
        # Extract time if received
        time_match = re.search(r'Time: ([\d.]+)s', content)
        receive_time = float(time_match.group(1)) if time_match else None
        
        # Extract last metrics line
        metrics_lines = re.findall(r'Sent: (\d+), Failed: (\d+)', content)
        if metrics_lines:
            last_sent, last_failed = metrics_lines[-1]
            sent = int(last_sent)
            failed = int(last_failed)
        else:
            sent = 0
            failed = 0
        
        return {
            'received': received,
            'time': receive_time,
            'sent': sent,
            'failed': failed
        }
    except FileNotFoundError:
        return {'received': False, 'time': None, 'sent': 0, 'failed': 0}

def analyze_experiment():
    """Analyze all 5 node logs"""
    print("\n" + "="*60)
    print("EXTRACTING METRICS FROM LOGS")
    print("="*60 + "\n")
    
    nodes = ['h1', 'h2', 'h3', 'h4', 'h5']
    results = {}
    
    for node in nodes:
        log_file = f'/tmp/{node}.log'
        print(f"Reading {log_file}...")
        results[node] = extract_from_log(log_file)
    
    # Calculate totals
    coverage = sum(1 for r in results.values() if r['received'])
    total_sent = sum(r['sent'] for r in results.values())
    total_failed = sum(r['failed'] for r in results.values())
    
    # Find max convergence time
    times = [r['time'] for r in results.values() if r['time'] is not None]
    max_time = max(times) if times else 0
    
    # Display results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    
    print(f"\n{'Node':<8} {'Received':<12} {'Time(s)':<12} {'Sent':<8} {'Failed':<8}")
    print("-" * 60)
    
    for node, data in results.items():
        received_str = "✓ Yes" if data['received'] else "✗ No"
        time_str = f"{data['time']:.2f}" if data['time'] else "N/A"
        print(f"{node:<8} {received_str:<12} {time_str:<12} {data['sent']:<8} {data['failed']:<8}")
    
    print("-" * 60)
    print(f"\nCoverage: {coverage}/5 nodes ({coverage/5*100:.0f}%)")
    print(f"Total Messages Sent: {total_sent}")
    print(f"Total Failed: {total_failed}")
    print(f"Convergence Time: {max_time:.2f}s")
    print(f"Reliability: {((total_sent-total_failed)/total_sent*100):.1f}%")
    
    print("\n" + "="*60)
    
    # Save for later comparison
    return {
        'coverage': coverage,
        'total_messages': total_sent,
        'convergence_time': max_time,
        'failed': total_failed,
        'reliability': ((total_sent-total_failed)/total_sent*100) if total_sent > 0 else 0
    }

if __name__ == '__main__':
    analyze_experiment()