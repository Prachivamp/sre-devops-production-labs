# Lab 10: Reverse Proxy and Load Balancer Troubleshooting

## Objective

Build and troubleshoot an Nginx reverse proxy that distributes HTTP requests across two backend containers. Simulate a backend failure, investigate proxy logs, configure retry behavior, and verify recovery.

## Architecture

```text
Client (Mac)
    |
    | http://localhost:8081
    v
Nginx Reverse Proxy (lab10-proxy)
    |
    |---- lab10-backend1:5678
    |
    |---- lab10-backend2:5678

All containers communicate over lab10-network.
```

## Environment

- Docker Desktop on macOS
- Nginx Alpine as the reverse proxy
- Two `hashicorp/http-echo:1.0` backend containers
- Docker user-defined bridge network: `lab10-network`
- Host port `8081` mapped to Nginx port `80`

## 1. Create the Docker network and backend containers

```bash
docker network create lab10-network

docker run -d \
  --name lab10-backend1 \
  --network lab10-network \
  hashicorp/http-echo:1.0 \
  -text="Hello from Backend 1"

docker run -d \
  --name lab10-backend2 \
  --network lab10-network \
  hashicorp/http-echo:1.0 \
  -text="Hello from Backend 2"
```

### Test backend connectivity

```bash
docker run --rm --network lab10-network \
  curlimages/curl:latest -sS \
  http://lab10-backend1:5678

docker run --rm --network lab10-network \
  curlimages/curl:latest -sS \
  http://lab10-backend2:5678
```

Expected responses:

```text
Hello from Backend 1
Hello from Backend 2
```

A temporary curl container was used because the backend image did not include the expected troubleshooting utility.

## 2. Configure Nginx

File: `nginx.conf`

```nginx
events {}

http {
    upstream backend_servers {
        server lab10-backend1:5678 max_fails=1 fail_timeout=10s;
        server lab10-backend2:5678 max_fails=1 fail_timeout=10s;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://backend_servers;

            proxy_connect_timeout 2s;
            proxy_read_timeout 5s;

            proxy_next_upstream error timeout;
            proxy_next_upstream_tries 2;
        }
    }
}
```

### What the configuration does

- `upstream`: defines the backend server group.
- `proxy_pass`: forwards incoming requests to that group.
- `max_fails=1`: configures passive failure tracking with one qualifying failure.
- `fail_timeout=10s`: defines the failure-counting period and how long a server can be considered unavailable.
- `proxy_connect_timeout 2s`: limits the time allowed to establish an upstream connection.
- `proxy_read_timeout 5s`: limits the interval between successive upstream read operations.
- `proxy_next_upstream error timeout`: allows a retry for qualifying connection errors and timeouts.
- `proxy_next_upstream_tries 2`: limits the number of upstream attempts to two.

These settings provide passive failure handling, not continuous active health checks.

## 3. Start the reverse proxy

```bash
docker run -d \
  --name lab10-proxy \
  --network lab10-network \
  -p 8081:80 \
  -v "$PWD/02-Networking/10-Reverse Proxy and Load Balancer Troubleshooting/nginx.conf:/etc/nginx/nginx.conf:ro" \
  nginx:alpine
```

Validate the configuration:

```bash
docker exec lab10-proxy nginx -t
```

Reload Nginx after configuration changes:

```bash
docker exec lab10-proxy nginx -s reload
```

## 4. Verify reverse proxy routing

From the Mac terminal:

```bash
curl -i http://localhost:8081
```

The response returned HTTP 200 with a backend response body.

Send several requests:

```bash
for i in {1..6}; do
  curl -sS http://localhost:8081
  echo
done
```

### Observation

Responses alternated between Backend 1 and Backend 2.

**Learning:** Nginx uses round-robin load balancing by default when multiple upstream servers are configured without a different balancing method.

## 5. Simulate a backend failure

Stop Backend 1:

```bash
docker stop lab10-backend1
```

Send requests through Nginx:

```bash
curl -sS --max-time 5 http://localhost:8081
```

