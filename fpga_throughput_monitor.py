#!/usr/bin/env python3
"""
Real-time FPGA throughput monitor for AWS F2 instances
Continuous monitoring of system performance during FPGA operations
"""

import time
import psutil
import threading
import json
import numpy as np
from datetime import datetime
import os

class FPGAThroughputMonitor:
    """Real-time monitoring of FPGA throughput and system performance"""
    
    def __init__(self, monitoring_duration: int = 60):
        self.monitoring_duration = monitoring_duration
        self.is_monitoring = False
        self.metrics = []
        self.start_time = None
        
    def collect_system_metrics(self):
        """Collect system performance metrics"""
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(interval=None),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_available_gb': psutil.virtual_memory().available / (1024**3),
            'disk_io_read_mb': psutil.disk_io_counters().read_bytes / (1024**2) if psutil.disk_io_counters() else 0,
            'disk_io_write_mb': psutil.disk_io_counters().write_bytes / (1024**2) if psutil.disk_io_counters() else 0,
            'network_sent_mb': psutil.net_io_counters().bytes_sent / (1024**2),
            'network_recv_mb': psutil.net_io_counters().bytes_recv / (1024**2)
        }
    
    def simulate_fpga_workload(self, fpga_id: int, operations_per_cycle: int = 100000):
        """Simulate FPGA computational workload"""
        workload_metrics = []
        
        while self.is_monitoring:
            start_cycle = time.time()
            
            # Simulate FPGA operations (matrix multiply, convolution, etc.)
            data_size = operations_per_cycle
            a = np.random.randint(0, 255, data_size, dtype=np.int16)
            b = np.random.randint(0, 255, data_size, dtype=np.int16)
            
            # Perform operations
            result = np.sum(a * b)  # Simulates DSP operations
            
            end_cycle = time.time()
            cycle_time = end_cycle - start_cycle
            ops_per_second = operations_per_cycle / cycle_time if cycle_time > 0 else 0
            
            workload_metrics.append({
                'fpga_id': fpga_id,
                'timestamp': datetime.now().isoformat(),
                'cycle_time_ms': cycle_time * 1000,
                'operations_performed': operations_per_cycle,
                'ops_per_second': ops_per_second,
                'throughput_mops': ops_per_second / 1e6
            })
            
            # Small delay to prevent overwhelming the system
            time.sleep(0.1)
        
        return workload_metrics
    
    def monitor_throughput(self, num_fpgas: int = 8):
        """Monitor throughput across multiple simulated FPGAs"""
        print(f"Starting throughput monitoring for {num_fpgas} FPGAs...")
        print(f"Monitoring duration: {self.monitoring_duration} seconds")
        
        self.is_monitoring = True
        self.start_time = time.time()
        
        # Start FPGA workload threads
        fpga_threads = []
        fpga_results = {}
        
        for fpga_id in range(num_fpgas):
            def fpga_worker(fid):
                fpga_results[fid] = self.simulate_fpga_workload(fid)
            
            thread = threading.Thread(target=fpga_worker, args=(fpga_id,))
            thread.start()
            fpga_threads.append(thread)
        
        # Collect system metrics in main thread
        system_metrics = []
        end_time = self.start_time + self.monitoring_duration
        
        while time.time() < end_time:
            metrics = self.collect_system_metrics()
            system_metrics.append(metrics)
            time.sleep(1.0)  # Collect metrics every second
        
        # Stop monitoring
        self.is_monitoring = False
        
        # Wait for all FPGA threads to finish
        for thread in fpga_threads:
            thread.join()
        
        # Compile results
        monitoring_results = {
            'monitoring_info': {
                'duration_seconds': self.monitoring_duration,
                'num_fpgas_simulated': num_fpgas,
                'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
                'end_time': datetime.now().isoformat()
            },
            'system_metrics': system_metrics,
            'fpga_workload_metrics': fpga_results,
            'performance_analysis': self._analyze_performance(system_metrics, fpga_results)
        }
        
        return monitoring_results
    
    def _analyze_performance(self, system_metrics, fpga_results):
        """Analyze collected performance data"""
        if not system_metrics or not fpga_results:
            return {}
        
        # System performance analysis
        cpu_usage = [m['cpu_percent'] for m in system_metrics]
        memory_usage = [m['memory_percent'] for m in system_metrics]
        
        # FPGA performance analysis
        all_fpga_ops = []
        for fpga_id, metrics in fpga_results.items():
            for metric in metrics:
                all_fpga_ops.append(metric['ops_per_second'])
        
        # Calculate aggregate throughput
        total_throughput = 0
        for fpga_id, metrics in fpga_results.items():
            if metrics:
                avg_ops = np.mean([m['ops_per_second'] for m in metrics])
                total_throughput += avg_ops
        
        analysis = {
            'system_performance': {
                'avg_cpu_percent': round(np.mean(cpu_usage), 2),
                'max_cpu_percent': round(np.max(cpu_usage), 2),
                'avg_memory_percent': round(np.mean(memory_usage), 2),
                'max_memory_percent': round(np.max(memory_usage), 2)
            },
            'fpga_performance': {
                'total_aggregate_ops_per_second': round(total_throughput, 0),
                'total_aggregate_gops_per_second': round(total_throughput / 1e9, 4),
                'avg_ops_per_fpga': round(total_throughput / len(fpga_results), 0) if fpga_results else 0,
                'peak_single_fpga_ops': round(np.max(all_fpga_ops), 0) if all_fpga_ops else 0
            },
            'efficiency_metrics': {
                'ops_per_cpu_percent': round(total_throughput / np.mean(cpu_usage), 0) if np.mean(cpu_usage) > 0 else 0,
                'system_utilization_score': round((np.mean(cpu_usage) + np.mean(memory_usage)) / 2, 2)
            }
        }
        
        return analysis
    
    def save_monitoring_results(self, results, filename=None):
        """Save monitoring results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fpga_throughput_monitoring_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Monitoring results saved to {filename}")
        return filename

def main():
    """Main monitoring execution"""
    print("AWS EC2 F2 FPGA Throughput Monitor")
    print("=" * 40)
    
    # Configuration
    monitoring_duration = 60  # seconds
    num_fpgas = 8  # F2.48xlarge has 8 FPGAs
    
    monitor = FPGAThroughputMonitor(monitoring_duration)
    
    print(f"Monitoring configuration:")
    print(f"- Duration: {monitoring_duration} seconds")
    print(f"- Simulated FPGAs: {num_fpgas}")
    print(f"- Start time: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # Run monitoring
    results = monitor.monitor_throughput(num_fpgas)
    
    # Display summary
    print("\nMonitoring Complete!")
    print("=" * 40)
    analysis = results['performance_analysis']
    
    print(f"System Performance:")
    print(f"- Average CPU Usage: {analysis['system_performance']['avg_cpu_percent']:.1f}%")
    print(f"- Average Memory Usage: {analysis['system_performance']['avg_memory_percent']:.1f}%")
    
    print(f"\nFPGA Performance:")
    print(f"- Total Aggregate Ops/sec: {analysis['fpga_performance']['total_aggregate_ops_per_second']:,.0f}")
    print(f"- Total Aggregate GOPS/sec: {analysis['fpga_performance']['total_aggregate_gops_per_second']:.4f}")
    print(f"- Average per FPGA: {analysis['fpga_performance']['avg_ops_per_fpga']:,.0f} ops/sec")
    
    print(f"\nEfficiency Metrics:")
    print(f"- Ops per CPU%: {analysis['efficiency_metrics']['ops_per_cpu_percent']:,.0f}")
    print(f"- System Utilization: {analysis['efficiency_metrics']['system_utilization_score']:.1f}%")
    
    # Save results
    filename = monitor.save_monitoring_results(results)
    
    return results

if __name__ == "__main__":
    main()