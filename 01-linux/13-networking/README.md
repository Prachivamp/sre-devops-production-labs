# Linux Lab 13 — Networking Basics & Connectivity Troubleshooting

## Objective

Learn how to troubleshoot a basic Linux networking problem using a layered approach.

This lab focuses on:

* Network interfaces
* IP addresses
* Routing tables
* Default gateways
* Local network connectivity
* External network connectivity
* DNS resolution
* HTTP/HTTPS connectivity
* Separating network, DNS, and application-layer problems

---

## Production Scenario

An application is reported as:

> "The application cannot connect to another service."

Instead of immediately assuming that the network is broken, investigate the problem layer by layer.

The troubleshooting flow used in this lab:

```text
Network interface
       ↓
IP address
       ↓
Routing
       ↓
Gateway connectivity
       ↓
External connectivity
       ↓
DNS resolution
       ↓
Application-layer connectivity
```

The goal is to prove where the failure occurs.

---

## Environment

* Ubuntu 24.04 LTS
* Running inside Docker
* Container: `sre-linux-lab`
* Host: macOS

---

# 1. Check Network Interfaces

Initially, the `ip` command was not available:

```text
bash: ip: command not found
```

Checked the package:

```bash
dpkg -l iproute2
```

The package was not installed.

Installed it:

```bash
apt update
apt install -y iproute2
```

Verified that the command was available:

```bash
command -v ip
```

Then checked the interfaces:

```bash
ip addr
```

The important interface was:

```text
eth0@if23
```

with:

```text
inet 172.17.0.2/16
```

### Important observations

* Interface: `eth0`
* Interface state: `UP`
* IP address: `172.17.0.2`
* Network: `172.17.0.0/16`

The container therefore has an active network interface and an assigned IP address.

---

# 2. Understand the Network Interface

Relevant output:

```text
eth0@if23: <BROADCAST,MULTICAST,UP,LOWER_UP>
inet 172.17.0.2/16
```

### `eth0`

The main network interface inside the container.

### `UP`

The interface is administratively enabled.

### `LOWER_UP`

The underlying link is operational.

### `172.17.0.2/16`

The container's IP address.

The `/16` means the subnet covers:

```text
172.17.0.0 - 172.17.255.255
```

---

# 3. Check the Routing Table

Command:

```bash
ip route
```

Output:

```text
default via 172.17.0.1 dev eth0
172.17.0.0/16 dev eth0 proto kernel scope link src 172.17.0.2
```

### Default route

```text
default via 172.17.0.1 dev eth0
```

This means traffic for destinations without a more specific route is sent through:

```text
172.17.0.1
```

using:

```text
eth0
```

For this Docker network, `172.17.0.1` is the gateway.

### Local route

```text
172.17.0.0/16 dev eth0
```

This tells Linux that the `172.17.0.0/16` network is directly reachable through `eth0`.

---

# 4. Test Gateway Connectivity

Initially, the `ping` command was missing:

```text
bash: ping: command not found
```

Installed the required package:

```bash
apt install -y iputils-ping
```

Then tested the Docker gateway:

```bash
ping -c 4 172.17.0.1
```

Result:

```text
4 packets transmitted, 4 received, 0% packet loss
```

Average latency:

```text
2.393 ms
```

### Conclusion

The container can successfully communicate with its local Docker gateway.

Therefore:

* Network interface works
* IP configuration works
* Local gateway is reachable

---

# 5. Test External Network Connectivity

Next, test an external IP address:

```bash
ping -c 4 8.8.8.8
```

Result:

```text
4 packets transmitted, 4 received, 0% packet loss
```

Average latency:

```text
19.179 ms
```

### Why use an IP address?

Using an IP address avoids DNS.

This test answers:

> Can the container reach an external network without involving hostname resolution?

The answer was yes.

Therefore basic external network connectivity was working.

---

# 6. Test DNS Resolution

Next, test whether Linux can resolve a hostname:

```bash
getent hosts google.com
```

Result:

```text
2404:6800:4002:818::200e google.com
```

This means the hostname:

```text
google.com
```

was successfully resolved to an IPv6 address.

### Important troubleshooting distinction

If:

```text
ping 8.8.8.8
```

works but:

```text
getent hosts google.com
```

fails, the underlying network may be working while DNS is the problem.

This distinction is extremely useful during production troubleshooting.

---

# 7. Test Application-Layer Connectivity

Finally, test an actual HTTPS connection:

```bash
curl -I https://google.com
```

The response included:

```text
HTTP/2 301
location: https://www.google.com/
```

### What does `301` mean?

`301` is an HTTP redirect.

Google successfully received the request and returned a valid HTTP response directing the client to another URL.

Therefore:

* DNS worked
* Network connectivity worked
* TCP/HTTPS connectivity worked
* Remote HTTP server responded

The connectivity path was healthy.

---