Inspect the proxy error log:

```bash
docker logs --tail 100 lab10-proxy
```

### Initial failure observation

Before the retry and passive failure settings were added, some requests succeeded through Backend 2 while others timed out when Nginx selected the unavailable Backend 1.

An observed error included:

```text
connect() failed (113: Host is unreachable)
while connecting to upstream
```

The log identified the unavailable upstream address and port.

Some requests also produced HTTP status `499` in Nginx logs. This indicates that the client closed the request before Nginx could finish responding; in this test, curl's timeout was a likely cause.

**Important:** A `499` is not a backend HTTP response. It is an Nginx log status associated with a client closing the connection.

## 6. Configure retry and passive failure handling

The upstream definitions were updated with `max_fails=1` and `fail_timeout=10s`. The location block was updated with connection/read timeouts and upstream retry settings.

Validate and reload:

```bash
docker exec lab10-proxy nginx -t
docker exec lab10-proxy nginx -s reload
```

Repeat the failure test:

```bash
docker stop lab10-backend1

for i in {1..4}; do
  curl -sS --max-time 5 http://localhost:8081
  echo
done
```

### Observation

In the retest, all four requests returned:

```text
Hello from Backend 2
```

This demonstrated successful service through the surviving backend in this test.

This behavior is not a guarantee that every possible backend failure will be handled without errors. Nginx's passive failure tracking depends on observed failures and its configured retry behavior.

## 7. Restore the backend and verify recovery

```bash
docker start lab10-backend1

docker run --rm --network lab10-network \
  curlimages/curl:latest -sS \
  http://lab10-backend1:5678

curl -sS http://localhost:8081
```

Both backend connectivity and proxy routing were verified after recovery.

## Troubleshooting commands

```bash
docker ps
docker network inspect lab10-network
docker logs --tail 100 lab10-proxy
docker exec lab10-proxy nginx -t
docker exec lab10-proxy nginx -s reload
curl -i --max-time 5 http://localhost:8081
```

## SRE investigation approach

When a service behind a reverse proxy becomes slow or unavailable:

1. **Confirm the impact:** Check request success rate, HTTP status codes, latency, and affected routes.
2. **Inspect proxy logs:** Look for connection failures, upstream timeouts, and repeated errors for a particular backend.
3. **Check backend health:** Verify the container or service is running and listening on the expected port.
4. **Check networking and name resolution:** Verify the proxy and backend share a network, and that the backend name resolves correctly.
5. **Check timeouts and retries:** Confirm their values match the application's behavior and that retries will not amplify load.
6. **Mitigate:** Restore the backend, remove an unhealthy target from service, or route traffic to healthy instances where appropriate.
7. **Verify recovery:** Repeat requests and check error rate and latency.
8. **Prevent recurrence:** Investigate the underlying failure and improve health checks, alerting, capacity, or deployment safety.

## Key interview takeaways

- A reverse proxy receives client requests and forwards them to backend services.
- A load balancer distributes traffic across multiple backend instances.
- Nginx's default upstream method is round robin.
- A running container does not automatically mean its application is healthy.
- `Host is unreachable` points toward a connectivity or network-path problem.
- Connection refused generally indicates that the destination is reachable but no process is accepting the connection on that port.
- Upstream timeouts indicate that an operation did not complete within its configured timeout; investigate connectivity, application responsiveness, and dependencies.
- HTTP `502` means a gateway/proxy received an invalid response from an upstream or could not complete the upstream exchange.
- Nginx log status `499` indicates the client closed the request before the proxy finished.
- Retries can improve resilience but should be bounded and used carefully, especially for non-idempotent operations such as payment requests.
- Passive failure tracking is different from active health checks.

## Cleanup

Only run these commands when you intentionally want to remove this lab:

```bash
docker rm -f lab10-proxy lab10-backend1 lab10-backend2
docker network rm lab10-network
```

These cleanup commands remove the Lab 10 resources. Do not run them while you still want to use the lab.
