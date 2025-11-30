import os
import time

def analyze():
    print("\n" + "="*60)
    print("GOSSIP PROTOCOL RESULTS")
    print("="*60 + "\n")
    
    nodes = ['10_0_0_1', '10_0_0_2', '10_0_0_3', '10_0_0_4', '10_0_0_5']
    
    seed_time = None
    received_times = {}
    total_messages = 0
    
    for node in nodes:
        filepath = f'/tmp/metrics_{node}.txt'
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if parts[0] == 'SEED':
                        seed_time = float(parts[2])
                    elif parts[0] == 'RECEIVED':
                        received_times[node] = float(parts[2])
                    elif parts[0] == 'SENT':
                        total_messages += 1
    
    print(f"Total nodes: 5")
    print(f"Nodes that received rumor: {len(received_times)}")
    print(f"Total messages sent: {total_messages}")
    
    if seed_time and received_times:
        print(f"\nConvergence times (from seed):")
        for node, recv_time in sorted(received_times.items()):
            delay = recv_time - seed_time
            print(f"  Node {node.replace('_', '.')}: {delay:.3f}s")
        
        max_time = max(received_times.values()) - seed_time
        print(f"\nTotal convergence time: {max_time:.3f}s")
    
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    analyze()
