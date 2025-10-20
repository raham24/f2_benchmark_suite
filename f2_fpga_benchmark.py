#!/usr/bin/env python3
"""
AWS EC2 F2 Instance FPGA Benchmark Suite
Measures throughput and operations per second for FPGA performance testing

Based on research from AWS FPGA Development Kit and performance studies
"""

import time
import numpy as np
import os
import subprocess
import json
import psutil
from typing import Dict, List, Tuple
import threading
import queue

class F2FPGABenchmark:
    """
    Comprehensive benchmark suite for AWS EC2 F2 FPGA instances
    Tests CPU-FPGA communication throughput and operations per second
    """
    
    def __init__(self):
        self.results = {}
        self.instance_info = self._get_instance_info()
        self.fpga_count = 8  # F2 instances have up to 8 FPGAs
        
    def _get_instance_info(self) -> Dict:
        """Get EC2 instance information"""
        try:
            # Get CPU info
            cpu_count = psutil.cpu_count()
            memory_gb = psutil.virtual_memory().total / (1024**3)
            
            # Check if running on F2 instance
            instance_type = "f2.48xlarge"  # Default assumption
            
            return {
                "instance_type": instance_type,
                "cpu_count": cpu_count,
                "memory_gb": round(memory_gb, 2),
                "fpga_count": self.fpga_count
            }
        except Exception as e:
            return {"error": str(e), "cpu_count": 0, "memory_gb": 0}
    
    def test_memory_bandwidth(self, data_size_mb: int = 1024) -> Dict:
        """
        Test memory bandwidth to simulate FPGA HBM access patterns
        F2 instances have 16GB HBM per FPGA with up to 460 GiB/s bandwidth
        """
        print(f"Testing memory bandwidth with {data_size_mb}MB data...")
        
        # Create test data
        data_size = data_size_mb * 1024 * 1024  # Convert to bytes
        test_data = np.random.randint(0, 255, data_size, dtype=np.uint8)
        
        results = {}
        
        # Sequential read test
        start_time = time.time()
        for _ in range(10):
            _ = test_data.sum()
        end_time = time.time()
        
        read_time = (end_time - start_time) / 10
        read_bandwidth_gbps = (data_size / read_time) / (1024**3)
        
        # Sequential write test
        write_data = np.zeros_like(test_data)
        start_time = time.time()
        for i in range(10):
            write_data[:] = test_data
        end_time = time.time()
        
        write_time = (end_time - start_time) / 10
        write_bandwidth_gbps = (data_size / write_time) / (1024**3)
        
        results = {
            "data_size_mb": data_size_mb,
            "read_bandwidth_gbps": round(read_bandwidth_gbps, 2),
            "write_bandwidth_gbps": round(write_bandwidth_gbps, 2),
            "read_time_sec": round(read_time, 4),
            "write_time_sec": round(write_time, 4)
        }
        
        return results
    
    def test_pcie_throughput_simulation(self, transfer_size_mb: int = 512) -> Dict:
        """
        Simulate PCIe DMA throughput testing
        Based on research showing 7+ GB/s possible with optimized DMA
        """
        print(f"Testing PCIe throughput simulation with {transfer_size_mb}MB transfers...")
        
        transfer_size = transfer_size_mb * 1024 * 1024
        
        # Simulate host-to-FPGA transfers
        host_data = np.random.randint(0, 65535, transfer_size // 2, dtype=np.uint16)
        fpga_buffer = np.zeros_like(host_data)
        
        # Test multiple transfer patterns
        results = {}
        
        # Single large transfer
        start_time = time.time()
        fpga_buffer[:] = host_data
        end_time = time.time()
        
        single_transfer_time = end_time - start_time
        single_throughput_gbps = (transfer_size / single_transfer_time) / (1024**3)
        
        # Multiple smaller transfers (simulating scatter-gather DMA)
        chunk_size = transfer_size // 64  # 64 chunks
        start_time = time.time()
        for i in range(0, len(host_data), chunk_size // 2):
            end_idx = min(i + chunk_size // 2, len(host_data))
            fpga_buffer[i:end_idx] = host_data[i:end_idx]
        end_time = time.time()
        
        multi_transfer_time = end_time - start_time
        multi_throughput_gbps = (transfer_size / multi_transfer_time) / (1024**3)
        
        results = {
            "transfer_size_mb": transfer_size_mb,
            "single_transfer_gbps": round(single_throughput_gbps, 2),
            "multi_transfer_gbps": round(multi_throughput_gbps, 2),
            "single_transfer_time_sec": round(single_transfer_time, 4),
            "multi_transfer_time_sec": round(multi_transfer_time, 4)
        }
        
        return results
    
    def test_operations_per_second(self, operation_type: str = "multiply_add") -> Dict:
        """
        Test operations per second for different FPGA-style computations
        F2 FPGAs have 9,024 DSP slices with up to 28 TOPS INT8 performance
        """
        print(f"Testing {operation_type} operations per second...")
        
        # Create test data sized for FPGA-style processing
        data_size = 1024 * 1024  # 1M operations
        
        if operation_type == "multiply_add":
            a = np.random.randint(0, 255, data_size, dtype=np.int16)
            b = np.random.randint(0, 255, data_size, dtype=np.int16)
            c = np.random.randint(0, 255, data_size, dtype=np.int16)
            
            # Time the operations
            start_time = time.time()
            for _ in range(100):  # 100 iterations
                result = a * b + c
            end_time = time.time()
            
            total_ops = data_size * 100 * 2  # multiply + add = 2 ops per element
            
        elif operation_type == "vector_sum":
            vectors = [np.random.randint(0, 255, data_size, dtype=np.int32) for _ in range(8)]
            
            start_time = time.time()
            for _ in range(100):
                result = sum(vectors)
            end_time = time.time()
            
            total_ops = data_size * 100 * 7  # 7 additions per element
            
        elif operation_type == "bitwise_ops":
            a = np.random.randint(0, 65535, data_size, dtype=np.uint16)
            b = np.random.randint(0, 65535, data_size, dtype=np.uint16)
            
            start_time = time.time()
            for _ in range(100):
                result = (a ^ b) & (a | b)
            end_time = time.time()
            
            total_ops = data_size * 100 * 3  # XOR + AND + OR = 3 ops per element
        
        else:
            raise ValueError(f"Unknown operation type: {operation_type}")
        
        elapsed_time = end_time - start_time
        ops_per_second = total_ops / elapsed_time
        
        results = {
            "operation_type": operation_type,
            "data_size": data_size,
            "iterations": 100,
            "total_operations": total_ops,
            "elapsed_time_sec": round(elapsed_time, 4),
            "ops_per_second": round(ops_per_second, 0),
            "mega_ops_per_second": round(ops_per_second / 1e6, 2),
            "giga_ops_per_second": round(ops_per_second / 1e9, 4)
        }
        
        return results
    
    def test_parallel_fpga_simulation(self) -> Dict:
        """
        Simulate parallel FPGA workload across multiple FPGAs
        F2.48xlarge has 8 FPGAs that can work in parallel
        """
        print("Testing parallel FPGA simulation...")
        
        def fpga_worker(fpga_id: int, result_queue: queue.Queue):
            """Simulate work on a single FPGA"""
            data_size = 512 * 1024  # 512K operations per FPGA
            a = np.random.randint(0, 255, data_size, dtype=np.int16)
            b = np.random.randint(0, 255, data_size, dtype=np.int16)
            
            start_time = time.time()
            for _ in range(50):
                result = np.sum(a * b)
            end_time = time.time()
            
            ops_performed = data_size * 50 * 2  # multiply + sum
            elapsed = end_time - start_time
            ops_per_sec = ops_performed / elapsed
            
            result_queue.put({
                "fpga_id": fpga_id,
                "ops_performed": ops_performed,
                "elapsed_time": elapsed,
                "ops_per_second": ops_per_sec
            })
        
        # Start parallel workers
        result_queue = queue.Queue()
        threads = []
        
        start_time = time.time()
        for fpga_id in range(self.fpga_count):
            thread = threading.Thread(target=fpga_worker, args=(fpga_id, result_queue))
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        end_time = time.time()
        
        # Collect results
        fpga_results = []
        total_ops = 0
        for _ in range(self.fpga_count):
            result = result_queue.get()
            fpga_results.append(result)
            total_ops += result["ops_performed"]
        
        total_time = end_time - start_time
        aggregate_ops_per_sec = total_ops / total_time
        
        results = {
            "fpga_count": self.fpga_count,
            "total_operations": total_ops,
            "total_time_sec": round(total_time, 4),
            "aggregate_ops_per_second": round(aggregate_ops_per_sec, 0),
            "aggregate_gops_per_second": round(aggregate_ops_per_sec / 1e9, 4),
            "individual_fpga_results": fpga_results
        }
        
        return results
    
    def run_full_benchmark(self) -> Dict:
        """Run complete benchmark suite"""
        print("Starting AWS EC2 F2 FPGA Benchmark Suite")
        print("=" * 50)
        
        benchmark_start = time.time()
        
        # Run all benchmark tests
        print("\n1. Memory Bandwidth Tests")
        memory_results = self.test_memory_bandwidth(1024)
        
        print("\n2. PCIe Throughput Tests")
        pcie_results = self.test_pcie_throughput_simulation(512)
        
        print("\n3. Operations Per Second Tests")
        ops_multiply_add = self.test_operations_per_second("multiply_add")
        ops_vector_sum = self.test_operations_per_second("vector_sum")
        ops_bitwise = self.test_operations_per_second("bitwise_ops")
        
        print("\n4. Parallel FPGA Simulation")
        parallel_results = self.test_parallel_fpga_simulation()
        
        benchmark_end = time.time()
        
        # Compile final results
        final_results = {
            "benchmark_info": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_benchmark_time": round(benchmark_end - benchmark_start, 2),
                "instance_info": self.instance_info
            },
            "memory_bandwidth": memory_results,
            "pcie_throughput": pcie_results,
            "operations_per_second": {
                "multiply_add": ops_multiply_add,
                "vector_sum": ops_vector_sum,
                "bitwise_operations": ops_bitwise
            },
            "parallel_fpga_simulation": parallel_results,
            "performance_summary": {
                "peak_memory_bandwidth_gbps": max(memory_results["read_bandwidth_gbps"], 
                                                 memory_results["write_bandwidth_gbps"]),
                "peak_pcie_throughput_gbps": max(pcie_results["single_transfer_gbps"],
                                               pcie_results["multi_transfer_gbps"]),
                "peak_ops_per_second": max(ops_multiply_add["ops_per_second"],
                                         ops_vector_sum["ops_per_second"],
                                         ops_bitwise["ops_per_second"]),
                "aggregate_parallel_gops": parallel_results["aggregate_gops_per_second"]
            }
        }
        
        return final_results
    
    def save_results(self, results: Dict, filename: str = "f2_benchmark_results.json"):
        """Save benchmark results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {filename}")

def main():
    """Main benchmark execution"""
    benchmark = F2FPGABenchmark()
    
    print("AWS EC2 F2 Instance FPGA Benchmark Suite")
    print("=" * 50)
    print(f"Instance Info: {benchmark.instance_info}")
    print("=" * 50)
    
    # Run full benchmark
    results = benchmark.run_full_benchmark()
    
    # Display summary
    print("\n" + "=" * 50)
    print("BENCHMARK SUMMARY")
    print("=" * 50)
    summary = results["performance_summary"]
    print(f"Peak Memory Bandwidth: {summary['peak_memory_bandwidth_gbps']:.2f} GB/s")
    print(f"Peak PCIe Throughput: {summary['peak_pcie_throughput_gbps']:.2f} GB/s")
    print(f"Peak Operations/sec: {summary['peak_ops_per_second']:,.0f}")
    print(f"Aggregate Parallel GOPS: {summary['aggregate_parallel_gops']:.4f}")
    
    # Save results
    benchmark.save_results(results)
    
    return results

if __name__ == "__main__":
    main()