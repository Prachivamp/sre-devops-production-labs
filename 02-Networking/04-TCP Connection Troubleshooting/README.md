# Lab 04: TCP Connection Troubleshooting

## Objective

Understand TCP listening sockets, established connections, and how to inspect TCP connection states during production troubleshooting.

## Environment

- **Host:** macOS
- **Lab environment:** Ubuntu 24.04 Docker container
- **Container IPv4 address:** `172.17.0.2`
- **Application port:** `8080`
- **Application response:** HTTP 200 OK

---

## 1. Inspect TCP Sockets

### Command

```bash
ss -ant
```

### Observed Output

```text
State   Recv-Q  Send-Q  Local Address:Port  Peer Address:Port
LISTEN  0       5       0.0.0.0:8080        0.0.0.0:*
```

### Findings

- `LISTEN` indicates that the application is waiting for incoming TCP connections.
- `0.0.0.0:8080` means the socket is listening on all IPv4 interfaces inside the container.
- `Recv-Q` and `Send-Q` show queue information for the socket.
- The listening socket alone does not prove that the application is healthy or reachable from external clients.

### Production Relevance

If an application is reported as unavailable, first verify whether the expected port is listening. Then test connectivity and application behavior separately.

---

## 2. Test the Application with curl

### Command

```bash
curl -v --max-time 5 http://127.0.0.1:8080/
```

### Observed Results

- TCP connection established successfully.
- HTTP GET request sent to the application.
- Application returned `HTTP/1.0 200 OK`.
- Response body: `SRE Lab application is running`.

### Findings

The application accepted a local TCP connection and returned a successful HTTP response.

This confirms that the service was responding correctly to a request from inside the container at the time of testing.

### Production Relevance

A successful TCP connection does not automatically guarantee that an application is healthy. Validate the HTTP response, application logs, and relevant dependencies as well.

---

## 3. Create a Long-Lived TCP Connection

A short-lived connection can close before we inspect it. To observe an established connection, we created a Python client that holds a TCP connection open for 30 seconds.

### Command

```bash
python3 -c 'import socket,time; s=socket.create_connection(("127.0.0.1",8080)); print("TCP connected; holding for 30 seconds"); time.sleep(30); s.close()'
```

The command was run inside the Ubuntu container while the application on port `8080` remained running.

### Inspect the Connection

While the Python client was holding the connection open, we ran:

```bash
ss -ant
```

### Observed Output

```text
State   Recv-Q  Send-Q  Local Address:Port  Peer Address:Port
LISTEN  0       5       0.0.0.0:8080        0.0.0.0:*
ESTAB   0       0       127.0.0.1:48578     127.0.0.1:8080
ESTAB   0       0       127.0.0.1:8080      127.0.0.1:48578
```

*Note: The client-side port `48578` is the value observed during this run. It may change on subsequent runs.*

### Findings

- `ESTAB` means the TCP connection is established.
- Port `48578` is the temporary client-side port in this example.
- Port `8080` is the server-side listening port.
- The two `ESTAB` rows represent the client and server endpoints of the same TCP connection.
- Both endpoints use `127.0.0.1` because the test was performed over localhost inside the container.

### Production Relevance

When investigating connection issues, inspect active connections to understand whether clients are establishing TCP sessions with the service.

---

## 4. Observe the Connection Closing

After the Python client completed its 30-second wait, it closed the socket.

We ran the following command again:

```bash
ss -ant
```

### Observed Result

Only the listening socket on port `8080` remained in the snapshot.

### Findings

This was expected because the temporary TCP connection had already closed before the next inspection.

### Production Relevance

TCP connection states represent a snapshot in time. Short-lived connections may not appear in a one-time inspection.

For connections that are difficult to catch, consider repeated observations, tools such as `watch` if installed, or appropriate network monitoring.

---

## 5. TCP States Covered

| State | Meaning | Troubleshooting Use |
|---|---|---|
| `LISTEN` | Waiting for incoming TCP connections | Check whether a service is listening on the expected port. |
| `ESTAB` | TCP connection established | Confirm that a connection currently exists between endpoints. |

---

## 6. Production TCP Troubleshooting Workflow

When a user reports that an application is unreachable, follow this sequence:

1. **Check the listening socket**
   ```bash
   ss -lntp
   ```

   Confirm that the expected port is listening and identify the process when permissions allow.

2. **Test local application access**
   ```bash
   curl -v --max-time 5 http://127.0.0.1:8080/
   ```

   Inspect whether the TCP connection succeeds and whether the application returns an HTTP response.

3. **Inspect active TCP connections**
   ```bash
   ss -ant
   ```

   Look for established connections and compare local and remote addresses.

4. **Test from the actual client or host**

   A successful localhost test does not prove that remote clients can reach the application. Check Docker port publishing, routing, firewall rules, and other network components as appropriate.

5. **Investigate the application layer**

   If TCP connects but requests fail, examine HTTP status codes, application logs, dependencies, and service health.

6. **Collect evidence before changing configuration**

   Use the observed errors and connection states to narrow down the failing layer before applying a fix.

---

## 7. Key Takeaways

- `ss -ant` displays TCP sockets and their current states.
- `LISTEN` means a socket is waiting for connections.
- `ESTAB` means a TCP connection has been established.
- A single TCP connection may appear as two established socket entries, one for each endpoint.
- Short-lived connections can disappear before they are inspected.
- A listening socket does not prove end-to-end reachability.
- A successful TCP connection does not by itself prove application health.
- Troubleshooting should distinguish TCP connectivity problems from HTTP and application-level failures.

---

## 8. Lab Completion Checklist

- [x] Inspected TCP listening sockets with `ss -ant`
- [x] Tested local application connectivity with `curl`
- [x] Observed a long-lived established TCP connection
- [x] Identified the client-side and server-side endpoints
- [x] Confirmed that the connection disappeared after it closed
- [x] Documented TCP states and production troubleshooting steps

**Status: Completed**

**Next Lab:** Lab 05 — HTTP and HTTPS Troubleshooting