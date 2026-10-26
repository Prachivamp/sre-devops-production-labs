# Lab 06 — Dockerfiles and Image Builds

## Objective
Build a custom Docker image, run a Python HTTP application as a non-root user, configure its port at runtime, and troubleshoot a failed container startup.

## 1. Application and Dockerfile

Created `app/app.py`, a small Python HTTP server with:
- `/` — returns a greeting
- `/health` — returns `OK`
- `APP_PORT` — controls the listening port, defaulting to `8000`

Dockerfile:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY app/app.py ./app.py

ENV APP_PORT=8000

EXPOSE 8000

USER 10001:10001

CMD ["python", "-u", "app.py"]
```

### Dockerfile instruction summary

| Instruction | Purpose |
|---|---|
| `FROM` | Defines the base image |
| `WORKDIR` | Sets the working directory |
| `COPY` | Copies application files into the image |
| `ENV` | Sets a default environment variable |
| `EXPOSE` | Documents the container port |
| `USER` | Runs the application as a non-root user |
| `CMD` | Defines the default startup command |

## 2. Build and inspect the image

```bash
docker build -t sre-lab06-app:1.0 .
docker image inspect sre-lab06-app:1.0 \
  --format 'Image={{.RepoTags}} OS={{.Os}} Architecture={{.Architecture}}'
```

**Result:** Image built successfully for Linux ARM64.

## 3. Run and test the application

```bash
docker run -d \
  --name docker-lab06-app \
  -p 127.0.0.1:8000:8000 \
  sre-lab06-app:1.0
```

Validated the endpoints:

```bash
curl -i http://127.0.0.1:8000/
curl -i http://127.0.0.1:8000/health
```

**Result:** Both endpoints returned HTTP 200 OK.

## 4. Runtime configuration and port mapping

Started a second container with a custom application port:

```bash
docker run -d \
  --name docker-lab06-custom-port \
  -e APP_PORT=9000 \
  -p 127.0.0.1:8001:9000 \
  sre-lab06-app:1.0
```

Tested:

```bash
curl -i http://127.0.0.1:8001/health
```

**Result:** HTTP 200 OK.

The mapping was host port `8001` to container port `9000`. The application listened on port `9000` because `APP_PORT` was overridden at runtime.

## 5. Startup failure simulation

Overrode the image's default command:

```bash
docker run -d \
  --name docker-lab06-broken \
  sre-lab06-app:1.0 \
  python missing_app.py
```

Inspected status and logs:

```bash
docker ps -a --filter name=docker-lab06-broken
docker logs docker-lab06-broken
```

Observed:

```text
Exited (2)
python: can't open file '/app/missing_app.py': [Errno 2] No such file or directory
```

### Root cause

The container startup command referenced a nonexistent Python file. The container exited because Python could not open the requested script.

Verified the actual image contents:

```bash
docker run --rm \
  --entrypoint sh \
  sre-lab06-app:1.0 \
  -c 'pwd; ls -l /app; ls -l /app/app.py'
```

**Result:** `/app/app.py` existed in the image. The failure was caused by the incorrect startup command, not by a missing application file in the image.

## Troubleshooting approach

1. Check container status using `docker ps -a`.
2. Review startup errors with `docker logs`.
3. Inspect the image's `CMD`, user, environment, and exposed ports.
4. Verify the working directory and files inside the image.
5. Correct the startup command or rebuild the image if required files are missing.
6. Retest the application before treating the issue as resolved.

## Production lessons

- A running container does not automatically mean the application is healthy.
- `EXPOSE` documents a container port; it does not publish the port on the host.
- Environment variables only affect application behavior when the application reads them.
- Non-root execution reduces risk, though it does not replace other security controls.
- Image contents, startup commands, and runtime configuration must agree.
- Use logs and direct evidence to identify root causes instead of guessing.

## Cleanup status

The broken container is intentionally retained for inspection. The two working application containers are also retained for further exercises. No existing containers or volumes were deleted.
