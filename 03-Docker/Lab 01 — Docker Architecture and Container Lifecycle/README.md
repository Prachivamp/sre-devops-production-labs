# Lab 01 — Docker Architecture and Container Lifecycle

## Objective

Understand Docker's core components and practice the container lifecycle using a disposable Nginx container.

## Environment

- Host: macOS on Apple Silicon (`arm64`)
- Docker Desktop: 4.74.0
- Docker Engine: 29.4.3
- Image: `nginx:alpine`
- Container: `docker-lab01-nginx`

## 1. Inspect Docker version

```bash
docker version
```

This displays the Docker Client and Server versions.

- **Docker Client:** Accepts commands from the terminal.
- **Docker Engine:** Manages images, containers, networks, and volumes.
- **Docker Desktop:** Provides the Linux environment required to run Linux containers on macOS.

## 2. Inspect the Docker Engine

```bash
docker info
```

Important environment observations:

- 14 containers listed at the time of inspection
- 6 running and 8 stopped
- Storage driver: `overlayfs`
- Logging driver: `json-file`
- Cgroups: version 2
- Default runtime: `runc`
- Docker Engine architecture: `aarch64`
- Docker Engine memory: approximately 3.827 GiB

These values describe the environment at the time of inspection and may change.

## 3. List all containers

```bash
docker ps -a
```

- `docker ps` lists running containers.
- `docker ps -a` lists running and stopped containers, including containers that have not started.

Example states observed:

- `Up`: the container's main process is running.
- `Exited (0)`: the main process exited successfully.
- `Exited (137)`: commonly indicates SIGKILL; investigate before assuming an out-of-memory event.
- `Created`: the container exists but has not started.

A running container is not necessarily a healthy application.

## 4. Create and start a container

```bash
docker run -d --name docker-lab01-nginx nginx:alpine
```

- `docker run` creates a container and starts it.
- `-d` runs it in the background.
- `--name` assigns a predictable container name.
- `nginx:alpine` specifies the image and tag.

The returned container ID began with `f1b2573ca5be`.

## 5. Verify the running container

```bash
docker ps --filter "name=docker-lab01-nginx"
```

The container appeared with status `Up`.

The `PORTS` column displayed `80/tcp`. This means the image/container exposes port 80 as metadata, but no host port was published. Host access would require a published port mapping.

## 6. Inspect container configuration

```bash
docker inspect docker-lab01-nginx \
  --format 'Name={{.Name}} Status={{.State.Status}} Image={{.Config.Image}} RestartPolicy={{.HostConfig.RestartPolicy.Name}}'
```

Observed:

```text
Name=/docker-lab01-nginx Status=running Image=nginx:alpine RestartPolicy=no
```

- `Name`: container name.
- `Status`: current process state.
- `Image`: source image.
- `RestartPolicy=no`: Docker does not automatically restart the container when its main process exits.

## 7. Stop the container

```bash
docker stop docker-lab01-nginx
```

Verify:

```bash
docker ps -a --filter "name=docker-lab01-nginx"
```

Observed state: `Exited (0)`.

`docker stop` requests a graceful shutdown and then forcefully terminates the process if it does not stop within the configured timeout.

The container remains available for a future start.

## 8. Start the existing container

```bash
docker start docker-lab01-nginx
```

Verify:

```bash
docker ps --filter "name=docker-lab01-nginx"
```

The same container ID was reused.

`docker start` starts an existing stopped container; it does not create a new one.

## 9. Restart the container

```bash
docker restart docker-lab01-nginx
```

Verify:

```bash
docker ps --filter "name=docker-lab01-nginx"
```

The restart operation stops and starts the existing container.

**Production caution:** Restarting may restore service temporarily, but it does not diagnose or resolve the underlying cause of an application failure.

## Key command comparison

| Command | Purpose |
|---|---|
| `docker run` | Create and start a container |
| `docker ps` | List running containers |
| `docker ps -a` | List all containers |
| `docker inspect` | Inspect detailed configuration and state |
| `docker stop` | Gracefully stop a container |
| `docker start` | Start an existing stopped container |
| `docker restart` | Stop and start an existing container |
| `docker logs` | Read container stdout/stderr logs |
| `docker rm` | Remove a stopped container |

## SRE interview takeaways

1. A container is a running instance created from an image.
2. Stopping a container does not remove it.
3. `docker run` and `docker start` are not interchangeable.
4. A running state does not guarantee application health.
5. Exit code 137 suggests SIGKILL, but the cause requires further investigation.
6. Published ports map host ports to container ports.
7. Restarting a service is a recovery action, not a root-cause analysis.

## Cleanup

When you no longer need this disposable lab container, run:

```bash
docker rm -f docker-lab01-nginx
```

This removes only the lab container named `docker-lab01-nginx`. Do not run it if you want to keep practicing with this container.

## Completion criteria

- [x] Docker Client and Server inspected
- [x] Docker Engine configuration reviewed
- [x] Container created and inspected
- [x] Container stopped and started
- [x] Container restarted
- [x] Lifecycle behavior verified
- [ ] README committed and pushed to GitHub