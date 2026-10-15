# Lab 05: HTTP and HTTPS Troubleshooting

## Objective

Understand how to troubleshoot HTTP and HTTPS connectivity issues in a Linux environment. Learn to distinguish application-level HTTP responses, redirects, TLS certificate errors, and connection failures.

## Environment

- Host: macOS
- Lab environment: Ubuntu Docker container
- Local application: `http://127.0.0.1:8080/`
- Tools: `curl`, Docker, and Linux command-line utilities

## 1. Test a Local HTTP Application

### Command

Run inside the Ubuntu container:

```bash
curl -v --max-time 5 http://127.0.0.1:8080/
```

### Observed result

- TCP connection to port `8080` succeeded.
- The application returned `HTTP/1.0 200 OK`.
- Server: `SimpleHTTP/0.6 Python/3.12.3`
- Response body: `SRE Lab application is running`

### What this means

The local service is reachable and returned a successful HTTP response. A `200 OK` status means the request was successfully handled.

The `-v` option displays connection details, request headers, response headers, and other diagnostic information.

## 2. Test HTTPS and TLS Verification

### Command

Run inside the Ubuntu container:

```bash
curl -v --max-time 10 https://google.com
```

### Observed result

- The hostname resolved to an IPv4 address.
- A TCP connection to port `443` succeeded.
- The TLS handshake completed.
- The certificate matched `google.com`.
- Certificate verification succeeded.
- HTTP/2 was negotiated.
- The server returned `HTTP/2 301` and redirected the request to `https://www.google.com/`.

### What this means

HTTPS requires a successful TCP connection followed by TLS negotiation and certificate validation before the HTTP response can be processed.

A successful TLS handshake does not necessarily mean the final HTTP status will be `200`. The server may return a redirect or another HTTP status.

## 3. Follow HTTP Redirects

### Command

```bash
curl -sS -L -o /dev/null -w 'Final HTTP status: %{http_code}\nRedirects followed: %{num_redirects}\nTotal time: %{time_total}s\n' --max-time 10 https://google.com
```

### Observed result

```text
Final HTTP status: 200
Redirects followed: 1
Total time: 0.645809s
```

### What this means

- `-L` follows redirects.
- `-o /dev/null` discards the response body.
- `-w` prints selected request metrics.
- The original URL returned a redirect, and following it led to a successful response.

Redirects are not automatically errors. Check the `Location` header and the final response status.

## 4. Troubleshoot an Expired TLS Certificate

### Command

```bash
curl -I --max-time 5 https://expired.badssl.com/
```

### Observed result

```text
curl: (60) SSL certificate problem: certificate has expired
```

This is an intentional test using a public endpoint designed to demonstrate an expired certificate.

### What this means

The request progressed far enough to receive a certificate, but certificate validation failed because the certificate had expired.

In production, investigate:

- Certificate expiration date.
- Certificate renewal and deployment status.
- Certificate chain and issuer.
- Correct certificate being served by the endpoint or load balancer.
- System clock, if certificate validity dates appear incorrect.

**Security note:** Do not treat disabling certificate verification with `curl -k` as a production fix. It bypasses an important security check.

## 5. HTTP and HTTPS Troubleshooting Workflow

When a website or API is unavailable, troubleshoot in layers:

1. **DNS:** Does the hostname resolve?
2. **TCP:** Can the client establish a connection to the target port?
3. **TLS:** Does the handshake complete? Is the certificate valid and trusted?
4. **HTTP:** What status code and response headers does the server return?
5. **Application:** Do application logs show errors, timeouts, or unhealthy dependencies?

Useful commands:

```bash
# Check DNS resolution
getent hosts example.com

# Test TCP connectivity and request details
curl -v --connect-timeout 3 --max-time 10 https://example.com/

# Show response headers
curl -I --max-time 10 https://example.com/

# Follow redirects and show the final status
curl -sS -L -o /dev/null -w 'HTTP %{http_code}\n' --max-time 10 https://example.com/
```

Replace `example.com` with the actual hostname being investigated.

## 6. Common Symptoms and Likely Investigation Areas

| Symptom | What to investigate |
|---|---|
| DNS resolution fails | DNS configuration, resolver availability, hostname |
| Connection refused | Target port, listening service, firewall or port publishing |
| Connection timeout | Routing, packet filtering, network reachability, overloaded service |
| TLS certificate error | Expiration, hostname mismatch, trust chain, system clock |
| HTTP 301 or 302 | Redirect destination and redirect configuration |
| HTTP 401 or 403 | Authentication, authorization, access policies |
| HTTP 404 | URL path, route configuration, application endpoint |
| HTTP 500 | Application errors and server logs |
| HTTP 502 or 503 | Upstream health, reverse proxy, service availability |
| HTTP 504 | Upstream response timeouts and dependency latency |

These are starting points for investigation, not definitive diagnoses. Confirm the cause using evidence from logs, metrics, and network tests.

## 7. Key Learnings

- HTTP status codes describe the result of an HTTP request.
- HTTPS adds TLS negotiation and certificate validation.
- A redirect is different from a failed connection.
- `curl -v` helps identify which stage of a request is failing.
- A certificate error should be investigated rather than bypassed.
- Troubleshooting is more efficient when performed layer by layer.

## Production Troubleshooting Checklist

- [ ] Confirm hostname resolution.
- [ ] Verify TCP connectivity to the destination port.
- [ ] Check TLS handshake and certificate validity for HTTPS.
- [ ] Inspect HTTP status, headers, and redirect destinations.
- [ ] Review application and proxy logs.
- [ ] Correlate findings with monitoring metrics and recent deployments.

## Lab Status

**Completed:** HTTP response inspection, HTTPS/TLS verification, redirect handling, and expired-certificate error analysis.

**Next lab:** Lab 06 — TLS.
