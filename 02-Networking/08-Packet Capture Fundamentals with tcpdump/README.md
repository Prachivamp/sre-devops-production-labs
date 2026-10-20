# Lab 08: Packet Capture Fundamentals with tcpdump

## Objective

Learn how to capture and analyze network packets using `tcpdump` to troubleshoot DNS resolution, TCP connections, HTTP requests, and connectivity problems.

## Environment

- Host: macOS
- Lab environment: Ubuntu Docker container
- Container IP: `172.17.0.2`
- Active network interface: `eth0`
- DNS resolver: `192.168.65.7`
- Tool: `tcpdump` 4.99.4

## 1. Install and verify tcpdump

Check whether tcpdump is installed:

```bash
command -v tcpdump
```

Update package lists and install it when necessary:

```bash
apt update
apt install -y tcpdump
tcpdump --version
```

## 2. Identify the network interface

```bash
ip -br addr
```

Observed active interface:

```text
eth0@if23 UP 172.17.0.2/16
```

`eth0` is the container's active network interface. The loopback interface `lo` is used for traffic within the same network namespace.

## 3. Capture packets

```bash
tcpdump -i eth0 -nn
```

- `-i eth0`: capture traffic on `eth0`.
- `-nn`: display numeric addresses and port numbers without name or service resolution.
- `-c 10`: stop after capturing 10 packets.
- `Ctrl+C`: stop a running capture.

An initial five-second capture returned zero packets. This was not proof of a network failure; no packets were captured during that observation window.

## 4. Observe DNS and ARP traffic

Generate traffic in a second shell while capturing on `eth0`:

```bash
tcpdump -i eth0 -nn -c 10
```

Generate a DNS lookup:

```bash
getent ahostsv4 google.com
```

### Observed DNS query

```text
172.17.0.2.50170 > 192.168.65.7.53: 27003+ A? google.com.
172.17.0.2.50170 > 192.168.65.7.53: 5246+ AAAA? google.com.
```

Interpretation:

- `172.17.0.2`: container IP.
- `50170`: temporary client source port in this capture.
- `192.168.65.7:53`: DNS resolver and destination port.
- `A?`: query for an IPv4 address.
- `AAAA?`: query for an IPv6 address.
- `>`: packet direction.

### Observed ARP exchange

```text
ARP, Request who-has 172.17.0.1 tell 172.17.0.2
ARP, Reply 172.17.0.1 is-at 16:35:f1:f3:e4:2f
```

The container requested the MAC address of its gateway, `172.17.0.1`, and received a reply.

The capture also contained ICMP messages reporting UDP port 50170 unreachable after DNS responses arrived. This can happen if the client socket is no longer listening when a response arrives. The capture alone does not establish the exact cause or prove that DNS is broken.

DNS resolution was subsequently confirmed to work:

```bash
getent ahostsv4 google.com
```

Observed IPv4 address:

```text
172.217.26.110
```

DNS results can change over time and may return different addresses.

## 5. Capture a TCP connection and HTTP request

Start a capture:

```bash
tcpdump -i eth0 -nn -c 12 'tcp port 80'
```

In another shell, generate an HTTP request:

```bash
curl -I --max-time 5 http://google.com
```

### Observed TCP handshake

```text
172.17.0.2.60922 > 172.217.26.110.80: Flags [S]
172.217.26.110.80 > 172.17.0.2.60922: Flags [S.]
172.17.0.2.60922 > 172.217.26.110.80: Flags [.]
```

Interpretation:

1. `[S]`: client sends SYN to initiate a TCP connection.
2. `[S.]`: server responds with SYN-ACK.
3. `[.]`: client sends ACK and completes the handshake.

The successful three-way handshake indicates that TCP connectivity to the destination was established.

### Observed HTTP exchange

```text
HTTP: HEAD / HTTP/1.1
HTTP: HTTP/1.1 301 Moved Permanently
```

The `curl -I` option sends a HEAD request. The server returned an HTTP 301 redirect.

`[F.]` represents a TCP FIN with ACK, which is part of a graceful connection close.

## 6. Verify the redirect

```bash
curl -sS -L -o /dev/null \
  -w 'Final HTTP status: %{http_code}\nRedirects followed: %{num_redirects}\n' \
  --max-time 10 http://google.com
```

Observed result:

```text
Final HTTP status: 200
Redirects followed: 1
```

The initial HTTP request redirected once, and the final response was successful.

## Key tcpdump options

| Option | Purpose |
|---|---|
| `-i eth0` | Capture on a specific interface |
| `-nn` | Avoid hostname and service-name resolution |
| `-c 10` | Stop after 10 captured packets |
| `-v` | Show more packet details |
| `-A` | Display packet payload as ASCII when applicable |
| `host 172.17.0.2` | Filter packets involving a host |
| `port 53` | Filter packets involving port 53 |
| `tcp port 80` | Filter TCP traffic involving port 80 |

Example DNS-focused capture:

```bash
tcpdump -i eth0 -nn -c 20 'port 53'
```

Example traffic for a particular host:

```bash
tcpdump -i eth0 -nn 'host 172.17.0.1'
```

## Production troubleshooting workflow

When investigating a network incident:

1. Identify the affected host, container, interface, destination, and port.
2. Verify DNS resolution independently.
3. Capture traffic on the relevant interface with a narrow filter.
4. Check whether requests leave the host and whether responses return.
5. For TCP, look for SYN, SYN-ACK, and ACK.
6. For HTTP, inspect status codes and redirect behavior.
7. Correlate packet evidence with application logs, metrics, and connection tests.
8. Draw conclusions only from observed evidence; a packet capture is a diagnostic aid, not proof of root cause by itself.

## Key learnings

- `tcpdump` can show real traffic entering and leaving a container.
- DNS queries distinguish IPv4 (`A`) from IPv6 (`AAAA`) lookups.
- ARP helps resolve local IPv4 addresses to MAC addresses.
- TCP flags reveal connection setup and closure.
- HTTP status codes help distinguish redirects from successful final responses.
- Packet filters reduce noise and make incident investigations more focused.
- Zero captured packets may simply mean no traffic matched during the capture window.

## Status

**Completed:** Installed tcpdump, identified the active interface, captured DNS and ARP packets, observed a TCP handshake and HTTP exchange, and verified a redirect ending in HTTP 200.

**Next lab:** Lab 09 — Docker Networking and Container Communication.
