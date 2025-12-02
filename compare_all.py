def compare_protocols():
    """Manual comparison after running all 3 experiments"""
    
    print("\n" + "="*70)
    print("PROTOCOL COMPARISON - Enter Your Results")
    print("="*70 + "\n")
    
    results = {}
    
    for mode in ['PUSH', 'PULL', 'HYBRID']:
        print(f"\n--- {mode} MODE (from {mode.lower()}_results.txt) ---")
        coverage = int(input("Coverage (nodes that received rumor): "))
        total_msg = int(input("Total messages sent: "))
        conv_time = float(input("Convergence time (seconds): "))
        failed = int(input("Failed messages: "))
        
        results[mode] = {
            'coverage': coverage,
            'messages': total_msg,
            'time': conv_time,
            'failed': failed,
            'reliability': ((total_msg - failed) / total_msg * 100) if total_msg > 0 else 0
        }
    
    # Display comparison
    print("\n" + "="*70)
    print("COMPARISON TABLE")
    print("="*70)
    print(f"\n{'Mode':<10} {'Coverage':<12} {'Messages':<12} {'Time(s)':<10} {'Reliability':<12}")
    print("-" * 70)
    
    for mode, data in results.items():
        print(f"{mode:<10} {data['coverage']}/5       {data['messages']:<12} "
              f"{data['time']:<10.2f} {data['reliability']:<12.1f}%")
    
    print("\n" + "="*70)
    print("WINNER BY CATEGORY")
    print("="*70)
    
    best_cov = max(results.items(), key=lambda x: x[1]['coverage'])
    best_time = min(results.items(), key=lambda x: x[1]['time'])
    best_msg = min(results.items(), key=lambda x: x[1]['messages'])
    
    print(f"\nBest Coverage: {best_cov[0]} ({best_cov[1]['coverage']}/5)")
    print(f"Fastest: {best_time[0]} ({best_time[1]['time']:.2f}s)")
    print(f"Most Efficient: {best_msg[0]} ({best_msg[1]['messages']} messages)")
    
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    compare_protocols()