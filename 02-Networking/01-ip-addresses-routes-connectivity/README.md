# Lab 01: IP Addresses, Routes, and Connectivity

## Objective

Learn how to inspect Linux network interfaces, understand routing, verify connectivity, troubleshoot DNS resolution, and test application reachability.

## Environment

- Host: macOS
- Lab environment: Ubuntu 24.04 Docker container
- Container IP: `172.17.0.2/16`
- Network interface: `eth0`
- Default gateway: `172.17.0.1`
- Test application: Python HTTP server on port `8080`

## Commands Practiced

| Command | Purpose |
|---|---|
| `ip addr` | Inspect network interfaces and IP addresses |
| `ip route` | Inspect the routing table and default gateway |
| `ping -c 4 172.17.0.1` | Test Docker gateway reachability |
| `ping -c 4 8.8.8.8` | Test external IPv4 reachability |
| `getent hosts google.com` | Test hostname resolution |
| `curl -I --max-time 10 https://google.com` | Test HTTPS and inspect response headers |
| `curl -I -L --max-time 10 https://google.com` | Follow redirects and inspect the final response |
| `curl -I --max-time 5 http://127.0.0.1:8080/` | Test the application from inside the container |
| `docker ps --filter name=sre-linux-lab` | Inspect container status and port publishing |
| `curl -i --max-time 5 http://127.0.0.1:8080/` | Test the application from the Mac host |

## Findings

- `eth0` was up with IPv4 address `172.17.0.2/16`.
- The default route pointed to `172.17.0.1`.
- Gateway and external IPv4 ping tests succeeded with zero packet loss.
- `getent hosts google.com` returned IPv6 addresses.
- HTTPS to Google returned `301`, followed by `200 OK` when redirects were followed.
- The application returned `200 OK` from inside the container.
- Docker published port `8080` to the host, and the Mac-side request succeeded.

## Troubleshooting Method

When a service is unreachable, investigate methodically:

1. Inspect the network interface and IP configuration.
2. Check the routing table and default gateway.
3. Test gateway and destination IP reachability where appropriate.
4. Verify hostname resolution.
5. Test TCP, TLS, and HTTP connectivity using the relevant client.
6. Check whether the application is listening on the expected port.
7. Verify Docker port publishing or other network rules.
8. Retest from the same location where the failure was observed.

## Key Learning

A running application is not necessarily reachable from outside its container. Successful ping tests do not prove that DNS, TCP, TLS, or HTTP is working. Each layer needs its own evidence.

## Production Note

Do not assume that ping failure always means a host is down: ICMP may be filtered. In production, combine network checks with application-level health checks, logs, metrics, and tests from the affected network location.

## Result

**Completed:** inspected interfaces and routes, verified gateway and external connectivity, tested hostname resolution and HTTPS, and confirmed application access from both inside the container and the Mac host.