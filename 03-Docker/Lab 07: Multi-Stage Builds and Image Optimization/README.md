# Lab 07: Multi-Stage Builds and Image Optimization

## Objective

Learn how to reduce Docker image size using multi-stage builds, separate build-time dependencies from runtime dependencies, and run a compiled application as a non-root user.

## Environment

- Host: MacBook Air
- Docker: Docker Desktop
- Application language: Go
- Container base image: Alpine Linux
- Application port: 8000

## Application

The Go application exposes two HTTP endpoints:

- `/` — returns a greeting message.
- `/health` — returns `OK` with HTTP 200.

The application reads its listening port from the `APP_PORT` environment variable, defaulting to `8000`.

## Single-Stage Build

The `Dockerfile.single` uses the Go image to compile and run the application in the same image.

```dockerfile
FROM golang:1.24-alpine
WORKDIR /src
COPY app/main.go .
RUN go build -o /app/server main.go
ENV APP_PORT=8000
EXPOSE 8000
CMD ["/app/server"]
```

### Result

- Image: `sre-lab07-single:1.0`
- Displayed image size: approximately 507 MB

This image includes the Go build environment, even though the running application only needs its compiled executable.

## Multi-Stage Build

The optimized `Dockerfile` separates compilation from runtime.

```dockerfile
FROM golang:1.24-alpine AS builder
WORKDIR /src
COPY app/main.go .
RUN CGO_ENABLED=0 GOOS=linux go build -o /server main.go

FROM alpine:3.22
WORKDIR /app
COPY --from=builder /server ./server
ENV APP_PORT=8000
EXPOSE 8000
USER 10001:10001
CMD ["/app/server"]
```

### How it works

1. **Builder stage:** Uses the Go image and compiler to build the application.
2. **Runtime stage:** Starts from a smaller Alpine image.
3. **COPY --from=builder:** Copies only the compiled executable into the runtime image.
4. **CGO_ENABLED=0:** Builds a statically linked Go executable for this application, avoiding dependence on C libraries at runtime.
5. **USER 10001:10001:** Runs the application as a non-root user.
6. **EXPOSE 8000:** Documents the container's listening port; it does not publish the port to the host.
7. **CMD:** Starts the compiled application when the container launches.

## Image Size Comparison

| Measurement | Result |
|---|---:|
| Single-stage image | 507 MB |
| Multi-stage image | 25.4 MB |
| Approximate reduction | 95% |
| Approximate space saved per image | 481.6 MB |

These are the sizes displayed by Docker during this lab; actual storage usage can vary with shared layers and image metadata.

## Runtime Verification

Started the optimized container with a loopback-only host port mapping:

```bash
docker run -d \
  --name docker-lab07-app \
  -p 127.0.0.1:8002:8000 \
  sre-lab07-multistage:1.0
```

Verified the health endpoint:

```bash
curl -i http://127.0.0.1:8002/health
```

**Result:** HTTP 200 OK with response body `OK`.

Container inspection confirmed:

- Status: `running`
- Image: `sre-lab07-multistage:1.0`
- Runtime user: `10001:10001`
- Host address and port: `127.0.0.1:8002`
- Container port: `8000`

The container logs showed:

```text
Application listening on port 8000
```

## Troubleshooting Finding: Missing Utility in a Minimal Image

Attempted to inspect the executable with:

```bash
docker run --rm \
  --entrypoint sh \
  sre-lab07-multistage:1.0 \
  -c 'ls -lh /app && file /app/server'
```

The output confirmed that `/app/server` existed and was executable, but the `file` command returned `not found`.

**Root cause:** The minimal Alpine runtime image did not include the optional `file` utility.

**Resolution:** No package installation was necessary. The application had already started successfully, and its health endpoint returned HTTP 200, confirming that the executable worked.

**Lesson:** A missing diagnostic utility does not automatically mean the application is broken. Validate the actual application behavior before drawing conclusions.

## Production Lessons

- Use multi-stage builds to keep compilers and build tools out of runtime images.
- Smaller images can reduce transfer time, storage requirements, and the amount of software included in the runtime environment.
- Run application processes as non-root users where practical.
- Bind development and test services to `127.0.0.1` when external access is not required.
- `EXPOSE` is metadata; `-p` publishes a port.
- A successful container start is useful evidence, but application-level health checks and meaningful tests provide stronger validation.
- Minimal images may omit troubleshooting tools, so choose diagnostics that are available or inspect from a separate temporary debugging environment.

## Cleanup

The following commands are optional and should only be run when you no longer need the lab resources:

```bash
docker stop docker-lab07-app
docker rm docker-lab07-app
docker image rm sre-lab07-single:1.0 sre-lab07-multistage:1.0
```

Do not run cleanup while you still want to inspect or reuse these resources.

## Lab Status

- [x] Built the single-stage image.
- [x] Built the multi-stage image.
- [x] Compared image sizes.
- [x] Verified the health endpoint.
- [x] Confirmed the application runs as a non-root user.
- [x] Investigated a missing diagnostic utility.
- [ ] Commit and push the README to GitHub.