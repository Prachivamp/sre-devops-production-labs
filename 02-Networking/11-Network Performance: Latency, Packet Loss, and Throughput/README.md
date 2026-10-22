# Lab 11: Network Performance — Latency, Packet Loss, and Throughput

## Objective

Measure network latency, test packet loss, and benchmark throughput between Docker containers. Learn how to interpret network performance signals during production incidents.

## Environment

- Docker Desktop on macOS
- Existing Docker network: `lab10-network`
- Existing HTTP backend: `lab10-backend1`
- Temporary Alpine containers for ping and iperf3
- Temporary iperf3 server and client

All tests ran within a local Docker network. These results are useful for learning the tools and interpreting metrics, but they are not a benchmark of the public internet or production infrastructure.

## 1. Measure request latency with curl

Command:

```bash
docker run --rm --network lab10-network curlimages/curl:latest \
  -sS -o /dev/null \
  -w 'DNS: %{time_namelookup}s | Connect: %{time_connect}s | First byte: %{time_starttransfer}s | Total: %{time_total}s\n' \
  http://lab10-backend1:5678
```

Observed output:

```text
DNS: 0.008123s
Connect: 0.014252s
First byte: 0.059798s
Total: 0.059847s
```

Interpretation:

- DNS lookup: approximately 8.12 ms.
- TCP connection: approximately 14.25 ms from the start of the request.
- Time to first byte: approximately 59.80 ms from the start of the request.
- Total request duration: approximately 59.85 ms.

Curl's `time_connect` and `time_starttransfer` are cumulative timings measured from the start of the transfer. They should not be added together. Here, the small gap between first-byte and total time indicates the response body completed quickly after the first byte.

## 2. Compare ten requests

Command:

```bash
for i in {1..10}; do
  docker run --rm --network lab10-network curlimages/curl:latest \
    -sS -o /dev/null \
    -w "Request $i: connect=%{time_connect}s total=%{time_total}s\n" \
    http://lab10-backend1:5678
done
```

Observed total request times:

| Request | Total time |
|---|---:|
| 1 | 50.62 ms |
| 2 | 7.55 ms |
| 3 | 9.92 ms |
| 4 | 9.25 ms |
| 5 | 4.19 ms |
| 6 | 4.58 ms |
| 7 | 4.11 ms |
| 8 | 3.63 ms |
| 9 | 1.40 ms |
| 10 | 2.55 ms |

The first request was slower than subsequent requests. Each iteration launched a new temporary curl container, so container startup, scheduling, and networking overhead can affect the measurements.

**SRE lesson:** A single request or average can hide variability. For production analysis, use sufficiently large samples and compare p50, p95, and p99 latency over a defined time window.

## 3. Test packet loss using ping

Command:

```bash
docker run --rm --network lab10-network alpine:latest sh -c \
  "apk add --no-cache iputils >/dev/null && ping -c 10 lab10-backend1"
```

Observed summary:

```text
10 packets transmitted, 10 received, 0% packet loss
rtt min/avg/max/mdev = 0.056/0.427/1.861/0.502 ms
```

Results:

- Packets transmitted: 10
- Packets received: 10
- Packet loss: 0%
- Minimum round-trip time: 0.056 ms
- Average round-trip time: 0.427 ms
- Maximum round-trip time: 1.861 ms

Interpretation:

The containers communicated successfully over `lab10-network` during this short test.

Ping measures ICMP reachability and round-trip time. It does not establish that an application is healthy or that its HTTP requests are succeeding. Zero packet loss across ten packets also does not prove that the network will never lose packets.

## 4. Benchmark throughput with iperf3

Start a temporary server:

```bash
docker run -d --rm \
  --name lab11-iperf-server \
  --network lab10-network \
  alpine:latest \
  sh -c "apk add --no-cache iperf3 >/dev/null && iperf3 -s"
```

Run the client:

```bash
docker run --rm --network lab10-network alpine:latest \
  sh -c "apk add --no-cache iperf3 >/dev/null && iperf3 -c lab11-iperf-server -t 5"
```

Observed summary:

```text
0.00-5.00 sec 29.0 GBytes 49.8 Gbits/sec 2 sender
0.00-5.00 sec 29.0 GBytes 49.8 Gbits/sec receiver
```

Results:

- Test duration: 5 seconds
- Reported throughput: approximately 49.8 Gbit/s
- TCP retransmissions reported by the sender: 2

Interpretation:

This test measured TCP data transfer between containers on a local Docker bridge network. Docker Desktop virtualization and the host's processing can affect the result. The reported rate must not be interpreted as the Mac's internet speed or as a physical network's guaranteed capacity.

Two retransmissions in a short test are not, on their own, enough to diagnose a network fault. Investigate trends, packet drops, retransmission rates, and application impact together.

Stop the temporary server after the test:

```bash
docker stop lab11-iperf-server
```

## 5. Key network performance concepts

- **Latency:** Time taken for data to travel between endpoints or for a request to complete.
- **Packet loss:** Percentage of transmitted packets that fail to arrive at the destination.
- **Jitter:** Variation in packet delay over time.
- **Throughput:** Amount of data transferred per unit of time.
- **TCP retransmission:** A TCP segment is sent again because delivery was not successfully acknowledged in time or the sender otherwise determines it must be resent.
- **p95/p99 latency:** The latency below which 95% or 99% of measured requests fall, respectively.

These signals are related but not interchangeable. High latency can occur without packet loss, and low packet loss does not guarantee high throughput.

## 6. SRE production troubleshooting workflow

When an application is slow or users report connectivity problems:

1. **Define the impact:** Identify affected services, users, regions, and time windows.
2. **Check application metrics:** Compare request rate, error rate, p50/p95/p99 latency, and dependency latency.
3. **Test reachability:** Use ping where ICMP is permitted, and use curl or application-specific checks to test the actual service.
4. **Measure request timing:** Separate name resolution, connection establishment, first-byte latency, and total duration.
5. **Investigate packet loss and retransmissions:** Correlate network-level evidence with interface counters, host metrics, and service symptoms.
6. **Measure throughput:** Use an appropriate tool such as iperf3 between approved endpoints and compare against expected capacity.
7. **Check host resources:** Look for CPU saturation, memory pressure, container limits, and competing workloads.
8. **Verify the result:** Repeat measurements and confirm that application-level latency and errors have recovered.

Use production-approved endpoints and controlled test windows when running throughput tests. Network benchmarks can consume resources and should not be launched indiscriminately during an incident.

## 7. Useful commands

```bash
# Measure HTTP request timing
curl -sS -o /dev/null \
  -w 'connect=%{time_connect}s total=%{time_total}s\n' \
  http://example-service:8080

# Inspect Docker network details
docker network inspect lab10-network

# Check running containers
docker ps

# Inspect a container's logs
docker logs --tail 100 CONTAINER_NAME

# Ping a target when ICMP is available
ping -c 10 TARGET_HOST

# Run a throughput test against an iperf3 server
iperf3 -c SERVER_HOST -t 5
```

## Key interview takeaways

- Latency, packet loss, jitter, and throughput describe different aspects of network performance.
- Curl timing fields help isolate where time is being spent in an HTTP request.
- Ping is a reachability tool, not a complete application health check.
- Throughput measurements must be interpreted in the context of the test path and host environment.
- Use percentiles and time-series trends rather than relying on one measurement.
- Correlate network evidence with application symptoms before declaring the network to be the root cause.
