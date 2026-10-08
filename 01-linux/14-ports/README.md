# Linux Lab 14 — Ports & Sockets Troubleshooting

## Objective

Learn how to:

* Check whether a TCP port is listening
* Identify which process owns a port
* Test application connectivity
* Understand `LISTEN` state
* Troubleshoot `Connection refused`
* Verify application recovery

---

## Production Scenario

Users report:

> "The server is reachable, but the application on port 8080 is not accessible."

The goal is to determine whether:

* The application process is running
* The application is listening on the expected port
* The port is reachable
* The application is actually responding

---

## Environment

* Ubuntu 24.04 container
* Docker
* Application: Python HTTP server
* Port: `8080`

---

## Step 1 — Check Listening Ports

Command:

```bash
ss -lntp
```

### Important options

| Option | Meaning                          |
| ------ | -------------------------------- |
| `-l`   | Listening sockets                |
| `-n`   | Show numeric addresses and ports |
| `-t`   | TCP sockets                      |
| `-p`   | Show process information         |

Initially, there was no application listening on port 8080.

---

## Step 2 — Create a Test Application

Created an application directory:

```bash
mkdir -p /opt/myapp/web
```

Created a simple web page:

```bash
echo "SRE Lab application is running" > /opt/myapp/web/index.html
```

Started a Python HTTP server:

```bash
cd /opt/myapp/web

python3 -m http.server 8080 --bind 0.0.0.0 &
```

The application started with PID `228`.

---

## Step 3 — Verify the Listening Port

Command:

```bash
ss -lntp
```

Output showed:

```text
LISTEN  0  5  0.0.0.0:8080  0.0.0.0:*  users:(("python3",pid=228,fd=3))
```

This confirmed:

* TCP port `8080` is listening
* Python is providing the service
* PID `228` owns the socket
* `0.0.0.0:8080` means the application is listening on all IPv4 interfaces

---

## Step 4 — Test the Application

Command:

```bash
curl http://127.0.0.1:8080
```

Result:

```text
SRE Lab application is running
```

The application was healthy.

---

# Incident Simulation

## Step 5 — Stop the Application

Stopped the application:

```bash
kill 228
```

Then checked the ports:

```bash
ss -lntp
```

There was no listener on port `8080`.

The shell also confirmed:

```text
[1]+ Terminated python3 -m http.server 8080 --bind 0.0.0.0
```

---

## Step 6 — Test the Failed Application

Command:

```bash
curl -v http://127.0.0.1:8080
```

Result:

```text
connect to 127.0.0.1 port 8080 failed: Connection refused
```

This reproduced the production problem.

---

## Step 7 — Check the Application Process

Command:

```bash
ps aux | grep '[p]ython3'
```

No Python application process was running.

### Root Cause

The application process had stopped.

Because the process was no longer running:

```text
Application process stopped
        ↓
No process listening on port 8080
        ↓
Client connection rejected
        ↓
curl reports Connection refused
```

---

# Recovery

Restarted the application:

```bash
python3 -m http.server 8080 --bind 0.0.0.0 &
```

The application restarted with PID `236`.

---

## Step 8 — Verify Recovery

Checked the listening port:

```bash
ss -lntp
```

Output:

```text
LISTEN  0  5  0.0.0.0:8080  0.0.0.0:*  users:(("python3",pid=236,fd=3))
```

The port was listening again.

Tested the application:

```bash
curl http://127.0.0.1:8080
```

Result:

```text
SRE Lab application is running
```

The application returned HTTP `200`.

---

# Important Concepts

## What does LISTEN mean?

`LISTEN` means a process has opened a TCP socket and is waiting for incoming connections.

Example:

```text
0.0.0.0:8080
```

means the application is listening on TCP port `8080` on all IPv4 interfaces.

---

## Connection Refused vs Connection Timeout

### Connection refused

Example:

```text
Connection refused
```

Usually means the host was reachable, but there was no service accepting the connection on that port, or the connection was actively rejected.

Typical investigation:

```bash
ss -lntp
ps aux
```

### Connection timeout

A timeout can indicate problems such as:

* Firewall filtering
* Routing problems
* Network path issues
* Security rules
* A service that isn't responding

A timeout requires broader network investigation.

---

# Production Troubleshooting Flow

When an application on a specific port is unavailable:

```text
Application unavailable
        ↓
Test the port
        ↓
curl / nc
        ↓
Connection refused?
        ↓
Check listening sockets
        ↓
ss -lntp
        ↓
Is the port listening?
        ↓
NO
        ↓
Check application process
        ↓
ps
        ↓
Check logs
        ↓
Find root cause
        ↓
Restart/fix application
        ↓
Verify process
        ↓
Verify port
        ↓
Verify application response
```

---

# Useful Commands

```bash
ss -lntp
```

Show listening TCP ports and processes.

```bash
ss -lnt
```

Show listening TCP ports without process information.

```bash
ps aux
```

List running processes.

```bash
curl http://127.0.0.1:8080
```

Test an HTTP application.

```bash
curl -v http://127.0.0.1:8080
```

Show detailed connection information.

---

# SRE Production Relevance

Port troubleshooting is extremely common in production.

An application may appear to be "up" from the server's perspective while still being inaccessible to users.

A proper investigation should verify three things:

1. **Process** — Is the application running?
2. **Port** — Is it listening on the expected port?
3. **Application** — Does it actually respond correctly?

A process existing by itself does not prove that the application is healthy.

---

# Interview Answer

If asked:

> "The server is reachable but the application on port 8080 is inaccessible. How would you troubleshoot?"

Answer:

> "First I'd test connectivity to port 8080 using curl or nc. If I get connection refused, I'd check whether anything is listening on that port using `ss -lntp`. If there is no listener, I'd check the application process with `ps` and then inspect the application logs to determine why it stopped. After fixing or restarting the application, I'd verify the process, confirm port 8080 is listening, and finally test the application endpoint to make sure it returns a successful response."

---

# Key Takeaways

* `ss` is one of the most important Linux networking troubleshooting commands.
* `LISTEN` means a process is accepting TCP connections on that port.
* `ss -lntp` can identify which process owns a listening port.
* `Connection refused` and `Connection timeout` are different problems.
* Always investigate before restarting.
* After recovery, verify **process → port → application response**.
* The goal of troubleshooting is not to memorize commands, but to understand the evidence each command provides.
