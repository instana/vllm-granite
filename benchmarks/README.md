# Benchmark Results on Self-Hosted Granite with vLLM Service

## Overview

This document presents benchmark results for self-hosted Granite models using vLLM. The benchmarks were collected from vLLM monitored metrics, GPU resource utilization data from nvida-smi, and measured performance characteristics from load testings conducted through Locust framework that simulate realistic user traffic patterns.

## Hardware Configuration

- **GPU**: NVIDIA H100 
- **Storage**: PersistentVolume 100GiB
- **Cluster Configuration**: OpenShift version 4.18.1

## Models and Service Benchmarked

- [IBM Granite-3.2-8B-Instruct](https://huggingface.co/ibm-granite/granite-3.2-8b-instruct)
- [vLLM v0.8.3](https://hub.docker.com/layers/vllm/vllm-openai/v0.8.3/images/sha256-4d8d397a62c36237293a4d5e2acbf911b91b0a8552825bda69f581c5811af9ec)

## Benchmark Methodology

### Test Scenarios

- Our [Load Testing](https://github.com/instana/vllm-granite/tree/main/tests/load_tests) simulated 4-5 concurrent users sending prompt requests to the Chat Completion API endpoint, with varying prompt lengths and complexities. Each test ran for 10 minutes to ensure stable measurements.

- The following setups were used for Scalability Testing:
  - 1 deployment with 1 replica using 1 GPU.
  - 1 deployment with 2 replicas, using 1 GPU for each replica, and a shared persistent volume.

### Metrics Collected

- **Generation Throughput**: Generation Token per second
- **Resource Utilization**: Percentage of computation resources utilized
- **Latency**: Time to complete requests (p50, p90, p99, etc. percentiles)
- **Token Latency**: Time per Output Token, Time to First Token
- **Queue Time**: Ruquest queue time
- **Request Prefill and Decode Time**: Request processing time by stage

### Testing Tools

- **Load Generation**: Locust framework
- **Metrics Collection**: Prometheus, Grafana

## 1. Performance Results

### 1.1. Generation Throughput

#### With 1 replica

| Avg Prompt Throuput | Avg generation throughput | Concurrent Users |
|-------|-----------------|--------------|
| 75.3 tokens/s | 194.2 tokens/s | 5 |

#### With 2 replicas

| Replica | Avg Prompt Throuput | Avg generation throughput | Concurrent Users |
|--------------|---------------------|---------------------------|--------------|
| 1 | 55.1 tokens/s       | 74.4 tokens/s             | - |
| 2 | 13.3 tokens/s       | 18.6 tokens/s             | - |
| Total | 68.4 tokens/s     | 93.0 tokens/s             | 5 |

### 1.2. Resource Utilization

#### With 1 replica

| Avg. GPU Utilization | Peak GPU Utilization | Avg. GPU Memory Utilization | Peak GPU Memory Utilization| Total Memory |
|-----------------|----------------------|----------------------|----------------------|--------------------|
| 88% | 90% | 61% | 63% | 95830 MiB |

#### With 2 replicas, 1 GPU for each replica

| Replica | Avg. GPU Utilization | Peak GPU Utilization | Avg. GPU Memory Utilization | Peak GPU Memory Utilization | Total Memory |
|--------------|----------------------|----------------------|-----------------------------|-----------------------------|--------------------|
| 1 | 40%                  | 91%                  | 95%                         | 95%                         | 95830 MiB |
| 2 | 17%                  | 91%                  | 95%                         | 95%                         | 95830 MiB |

## 2. Load Tests Results

### 2.1. Request Statistics

| # Requests	| # Fails	| Average (ms) | Min (ms)	| Max (ms) | Average size (bytes) | # Replicas |
|--------------|--------------| --------------|--------------|--------------|--------------|----------| 
| 719	| 1 |	1681.24 |	224	| 4855 | 1178.06	| 1 |
| 783	        | 0        | 	847.25      | 	212	     | 1144     | 824.66	              | 2 |

### 2.2. Response Time Statistics

| 50%ile (ms) | 60%ile (ms) |	70%ile (ms)	| 80%ile (ms)	| 90%ile (ms) |	95%ile (ms)	| 99%ile (ms)	| 100%ile (ms) | # Replicas |
|--------------|--------------| --------------|--------------|--------------|--------------|--------------|--------------|----------| 
| 1800 | 1800 |	1800	| 1800	| 1900	| 2000	| 2200 |	4900 | 1  |
| 900         | 900         | 	910	         | 910	         | 920	        | 930	         | 1100         | 	1100        | 2 |


Reference these Locust load test reports for more details:
- [Load Test Report with 1 Replica](https://instana.github.io/vllm-granite/load_test_report.html)
- [Load Test Report with 2 Replica](https://instana.github.io/vllm-granite/load_test_report_2.html)


## 3. vLLM Production Metrics

#### With 2 replicas

![part-1](https://github.com/instana/vllm-granite/blob/main/images/grafana-scale-test_part1.png)
![part-2](https://github.com/instana/vllm-granite/blob/main/images/grafana-scale-test_part2.png)
