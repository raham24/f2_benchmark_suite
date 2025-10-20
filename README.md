# AWS EC2 F2 Instance FPGA Benchmark Suite

Comprehensive benchmarking tools for testing throughput and operations per second on AWS EC2 F2 instances.

## Overview

This benchmark suite is designed to measure the performance characteristics of AWS EC2 F2 instances, specifically focusing on:
- **CPU-FPGA communication throughput**
- **FPGA operations per second**
- **Memory bandwidth simulation**
- **Parallel FPGA workload performance**

## F2 Instance Target Specifications

- **FPGAs**: Up to 8 AMD Virtex UltraScale+ HBM VU47P FPGAs
- **Memory**: 16GB HBM per FPGA (460 GiB/s bandwidth)
- **DSP Performance**: Up to 28 TOPS INT8 per FPGA
- **System**: 192 vCPU, 2 TiB memory, 7.6 TiB NVMe SSD
- **Network**: 100 Gbps bandwidth

## Files in This Suite

### Core Benchmark Tools

1. **f2_fpga_benchmark.py** - Main benchmark suite
   - Comprehensive performance testing
   - Memory bandwidth simulation
   - PCIe throughput measurement
   - Operations per second testing
   - Parallel FPGA simulation

2. **run_f2_benchmark.sh** - Automated benchmark runner
   - Environment setup and validation
   - Dependency checking
   - Instance metadata detection
   - Result archiving with timestamps

3. **fpga_throughput_monitor.py** - Real-time monitoring
   - Continuous performance tracking
   - System resource monitoring
   - Sustained throughput measurement
   - Efficiency metrics calculation

### Documentation

4. **logs.txt** - Complete research and implementation log
   - Research findings and methodology
   - Implementation details and design decisions
   - Usage instructions and troubleshooting

5. **README.md** - This file

## Quick Start

### 1. Basic Benchmark Run
```bash
chmod +x run_f2_benchmark.sh
./run_f2_benchmark.sh
```

### 2. Python-only Execution
```bash
python3 f2_fpga_benchmark.py
```

### 3. Real-time Monitoring
```bash
python3 fpga_throughput_monitor.py
```

## Expected Performance Metrics

Based on AWS F2 specifications and research:

- **Memory Bandwidth**: Up to 460 GiB/s per FPGA (HBM)
- **PCIe Throughput**: 7+ GB/s (optimized DMA)
- **Operations/Second**: Millions to billions depending on operation type
- **Aggregate Performance**: 10+ GOPS across 8 FPGAs

## Dependencies

### Python Libraries
- numpy (numerical operations)
- psutil (system monitoring)
- threading (parallel execution)
- json (results output)
- time (performance timing)

### System Requirements
- AWS EC2 F2 instance (recommended: f2.48xlarge)
- Python 3.6+
- Sufficient memory for test data arrays

## Results Output

All benchmarks generate JSON files with detailed metrics:
- Performance summaries
- Individual test results
- System resource utilization
- Timestamped data for comparison

## Important Notes

1. **Simulation-based**: These benchmarks simulate FPGA operations using CPU
2. **Indicative Results**: Actual FPGA performance depends on custom logic implementation
3. **Hardware Requirements**: Real FPGA benchmarks require AWS FPGA Development Kit
4. **Validation**: Results should be compared against AWS specifications and cl_mem_perf

## Troubleshooting

- Ensure all Python dependencies are installed
- Run with sufficient system memory
- Check logs.txt for detailed implementation information
- Verify F2 instance type for optimal results

## Future Enhancements

- Integration with AWS FPGA Development Kit
- Network throughput testing (DPDK)
- Power consumption monitoring
- Multi-instance distributed testing

---

**Created**: October 20, 2025  
**Target Platform**: AWS EC2 F2 Instances  
**Status**: Ready for deployment and testing