# Linux Lab 16: Shell Scripting and Health Checks

## Objective
Create a Bash script that checks application process status, port availability, and HTTP response.

## Scenario
An application may be unavailable even when its process exists. A repeatable health check helps identify failures quickly.

## Environment
- Ubuntu 24.04 running in Docker
- Python HTTP server on port 8080
- Bash health-check script

## Script location
`/opt/myapp/scripts/health-check.sh`

## Checks performed
1. Process check using `pgrep`
2. TCP listening-port check using `ss`
3. HTTP response check using `curl`
4. Overall status based on the results
5. Exit code: 0 for success, 1 for failure

## Commands practiced
- `if`, `then`, `else`, `fi`
- Variables
- `pgrep`
- `ss`
- `grep -q`
- `curl -fsS`
- Output redirection with `/dev/null`
- `exit` status codes
- Background processes using `&`
- Stopping processes with `kill`

## Failure test
Stopped the HTTP server and ran the health-check script.

Expected results:
- Process: DOWN
- Port 8080: NOT LISTENING
- HTTP: UNHEALTHY
- Overall Status: UNHEALTHY
- Exit code: 1

## Recovery test
Restarted the HTTP server and reran the health check.

Expected results:
- Process: RUNNING
- Port 8080: LISTENING
- HTTP: HEALTHY
- Overall Status: HEALTHY
- Exit code: 0

## Production relevance
Health-check scripts can support operational automation and CI/CD validation. Real production checks should use the application's dedicated health endpoint where available, handle timeouts, and avoid relying only on process existence.

## Key takeaway
A running process does not guarantee a healthy application. Verify the process, listening port, and application response separately.
