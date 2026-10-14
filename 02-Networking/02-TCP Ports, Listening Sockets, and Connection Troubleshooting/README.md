# Lab 02: TCP Ports, Listening Sockets, and Connection Troubleshooting

## Objective

Understand listening TCP ports, connection refused errors, and Docker port publishing.

## Environment

- Host: macOS
- Container: Ubuntu
- Web server: Python HTTP server
- Ports tested: 8080 and 9090

## 1. Inspect listening TCP ports

Command:

```bash
ss -lntp
```

Observed listener:

```text
LISTEN 0 5 0.0.0.0:8080 0.0.0.0:* users:(("python3",pid=18,fd=3))
```

Key findings:

- `LISTEN`: a process is accepting incoming TCP connections.
- `0.0.0.0:8080`: the service listens on port 8080 on all IPv4 interfaces.
- `python3`: the process running the service.
- `ss -lntp`: shows listening TCP sockets and associated processes.

## 2. Troubleshoot a closed port

Command, run inside the original container:

```bash
curl -v --max-time 3 http://127.0.0.1:9090/
```

Observed result:

```text
Connection refused
curl: (7) Failed to connect
```

Diagnosis: no service was listening on port 9090 at that time.

## 3. Start a test service

Commands, run inside the original container:

```bash
mkdir -p /tmp/lab02
echo "Lab 02 service is running" > /tmp/lab02/index.html
cd /tmp/lab02
python3 -m http.server 9090 --bind 0.0.0.0
```

The server was started in the foreground and left running.

From a second shell inside the same container:

```bash
curl -i --max-time 5 http://127.0.0.1:9090/
```

Result: HTTP 200 OK, with the expected response body.

This proved the service was working inside the container.

## 4. Test access from the Mac host

Command, run on macOS:

```bash
curl -v --max-time 3 http://127.0.0.1:9090/
```

Observed result: connection refused.

Inspection of the original container showed that Docker published port 8080, but not port 9090.

Diagnosis: the service was listening inside the container, but port 9090 was not published to the Mac.

## 5. Publish the port using a separate test container

Command, run on macOS:

```bash
docker run -d --name sre-lab02-port-test -p 9090:9090 sre-linux-lab-backup:before-port-fix bash -lc 'mkdir -p /tmp/lab02 && echo "Lab 02 service is running" > /tmp/lab02/index.html && cd /tmp/lab02 && exec python3 -m http.server 9090 --bind 0.0.0.0'
```

Verify the published port:

```bash
docker ps --filter name=sre-lab02-port-test
```

Observed mapping:

```text
0.0.0.0:9090->9090/tcp
[::]:9090->9090/tcp
```

Test from macOS:

```bash
curl -i --max-time 5 http://127.0.0.1:9090/
```

Result:

```text
HTTP/1.0 200 OK
Lab 02 service is running
```

## Troubleshooting method

When a service is unreachable:

1. Check whether the process is running.
2. Check listening sockets with `ss -lntp`.
3. Test locally inside the container.
4. Check the service bind address and port.
5. Inspect Docker port publishing with `docker ps`.
6. Test from the host with `curl`.
7. Check application logs if the issue remains.

## Key production lessons

- A process must listen on the expected port.
- A service bound only to loopback may not accept connections through the container's network interface.
- A container port is not automatically published to the host.
- Docker port publishing is configured when the container is created; an existing container generally needs to be recreated to add a published port.
- `Connection refused` often means no listener is reachable at the target address and port, but the exact cause should be verified.
- HTTP 200 confirms an HTTP response succeeded; it does not by itself prove every application dependency is healthy.

## Cleanup

After completing verification, remove the temporary test container from macOS:

```bash
docker rm -f sre-lab02-port-test
```

Do not remove the main `sre-linux-lab` container.
EOF

git status --short