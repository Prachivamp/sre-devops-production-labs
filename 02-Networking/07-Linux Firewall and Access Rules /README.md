# Lab 07: Linux Firewall and Access Rules

## 1. Objective

Understand how listening services, Docker port publishing, and firewall/access rules affect network connectivity.

This lab demonstrates how to:

- Inspect listening TCP ports.
- Verify local application connectivity.
- Check Docker port publishing.
- Recognize a connection-refused error.
- Separate service failures from potential firewall restrictions.

## 2. Environment

- Host: macOS
- Container: Ubuntu 24.04 running in Docker
- Container: `sre-linux-lab`
- Application port: TCP `8080`
- Test port: TCP `9099`
- Tools: `ss`, `curl`, and `docker`

## 3. Inspect Firewall Tools

Inside the Ubuntu container, we checked:

```bash
command -v ufw
command -v iptables
command -v nft
```

No paths were returned, meaning these commands were not installed in the container.

### Learning

A missing firewall command does not mean no firewall exists. Docker networking, the host operating system, cloud security groups, network ACLs, and upstream firewalls may all affect connectivity.

A normal application container is not necessarily the correct place to administer host firewall rules.

## 4. Check Listening TCP Ports

Inside the Ubuntu container:

```bash
ss -lnt
```

Observed result:

```text
LISTEN 0 5 0.0.0.0:8080 0.0.0.0:*
```

### Interpretation

- `LISTEN`: A TCP socket is waiting for incoming connections.
- `0.0.0.0:8080`: The application is listening on port `8080` on all IPv4 interfaces inside the container.
- `Recv-Q` and `Send-Q`: Queue information for the listening socket.

A listening socket confirms that a process has opened the port. It does not prove that clients outside the container can reach it.

## 5. Test the Application Inside the Container

Command:

```bash
curl -I --max-time 5 http://127.0.0.1:8080/
```

Observed result:

```text
HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.12.3
```

### Interpretation

The application responded successfully to a request from inside the container.

This verifies basic local HTTP functionality.

## 6. Verify Docker Port Publishing

On the Mac host:

```bash
docker ps --filter name=sre-linux-lab
```

Observed port mapping:

```text
0.0.0.0:8080->8080/tcp
[::]:8080->8080/tcp
```

### Interpretation

Docker publishes container port `8080` on host port `8080` for IPv4 and IPv6 host addresses.

We then tested the host endpoint:

```bash
curl -I --max-time 5 http://127.0.0.1:8080/
```

Observed result:

```text
HTTP/1.0 200 OK
```

This confirms that the application was reachable through the published port from the Mac.

**Security note:** Publishing a port on all host interfaces can make it reachable from other machines, depending on host firewall rules and network configuration. Bind services to loopback when access should be local only.

## 7. Simulate a Connection-Refused Error

On the Mac host:

```bash
curl -v --connect-timeout 3 --max-time 5 http://127.0.0.1:9099/
```

Observed result:

```text
connect to 127.0.0.1 port 9099 failed: Connection refused
curl: (7) Failed to connect
```

### Interpretation

We did not start a service on port `9099`, so the connection was refused immediately.

This is a useful example of an unavailable listener, not proof of a firewall restriction.

### Production relevance

A connection-refused error can occur when:

- No process is listening on the destination port.
- An application has stopped or failed to start.
- A service is listening on a different port or interface.
- A firewall or network device actively rejects connections.

Always confirm the cause rather than assuming every refused connection is a firewall issue.

## 8. Troubleshooting Workflow

When a service is reported as unreachable:

1. **Confirm the target:** Check the hostname, IP address, and port.
2. **Inspect the listener:** Use `ss -lntp` on the relevant Linux host or container.
3. **Test locally:** Use `curl` or an appropriate client against the local endpoint.
4. **Check port publishing:** For Docker, inspect `docker ps` and the port mapping.
5. **Test from the client:** Check connectivity from the actual source machine.
6. **Inspect firewall policy:** Review the relevant host firewall, cloud security group, network ACL, and upstream access rules.
7. **Check logs:** Correlate the failure with application, host, and network logs.

