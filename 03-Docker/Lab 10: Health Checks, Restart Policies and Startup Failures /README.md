# Docker Lab 10: Health Checks, Restart Policies and Startup Failures

## Objective

Learn how to distinguish container runtime state from application health, configure Docker health checks and restart policies, and troubleshoot application startup failures using `docker inspect` and `docker logs`.

## 1. Health Check on a Healthy Container

Created an Nginx container with a health check:

```bash
docker run -d \
  --name docker-lab10-health \
  --health-cmd="wget -q --spider http://127.0.0.1/ || exit 1" \
  --health-interval=10s \
  --health-timeout=3s \
  --health-retries=3 \
  --health-start-period=5s \
  nginx:alpine
```

Inspected its state:

```bash
docker inspect docker-lab10-health \
  --format='Status={{.State.Status}} Health={{.State.Health.Status}} RestartCount={{.RestartCount}}'
```

Observed:

```text
Status=running Health=healthy RestartCount=0
```

Inspected health-check history:

```bash
docker inspect docker-lab10-health \
  --format='{{range .State.Health.Log}}{{println "ExitCode=" .ExitCode "Output=" .Output}}{{end}}'
```

All recorded checks returned exit code `0`.

### Key concepts

- `running` describes the container's main process state.
- `healthy` means the configured health check is passing.
- A health check must test a meaningful application condition.
- A running container is not necessarily a healthy application.

## 2. Simulating an Unhealthy Application

Created a container with a deliberately incorrect health-check endpoint:

```bash
docker run -d \
  --name docker-lab10-unhealthy \
  --health-cmd="wget -q --spider http://127.0.0.1/nonexistent-health-endpoint || exit 1" \
  --health-interval=5s \
  --health-timeout=3s \
  --health-retries=2 \
  nginx:alpine
```

Inspected health status:

```bash
docker inspect docker-lab10-unhealthy \
  --format='Status={{.State.Status}} Health={{.State.Health.Status}} RestartCount={{.RestartCount}}'
```

Observed:

```text
Status=running Health=unhealthy RestartCount=0
```

Inspected the failure details:

```bash
docker inspect docker-lab10-unhealthy \
  --format='{{range .State.Health.Log}}{{println "ExitCode=" .ExitCode "Output=" .Output}}{{end}}'
```

Observed repeated failures:

```text
ExitCode=1
Output=wget: server returned error: HTTP/1.1 404 Not Found
```

### Root cause

Nginx was still running, but the health-check URL returned HTTP 404. The configured check therefore failed repeatedly, and Docker marked the container unhealthy.

**Important:** Docker does not automatically restart a container solely because it becomes unhealthy. A separate health-aware orchestration or remediation mechanism is needed if unhealthy containers must be restarted automatically.

## 3. Testing a Restart Policy

Created a container whose process deliberately exited unsuccessfully:

```bash
docker run -d \
  --name docker-lab10-restart \
  --restart=on-failure:3 \
  alpine:latest \
  sh -c 'echo "Simulating application failure"; exit 1'
```

Inspected the result:

```bash
docker inspect docker-lab10-restart \
  --format='Status={{.State.Status}} ExitCode={{.State.ExitCode}} RestartCount={{.RestartCount}} RestartPolicy={{.HostConfig.RestartPolicy.Name}}'
```

Observed:

```text
Status=exited ExitCode=1 RestartCount=3 RestartPolicy=on-failure
```

### What this proves

- The process exited with a nonzero code.
- Docker performed three restarts.
- The process continued failing, so the container eventually exited.
- A restart policy can recover from transient failures but cannot fix a persistent application defect.

## 4. Inspecting a Container Without a Restart Policy

Inspected the original healthy container:

```bash
docker inspect docker-lab10-health \
  --format='Status={{.State.Status}} Health={{.State.Health.Status}} RestartPolicy={{.HostConfig.RestartPolicy.Name}} RestartCount={{.RestartCount}}'
```

Observed:

```text
Status=running Health=healthy RestartPolicy=no RestartCount=0
```

The container was healthy and had no restart policy configured.

## 5. Simulating an Application Startup Failure

Created a container with a nonexistent Python script:

```bash
docker run -d \
  --name docker-lab10-startup-failure \
  --restart=no \
  python:3.12-slim \
  python /app/missing_app.py
```

Inspected the state:

```bash
docker inspect docker-lab10-startup-failure \
  --format='Status={{.State.Status}} ExitCode={{.State.ExitCode}} Error={{.State.Error}}'
```

Observed:

```text
Status=exited ExitCode=2 Error=
```

Inspected application logs:

```bash
docker logs docker-lab10-startup-failure
```

Observed:

```text
python: can't open file '/app/missing_app.py': [Errno 2] No such file or directory
```

### Root cause

The Python process could not find the requested script and exited. Docker reported the process exit status, while the application error appeared in the logs.

### Troubleshooting approach

1. Check the container state and exit code.
2. Read the container logs.
3. Verify the image, working directory, startup command, and required files.
4. Inspect the Dockerfile's `COPY`, `WORKDIR`, and `CMD` instructions.
5. Correct the root cause before restarting the application.

## 6. Production Troubleshooting Commands

```bash
# List containers and their states
docker ps -a

# Inspect state, health and restart count
docker inspect CONTAINER_NAME \
  --format='Status={{.State.Status}} Health={{if .State.Health}}{{.State.Health.Status}}{{else}}not-configured{{end}} RestartCount={{.RestartCount}}'

# Read recent logs
docker logs --tail 100 CONTAINER_NAME

# Follow logs in real time
docker logs --follow --tail 50 CONTAINER_NAME

# Inspect health-check history
docker inspect CONTAINER_NAME \
  --format='{{json .State.Health.Log}}'

# Inspect configured restart policy
docker inspect CONTAINER_NAME \
  --format='{{json .HostConfig.RestartPolicy}}'
```

Replace `CONTAINER_NAME` with the container you are investigating.

## 7. Key Takeaways

- Container state and application health are different signals.
- An unhealthy container can remain running.
- Restart policies react to process termination, not health-check failure alone.
- `on-failure:3` retries a failing process up to the configured retry limit.
- Exit codes and logs help distinguish startup errors from health-check failures.
- Restarting repeatedly without fixing the root cause can create a crash loop.
- Health checks should verify meaningful application behavior, not just the existence of a process.

## Lab Status

- [x] Configured a successful health check.
- [x] Inspected health-check history.
- [x] Simulated and diagnosed an unhealthy container.
- [x] Tested `on-failure:3` restart behavior.
- [x] Investigated an application startup failure.
- [x] Practiced production-style Docker troubleshooting.