# 8. Final Troubleshooting Chain

The investigation followed this sequence:

```text
1. Network interface
       ↓
   eth0 ✅

2. IP address
       ↓
   172.17.0.2/16 ✅

3. Routing
       ↓
   172.17.0.1 gateway ✅

4. Gateway connectivity
       ↓
   0% packet loss ✅

5. External connectivity
       ↓
   8.8.8.8 reachable ✅

6. DNS resolution
       ↓
   google.com resolves ✅

7. HTTPS connectivity
       ↓
   HTTP/2 301 response ✅
```

---

# 9. SRE Troubleshooting Mindset

One of the most important lessons from this lab is:

> Never immediately assume "the network is down."

Instead, narrow the problem down layer by layer.

For example:

```text
Application cannot connect
        ↓
Does the host have an interface?
        ↓
Does it have an IP?
        ↓
Does it have a route?
        ↓
Can it reach the gateway?
        ↓
Can it reach the destination IP?
        ↓
Does DNS resolve the destination?
        ↓
Is the destination service reachable?
        ↓
Is the application protocol working?
```

This prevents random troubleshooting.

---

# 10. Common Failure Patterns

## Case 1 — Interface is down

Example:

```text
eth0: state DOWN
```

Possible investigation:

```bash
ip addr
```

---

## Case 2 — No IP address

The interface exists but has no usable IP.

Investigate:

```bash
ip addr
```

---

## Case 3 — No default route

Check:

```bash
ip route
```

If the default route is missing, external destinations may not be reachable.

---

## Case 4 — Gateway unreachable

Example:

```bash
ping -c 4 172.17.0.1
```

with packet loss or failure.

This points toward a local network/interface/routing problem.

---

## Case 5 — External IP unreachable

If:

```bash
ping 172.17.0.1
```

works but:

```bash
ping 8.8.8.8
```

fails, investigate routing, firewalling, Docker networking, or upstream connectivity.

---

## Case 6 — IP works but DNS fails

Example:

```text
ping 8.8.8.8 → works
getent hosts google.com → fails
```

This strongly suggests a DNS-related problem.

---

## Case 7 — DNS works but application connection fails

Example:

```text
DNS → works
curl → connection refused
```

Now investigate the destination service, port, firewall, or application.

This is where the next lab becomes important.

---

# Key Commands Learned

| Command        | Purpose                                        |
| -------------- | ---------------------------------------------- |
| `ip addr`      | View network interfaces and IP addresses       |
| `ip route`     | View routing table                             |
| `ping`         | Test basic IP connectivity                     |
| `getent hosts` | Test hostname resolution                       |
| `curl`         | Test application-layer HTTP/HTTPS connectivity |
| `command -v`   | Check whether a command is available           |
| `dpkg -l`      | Check installed Debian/Ubuntu packages         |

---

# Production Troubleshooting Flow

When an application cannot connect to another service:

```text
PROBLEM
Application cannot connect
        ↓
CHECK INTERFACE
ip addr
        ↓
CHECK IP
Is the host/container configured correctly?
        ↓
CHECK ROUTE
ip route
        ↓
CHECK GATEWAY
ping gateway
        ↓
CHECK DESTINATION
ping destination IP where appropriate
        ↓
CHECK DNS
getent hosts hostname
        ↓
CHECK PORT
Is the destination port reachable?
        ↓
CHECK APPLICATION
Is the service listening and accepting connections?
        ↓
FIX
        ↓
VERIFY
        ↓
DOCUMENT
```

---

# Interview Question

### Q: An application cannot connect to a database. How would you troubleshoot it?

A strong answer:

> "I would troubleshoot it layer by layer instead of immediately assuming it's a network issue. First I would verify the server or container has a valid interface, IP address, and route. Then I would test connectivity to the destination. If the application uses a hostname, I would verify DNS resolution. After that I would check whether the database port is reachable and whether the database service is actually listening. Finally, I would inspect application and database logs for authentication, timeout, or connection errors."

---

# Key Takeaways

* A network interface must be present and operational.
* An IP address alone does not guarantee connectivity.
* Routing determines where packets go.
* The default gateway handles destinations outside the local network.
* `ping` can help test basic IP connectivity.
* DNS resolution and network connectivity are separate problems.
* `curl` can test connectivity at the application layer.
* A successful ping does not prove that an application port is working.
* Troubleshooting should move from lower-level connectivity toward the application layer.
* Always gather evidence before deciding what is broken.

---

## Production Mindset

The goal is not to memorize networking commands.

The goal is to answer:

> **Can I prove where the connection is failing?**

Think:

```text
Interface
   ↓
IP
   ↓
Route
   ↓
Gateway
   ↓
Destination
   ↓
DNS
   ↓
Port
   ↓
Application
```

This layered approach will be reused throughout the Docker, Kubernetes, cloud, and production troubleshooting labs.