Useful commands:

```bash
# Inspect listening TCP ports
ss -lntp

# Test local HTTP
curl -v --connect-timeout 3 --max-time 5 http://127.0.0.1:8080/

# Check Docker port publishing
docker ps

# Check basic TCP connectivity when netcat is installed
nc -vz <host> <port>
```

Run firewall inspection commands on the relevant host or network platform, using the tools supported by that environment.

## 9. Common Symptoms

| Symptom | Possible investigation areas |
|---|---|
| Connection refused | Listener, application state, destination port, active rejection |
| Connection timeout | Silent filtering, routing, unreachable host, overloaded service |
| Works inside container but not externally | Port publishing, binding address, firewall, routing |
| Works locally but not from another machine | Host firewall, access rules, routing, network ACL |
| Port is listening but application fails | Application logs, dependencies, protocol mismatch |

These are investigation starting points, not definitive diagnoses.

## 10. Key Learnings

- A listening port does not guarantee remote reachability.
- Docker port publishing connects a host port to a container port.
- A connection-refused error is different from a connection timeout.
- Missing firewall tools in a container do not prove that traffic is unrestricted.
- Firewall troubleshooting must be performed at the network layer that actually controls the traffic.
- Verify the application, listener, port mapping, and access policy separately.

## 11. Lab Completion Checklist

- [x] Checked for available firewall tools.
- [x] Inspected the listening application port.
- [x] Verified local application connectivity.
- [x] Inspected Docker port publishing.
- [x] Confirmed host connectivity to the published port.
- [x] Reproduced a connection-refused error on an unused port.
- [x] Documented a production troubleshooting workflow.

**Status:** Core hands-on checks completed. Direct firewall-rule inspection or modification was not performed in this container.

**Next lab:** Lab 08 — Packet Capture Fundamentals with tcpdump.
# Lab 07: Linux Firewall and Access Rules

## 1. Objective

Understand how listening services, Docker port publishing, and firewall/access rules affect network connectivity.

This lab demonstrates how to:

- Inspect listening TCP ports.
- Verify local application connectivity.
- Check Docker port publishing.
- Recognize a connection-refused error.
- Separate service failures from potential firewall restrictions.

## 2. Environment

- Host: macOS
- Container: Ubuntu 24.04 running in Docker
- Container: `sre-linux-lab`
- Application port: TCP `8080`
- Test port: TCP `9099`
- Tools: `ss`, `curl`, and `docker`

## 3. Inspect Firewall Tools

Inside the Ubuntu container, we checked:

```bash
command -v ufw
command -v iptables
command -v nft
```

No paths were returned, meaning these commands were not installed in the container.

### Learning

A missing firewall command does not mean no firewall exists. Docker networking, the host operating system, cloud security groups, network ACLs, and upstream firewalls may all affect connectivity.

A normal application container is not necessarily the correct place to administer host firewall rules.

## 4. Check Listening TCP Ports

Inside the Ubuntu container:

```bash
ss -lnt
```

Observed result:

```text
LISTEN 0 5 0.0.0.0:8080 0.0.0.0:*
```

### Interpretation

- `LISTEN`: A TCP socket is waiting for incoming connections.
- `0.0.0.0:8080`: The application is listening on port `8080` on all IPv4 interfaces inside the container.
- `Recv-Q` and `Send-Q`: Queue information for the listening socket.

A listening socket confirms that a process has opened the port. It does not prove that clients outside the container can reach it.

## 5. Test the Application Inside the Container

Command:

```bash
curl -I --max-time 5 http://127.0.0.1:8080/
```

Observed result:

```text
HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.12.3
```

### Interpretation

The application responded successfully to a request from inside the container.

This verifies basic local HTTP functionality.

