# Networking Lab 03: DNS Troubleshooting

## Objective

Understand hostname resolution, compare IPv4 and IPv6 connectivity, and distinguish DNS resolution failures from network connectivity failures.

## Environment

- **Host:** macOS
- **Lab environment:** Ubuntu 24.04 Docker container
- **Container IPv4 address:** `172.17.0.2`
- **DNS resolver:** `192.168.65.7`

## 1. Check DNS Resolution

### Commands

```bash
getent hosts google.com
getent ahostsv4 google.com
```

### Findings

- `getent hosts google.com` returned an IPv6 address.
- `getent ahostsv4 google.com` returned IPv4 addresses.
- Both IPv4 and IPv6 name resolution worked during these tests.

**Key takeaway:** DNS can return addresses even when the container cannot connect to those addresses.

## 2. Inspect DNS Configuration

### Command

```bash
cat /etc/resolv.conf
```

### Finding

The container's configured DNS resolver was:

```text
nameserver 192.168.65.7
```

Docker generated this resolver configuration.

## 3. Investigate an Intermittent DNS Timeout

### Command

```bash
curl -4 -I --max-time 5 https://google.com
```

### Findings

- An initial request timed out during name resolution.
- Five repeated IPv4 hostname lookups succeeded.
- A subsequent IPv4 HTTPS request succeeded.
- The cause of the intermittent DNS timeout was not established.

**Production lesson:** A single timeout is evidence of a failure, not proof of its root cause. Repeat the test and collect more evidence before making changes.

## 4. Compare IPv4 and IPv6 Connectivity

### Commands

```bash
curl -4 -I --max-time 10 https://google.com
curl -6 -I --max-time 10 https://google.com
```

### IPv4 Result

The IPv4 request succeeded and returned:

```text
HTTP/2 301
location: https://www.google.com/
```

The `301` response is a normal HTTP redirect.

### IPv6 Result

The IPv6 request failed with a connection error on port `443`.

**Finding:** IPv4 HTTPS connectivity worked, while IPv6 HTTPS connectivity failed.

## 5. Inspect IPv6 Routes and Interface Addresses

### Commands

```bash
ip -6 route
ip -br addr
```

### Findings

- `ip -6 route` returned no routes.
- The `eth0` interface was UP.
- `eth0` had IPv4 address `172.17.0.2/16`.
- `eth0` had no configured IPv6 address.
- The loopback interface had `::1/128`, which is used for local IPv6 communication.

### Conclusion

The container had no configured IPv6 address on its main network interface and no IPv6 routes. This explains why the tested external IPv6 connection could not be established in the current environment.

This finding does not establish the cause of the separate intermittent DNS timeout.

## 6. Production Troubleshooting Workflow

When an application cannot reach a hostname, investigate in this order:

1. **DNS resolution:** Does the hostname resolve?
   ```bash
   getent hosts example.com
   ```

2. **DNS configuration:** Which resolver is configured?
   ```bash
   cat /etc/resolv.conf
   ```

3. **Interface configuration:** Does the system have the expected IP address?
   ```bash
   ip -br addr
   ```

4. **Routing:** Is there a route to the destination?
   ```bash
   ip route
   ip -6 route
   ```

5. **Connectivity:** Can the system establish an HTTP connection?
   ```bash
   curl -4 -I --max-time 10 https://example.com
   curl -6 -I --max-time 10 https://example.com
   ```

6. **Root cause:** Correlate the results with logs, network configuration, and repeated tests before changing anything.

## 7. Common Interview Questions

**Q1. Can DNS work while an application is unreachable?**

Yes. DNS resolution only provides an address. Connectivity can still fail because of routing, firewall rules, missing IP configuration, or destination-side issues.

**Q2. How do you compare IPv4 and IPv6 connectivity?**

Use `curl -4` and `curl -6`, then inspect interface addresses and routing tables.

**Q3. What does an empty IPv6 routing table indicate?**

It indicates that no IPv6 routes are configured in the current network namespace. External IPv6 destinations generally cannot be reached without a suitable route.

**Q4. Does a DNS timeout always mean the DNS server is down?**

No. It could be intermittent resolver connectivity, packet loss, delays, or another issue along the resolution path. More evidence is needed to identify the cause.

## 8. Lab Checklist

- [x] Checked hostname resolution
- [x] Checked IPv4 DNS resolution
- [x] Inspected DNS resolver configuration
- [x] Investigated an intermittent DNS timeout
- [x] Compared IPv4 and IPv6 HTTPS connectivity
- [x] Inspected interface addresses
- [x] Inspected IPv6 routes
- [x] Documented findings and remaining uncertainty

## Summary

This lab demonstrated that DNS resolution and network connectivity are separate troubleshooting layers. IPv4 HTTPS worked, but IPv6 HTTPS failed because the container had no IPv6 address on `eth0` and no IPv6 routes. The intermittent DNS timeout remains unexplained and would require further investigation.