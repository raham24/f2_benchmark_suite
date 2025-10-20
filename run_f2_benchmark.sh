#!/bin/bash

# AWS EC2 F2 Instance FPGA Benchmark Runner
# This script sets up the environment and runs the F2 FPGA benchmark

echo "AWS EC2 F2 Instance FPGA Benchmark Runner"
echo "========================================"

# Check if running on AWS EC2
if command -v curl >/dev/null 2>&1; then
    echo "Checking instance metadata..."
    INSTANCE_TYPE=$(curl -s http://169.254.169.254/latest/meta-data/instance-type 2>/dev/null || echo "unknown")
    INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id 2>/dev/null || echo "unknown")
    AZ=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone 2>/dev/null || echo "unknown")
    
    echo "Instance Type: $INSTANCE_TYPE"
    echo "Instance ID: $INSTANCE_ID"
    echo "Availability Zone: $AZ"
    echo ""
fi

# Check Python dependencies
echo "Checking Python dependencies..."
python3 -c "import numpy, psutil, threading, queue, json, time" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ All Python dependencies available"
else
    echo "⚠ Installing missing Python dependencies..."
    pip3 install numpy psutil --user
fi

# Check system resources
echo ""
echo "System Resources:"
echo "CPU Cores: $(nproc)"
echo "Memory: $(free -h | grep ^Mem | awk '{print $2}')"
echo "Storage: $(df -h / | tail -1 | awk '{print $4}' | sed 's/G/ GB/')"

# Check for FPGA development tools (optional)
echo ""
echo "FPGA Development Environment:"
if command -v vivado >/dev/null 2>&1; then
    echo "✓ Xilinx Vivado found: $(vivado -version 2>/dev/null | head -1)"
else
    echo "⚠ Xilinx Vivado not found (optional for benchmark)"
fi

if [ -d "/opt/xilinx" ]; then
    echo "✓ Xilinx tools directory found"
else
    echo "⚠ Xilinx tools directory not found (optional for benchmark)"
fi

# Set up benchmark environment
echo ""
echo "Setting up benchmark environment..."
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export OMP_NUM_THREADS=$(nproc)

# Create output directory
mkdir -p benchmark_results
cd benchmark_results

# Run the benchmark
echo ""
echo "Starting F2 FPGA Benchmark..."
echo "========================================"
python3 ../f2_fpga_benchmark.py

# Check if benchmark completed successfully
if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Benchmark completed successfully"
    
    # Display results summary
    if [ -f "f2_benchmark_results.json" ]; then
        echo ""
        echo "Results Summary:"
        echo "==============="
        python3 -c "
import json
with open('f2_benchmark_results.json', 'r') as f:
    data = json.load(f)
    summary = data['performance_summary']
    print(f'Peak Memory Bandwidth: {summary[\"peak_memory_bandwidth_gbps\"]:.2f} GB/s')
    print(f'Peak PCIe Throughput: {summary[\"peak_pcie_throughput_gbps\"]:.2f} GB/s')
    print(f'Peak Operations/sec: {summary[\"peak_ops_per_second\"]:,.0f}')
    print(f'Aggregate Parallel GOPS: {summary[\"aggregate_parallel_gops\"]:.4f}')
"
    fi
    
    # Move results to timestamped file
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    if [ -f "f2_benchmark_results.json" ]; then
        cp f2_benchmark_results.json "f2_benchmark_${TIMESTAMP}.json"
        echo "Results archived as: f2_benchmark_${TIMESTAMP}.json"
    fi
    
else
    echo "✗ Benchmark failed"
    exit 1
fi

echo ""
echo "Benchmark run completed at $(date)"