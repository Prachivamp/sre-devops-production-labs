# Lab 20: Linux Troubleshooting — Mini Production Incident

## Objective

Investigate and resolve an application accessibility issue using a structured SRE troubleshooting process.

## Incident Summary

**Symptom:** The application was accessible inside its Docker container but could not be reached from the Mac host.

**Root cause:** The original Docker container was created without publishing port 8080 to the host.

**Resolution:** Preserved the original container, created a backup image, recreated the container with port publishing, restarted the HTTP server, and verified external access.

## Step 1: Check Application Health

```bash
/opt/myapp/scripts/health-check.sh
echo $?
```

The health check reported:

* Process: RUNNING
* Port 8080: LISTENING
* HTTP: HEALTHY
* Exit code: 0

## Step 2: Check Listening Ports

```bash
ss -lntp
```

The Python HTTP server was listening on `0.0.0.0:8080` inside the original container.

## Step 3: Test HTTP Locally

```bash
curl -i --max-time 5 http://127.0.0.1:8080/
```

The original container returned `HTTP/1.0 200 OK`.

## Step 4: Inspect Logs

```bash
tail -n 20 /opt/myapp/logs/http-server.log
tail -n 20 /opt/myapp/logs/app.log
```

The recent HTTP server log entries showed successful local requests. The application log contained older database errors, but these did not establish the cause of the current accessibility issue.

## Step 5: Check Docker Port Publishing

On the Mac host:

```bash
docker ps --filter name=sre-linux-lab
docker port sre-linux-lab
docker inspect sre-linux-lab --format '{{json .HostConfig.PortBindings}}'
```

**Finding:** The original container had no published ports. The port bindings were `{}` and `docker port` returned no mappings.

A host request failed:

```bash
curl -i --max-time 5 http://127.0.0.1:8080/
```

## Step 6: Preserve the Original Container

Created a backup image:

```bash
docker commit sre-linux-lab sre-linux-lab-backup:before-port-fix
```

Stopped and renamed the original container rather than deleting it:

```bash
docker stop sre-linux-lab
docker rename sre-linux-lab sre-linux-lab-original
```

## Step 7: Recreate with Port Publishing

```bash
docker run -dit \
  --name sre-linux-lab \
  -p 8080:8080 \
  sre-linux-lab-backup:before-port-fix \
  bash
```

The `-p 8080:8080` option publishes host port 8080 to container port 8080.

Started the HTTP server inside the replacement container:

```bash
docker exec -it sre-linux-lab bash
cd /opt/myapp/web
python3 -m http.server 8080 --bind 0.0.0.0 >> /opt/myapp/logs/http-server.log 2>&1 < /dev/null &
```

## Step 8: Verify Recovery

From the Mac host:

```bash
curl -i --max-time 5 http://127.0.0.1:8080/
docker port sre-linux-lab
```

**Result:** The HTTP request returned `200 OK`, and Docker reported host port 8080 mapped to container port 8080.

## Root Cause

The application was healthy inside the container, but Docker had no host port mapping. Therefore, a request to `127.0.0.1:8080` on the Mac could not reach the application.

## Prevention

* Publish required ports when creating containers.
* Verify port mappings during deployment.
* Test application health from both inside the container and outside it.
* Use readiness and external synthetic checks, not only process checks.
* Preserve persistent application data outside the container writable layer for production workloads.
* Use a documented incident checklist and verify recovery after a fix.

## Troubleshooting Workflow

**Observe → Check process → Check port → Test local HTTP → Inspect logs → Check Docker networking → Fix → Verify externally → Document**

## Lab Status

Completed: Linux and Docker troubleshooting of a simulated application availability incident.