## 6. Verify Docker Port Publishing

On the Mac host:

```bash
docker ps --filter name=sre-linux-lab
```

Observed port mapping:

```text
0.0.0.0:8080->8080/tcp
[::]:8080->8080/tcp
```

### Interpretation

Docker publishes container port `8080` on host port `8080` for IPv4 and IPv6 host addresses.

We then tested the host endpoint:

```bash
curl -I --max-time 5 http://127.0.0.1:8080/
```

Observed result:

```text
HTTP/1.0 200 OK
```

This confirms that the application was reachable through the published port from the Mac.

**Security note:** Publishing a port on all host interfaces can make it reachable from other machines, depending on host firewall rules and network configuration. Bind services to loopback when access should be local only.

## 7. Simulate a Connection-Refused Error

On the Mac host:

```bash
curl -v --connect-timeout 3 --max-time 5 http://127.0.0.1:9099/
```

Observed result:

```text
connect to 127.0.0.1 port 9099 failed: Connection refused
curl: (7) Failed to connect
```

### Interpretation

We did not start a service on port `9099`, so the connection was refused immediately.

This is a useful example of an unavailable listener, not proof of a firewall restriction.

### Production relevance

A connection-refused error can occur when:

- No process is listening on the destination port.
- An application has stopped or failed to start.
- A service is listening on a different port or interface.
- A firewall or network device actively rejects connections.

Always confirm the cause rather than assuming every refused connection is a firewall issue.

## 8. Troubleshooting Workflow

When a service is reported as unreachable:

1. **Confirm the target:** Check the hostname, IP address, and port.
2. **Inspect the listener:** Use `ss -lntp` on the relevant Linux host or container.
3. **Test locally:** Use `curl` or an appropriate client against the local endpoint.
4. **Check port publishing:** For Docker, inspect `docker ps` and the port mapping.
5. **Test from the client:** Check connectivity from the actual source machine.
6. **Inspect firewall policy:** Review the relevant host firewall, cloud security group, network ACL, and upstream access rules.
7. **Check logs:** Correlate the failure with application, host, and network logs.

Useful commands:

```bash
# Inspect listening TCP ports
ss -lntp

# Test local HTTP
curl -v --connect-timeout 3 --max-time 5 http://127.0.0.1:8080/

# Check Docker port publishing
docker ps

# Check basic TCP connectivity when netcat is installed
nc -vz <host> <port>
```

Run firewall inspection commands on the relevant host or network platform, using the tools supported by that environment.

## 9. Common Symptoms

| Symptom | Possible investigation areas |
|---|---|
| Connection refused | Listener, application state, destination port, active rejection |
| Connection timeout | Silent filtering, routing, unreachable host, overloaded service |
| Works inside container but not externally | Port publishing, binding address, firewall, routing |
| Works locally but not from another machine | Host firewall, access rules, routing, network ACL |
| Port is listening but application fails | Application logs, dependencies, protocol mismatch |

These are investigation starting points, not definitive diagnoses.

## 10. Key Learnings

- A listening port does not guarantee remote reachability.
- Docker port publishing connects a host port to a container port.
- A connection-refused error is different from a connection timeout.
- Missing firewall tools in a container do not prove that traffic is unrestricted.
- Firewall troubleshooting must be performed at the network layer that actually controls the traffic.
- Verify the application, listener, port mapping, and access policy separately.

## 11. Lab Completion Checklist

- [x] Checked for available firewall tools.
- [x] Inspected the listening application port.
- [x] Verified local application connectivity.
- [x] Inspected Docker port publishing.
- [x] Confirmed host connectivity to the published port.
- [x] Reproduced a connection-refused error on an unused port.
- [x] Documented a production troubleshooting workflow.

**Status:** Core hands-on checks completed. Direct firewall-rule inspection or modification was not performed in this container.

**Next lab:** Lab 08 — Packet Capture Fundamentals with tcpdump.
