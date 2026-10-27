# Lab 09 — Container Logs and Debugging

## Objective

Practice investigating application logs, filtering errors, following logs in real time, diagnosing exited containers, and distinguishing application-level failures from container crashes.

## Lab environment

This lab uses separate test containers so existing lab containers and volumes remain untouched.

| Container | Purpose |
|---|---|
| `docker-lab09-logs` | Generates continuous INFO logs and a simulated ERROR |
| `docker-lab09-crash` | Simulates an application process exiting with code 1 |
| `docker-lab09-success` | Demonstrates a successful process exit with code 0 |
| `docker-lab09-web-error` | Returns HTTP 200 on `/` and HTTP 500 on `/error` |

## 1. Inspect container logs

Display the logs:

```bash
docker logs docker-lab09-logs
```

Filter for errors:

```bash
docker logs docker-lab09-logs 2>&1 | grep ERROR
```

Observed result:

```text
ERROR request=3 simulated_failure
```

**Lesson:** `docker logs` retrieves the container's standard output and standard error. Filtering with `grep` helps isolate relevant messages during troubleshooting.

## 2. Follow logs in real time

```bash
docker logs --follow --tail 5 docker-lab09-logs
```

- `--follow` streams new log entries.
- `--tail 5` initially displays the last five lines.
- Press `Ctrl + C` to stop following logs. This does not stop the container.

Verify the container remains running:

```bash
docker ps --filter name=docker-lab09-logs
```

## 3. Inspect timestamps and recent entries

Show Docker log timestamps:

```bash
docker logs --timestamps --tail 10 docker-lab09-logs
```

Show only the latest three entries:

```bash
docker logs --tail 3 docker-lab09-logs
```

**Lesson:** Timestamps help correlate application events with alerts, deployments, and incident timelines. Docker timestamps and timestamps printed by the application may both appear.

## 4. Diagnose a failed container

The crash simulation was started with:

```bash
docker run --name docker-lab09-crash alpine:latest \
  sh -c 'echo "INFO Application starting"; echo "ERROR Missing required configuration"; exit 1'
```

Inspect stopped containers:

```bash
docker ps -a --filter name=docker-lab09-crash
```

Read its logs:

```bash
docker logs docker-lab09-crash
```

Inspect the container state:

```bash
docker inspect docker-lab09-crash \
  --format 'Status={{.State.Status}} ExitCode={{.State.ExitCode}} OOMKilled={{.State.OOMKilled}} Error={{.State.Error}} FinishedAt={{.State.FinishedAt}}'
```

Observed evidence:

- Status: `exited`
- Exit code: `1`
- `OOMKilled=false`
- The application log included `ERROR Missing required configuration`.

**Diagnosis:** The simulated application process exited with an error. The log suggests missing configuration, but in a real incident the application's startup code and configuration would need to be examined to confirm the root cause.

## 5. Compare a successful process exit

The successful task was started with:

```bash
docker run --name docker-lab09-success alpine:latest \
  sh -c 'echo "INFO Task started"; echo "INFO Task completed successfully"; exit 0'
```

Inspect its state:

```bash
docker inspect docker-lab09-success \
  --format 'Status={{.State.Status}} ExitCode={{.State.ExitCode}} OOMKilled={{.State.OOMKilled}}'
```

Observed result: `Status=exited ExitCode=0 OOMKilled=false`.

**Lesson:** An exited container is not automatically a failure. A one-off job that completes with exit code `0` is behaving as expected. An unexpected exit from a long-running service requires investigation.

## 6. Simulate an HTTP 500 application error

The test web container publishes host port `8091` to container port `8000`, bound to localhost.

Test the normal endpoint:

```bash
curl -i http://127.0.0.1:8091/
```

Observed result: HTTP 200 OK.

Test the failing endpoint:

```bash
curl -i http://127.0.0.1:8091/error
```

Observed result: HTTP 500 Internal Server Error.

Get only the HTTP status code:

```bash
curl -s -o /dev/null -w 'HTTP status: %{http_code}\n' \
  http://127.0.0.1:8091/error
```

Observed result:

```text
HTTP status: 500
```

Inspect the application logs:

```bash
docker logs --tail 20 docker-lab09-web-error
```

Filter for HTTP 500 responses:

```bash
docker logs docker-lab09-web-error 2>&1 | grep '500'
```

Observed log entries included:

```text
"GET / HTTP/1.1" 200 -
"GET /error HTTP/1.1" 500 -
```

## 7. Verify container state

Inspect the web container:

```bash
docker inspect docker-lab09-web-error \
  --format 'Status={{.State.Status}} Running={{.State.Running}} ExitCode={{.State.ExitCode}}'
```

Inspect restart count:

```bash
docker inspect docker-lab09-web-error \
  --format 'Running={{.State.Running}} Status={{.State.Status}} RestartCount={{.RestartCount}}'
```

Observed result:

```text
Running=true Status=running RestartCount=0
```

**Diagnosis:** The container remained running and had not restarted, even though `/error` returned HTTP 500.

This is an application-level failure, not evidence of a container crash. The test server deliberately returns HTTP 500 for that route.

## 8. Troubleshooting reference

| Command | What it helps establish |
|---|---|
| `docker ps` | Which containers are running |
| `docker ps -a` | Running and stopped containers |
| `docker logs <container>` | Application output and errors |
| `docker logs --tail 50 <container>` | Most recent log entries |
| `docker logs --follow <container>` | New log entries as they arrive |
| `docker logs --timestamps <container>` | Docker timestamps for log events |
| `docker inspect <container>` | Detailed container state and configuration |
| `docker inspect <container> --format '{{.State.ExitCode}}'` | Main process exit code |
| `docker stats` | Live resource usage of running containers |
| `curl -i <endpoint>` | HTTP status and response headers |

## 9. Production SRE investigation sequence

When a service is failing:

1. **Confirm the symptom:** Reproduce the failure with a request or health check.
2. **Check container state:** Determine whether the container is running, restarting, or exited.
3. **Read logs:** Search for errors around the time of the incident.
4. **Inspect exit information:** Check exit code, OOM status, restart count, and container-level errors.
5. **Check resources:** Use `docker stats` and other available metrics to investigate CPU and memory pressure.
6. **Correlate evidence:** Compare timestamps, HTTP responses, logs, deployments, and alerts.
7. **Mitigate safely:** Choose an action based on the evidence; do not restart or delete containers blindly.
8. **Verify recovery:** Retest the failing endpoint and monitor for recurring errors.

## Key takeaways

- A running container does not guarantee a healthy application.
- `docker logs` and log filtering help narrow down errors.
- Exit code `0` indicates successful process completion; nonzero codes indicate an error or abnormal termination that needs interpretation.
- `OOMKilled=false` means Docker did not record an OOM kill for that container state.
- HTTP 500 can occur while the container remains running.
- Logs, container state, HTTP status, and resource metrics should be correlated before deciding on a root cause.

## Lab status

- [x] Read and filter container logs
- [x] Follow logs in real time
- [x] Inspect timestamps and recent entries
- [x] Investigate a container that exits with code 1
- [x] Compare a successful exit with code 0
- [x] Reproduce and inspect HTTP 500 responses
- [x] Correlate application logs with container state
