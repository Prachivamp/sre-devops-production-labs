# Lab 12: Production Network Incident Simulation

## Objective

Practice a basic production incident workflow using Docker: verify application health, identify a port mismatch, investigate hostname resolution failures, inspect network membership, and confirm recovery.

## Environment

- Docker bridge network: `lab12-incident-network`
- Application container: `lab12-app`
- Application image: `hashicorp/http-echo:1.0`
- Application listening port: `8080`
- Application response: `Production application is healthy`

## 1. Create the isolated network

```bash
docker network create lab12-incident-network
```

This creates a separate Docker network for the lab.

## 2. Start the application

```bash
docker run -d \
  --name lab12-app \
  --network lab12-incident-network \
  hashicorp/http-echo:1.0 \
  -listen=:8080 \
  -text="Production application is healthy"
```

Inspect its state and configured command:

```bash
docker inspect lab12-app \
  --format 'Status={{.State.Status}} Image={{.Config.Image}} Command={{json .Config.Cmd}}'
```

Observed result:

- Status: `running`
- Image: `hashicorp/http-echo:1.0`
- Listening configuration: `:8080`

Note: `running` confirms that the container process is running; an HTTP request is still needed to verify application reachability.

## 3. Establish the healthy baseline

```bash
docker run --rm \
  --network lab12-incident-network \
  curlimages/curl:latest \
  -sS -i http://lab12-app:8080
```

Observed result:

```text
HTTP/1.1 200 OK
Production application is healthy
```

**Diagnosis:** The application responds successfully through its Docker network hostname on port 8080.

## 4. Incident A — Connection refused

Send a request to port 8081:

```bash
docker run --rm \
  --network lab12-incident-network \
  curlimages/curl:latest \
  -v --connect-timeout 3 http://lab12-app:8081
```

Observed symptom:

```text
Host lab12-app:8081 was resolved.
connect to 172.24.0.2 port 8081 failed: Connection refused
```

### Investigation

The hostname resolves to an IP address, but the application is configured to listen on port 8080, not 8081.

### Root cause

Port mismatch: the request targets a port where no service is listening.

### Resolution and verification

Use the correct port:

```bash
docker run --rm \
  --network lab12-incident-network \
  curlimages/curl:latest \
  -sS -i http://lab12-app:8080
```

Observed recovery: HTTP 200 OK.

**Learning:** Connection refused usually means the destination was reached but no process accepted the connection on that port. Verify the listening port, service configuration, and port mappings where applicable.

## 5. Incident B — Hostname resolution failure

Request a hostname that does not exist:

```bash
docker run --rm \
  --network lab12-incident-network \
  curlimages/curl:latest \
  -v --connect-timeout 3 http://lab12-missing-app:8080
```

Observed symptom:

```text
Resolving timed out after 3003 milliseconds
curl: (28) Resolving timed out
```

### Investigation

Inspect the Docker network:

```bash
docker network inspect lab12-incident-network
```

Observed details:

- Network driver: `bridge`
- Application container: `lab12-app`
- Application IP: `172.24.0.2`

The application is attached to the network. A subsequent request to `http://lab12-app:8080` returned HTTP 200.

### Diagnosis

The requested hostname, `lab12-missing-app`, was intentionally chosen because it does not exist on the network. The failed lookup is consistent with a missing hostname, but the timeout alone does not prove a general Docker DNS outage.

**Learning:** Distinguish a missing service name from a network-wide DNS problem. If multiple valid container names fail to resolve, investigate network membership, Docker DNS, and network connectivity.

## 6. Troubleshooting a minimal container image

Attempting to run a shell inside the application container:

```bash
docker exec lab12-app sh -c 'ps'
```

failed because `sh` is not available in this minimal image.

Instead, inspect container metadata:

```bash
docker inspect lab12-app \
  --format 'Status={{.State.Status}} Image={{.Config.Image}} Command={{json .Config.Cmd}}'
```

**Learning:** Minimal production images may not include a shell or diagnostic utilities. Use available external diagnostic containers and Docker inspection commands when appropriate.

## 7. Production incident workflow

1. **Confirm impact:** Check the failing endpoint, HTTP status, error rate, and affected service.
2. **Collect evidence:** Capture the exact error and relevant timestamps.
3. **Isolate the layer:** Check hostname resolution, network connectivity, port availability, and application health separately.
4. **Verify configuration:** Compare the requested hostname and port with the container's network membership and listening configuration.
5. **Mitigate:** Correct the hostname or port configuration, or restore the affected network/service if evidence identifies that issue.
6. **Verify recovery:** Repeat the original request and check the expected status and response.
7. **Document:** Record symptoms, evidence, root cause, corrective action, and follow-up prevention.

Do not restart containers or change network configuration without evidence that the action is necessary.

## 8. Key interview takeaways

- **HTTP 200:** The tested endpoint returned a successful HTTP response.
- **Connection refused:** The connection reached a destination, but the target port did not accept it.
- **DNS resolution failure:** The hostname could not be resolved; determine whether the name is missing or DNS is unhealthy.
- **Container running:** Does not, by itself, prove that the application is healthy.
- **Network inspection:** Helps verify network configuration and attached containers.
- **Recovery validation:** Always repeat the original failing request after applying a fix.

## Cleanup (optional)

Only run these commands when you intentionally want to remove this lab:

```bash
docker rm -f lab12-app
docker network rm lab12-incident-network
```

These commands remove the lab application container and network. Do not run them if you want to keep practicing with this environment.
