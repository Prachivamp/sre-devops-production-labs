# Lab 04 — Ports, Environment Variables and Container Configuration

## Objective

Understand Docker port publishing, environment variables, container configuration, and common production configuration failures through hands-on exercises.

## 1. Inspect exposed and published ports

```bash
docker port docker-lab01-nginx
```

```bash
docker inspect docker-lab01-nginx \
  --format 'Name={{.Name}} ExposedPorts={{json .Config.ExposedPorts}} PortBindings={{json .HostConfig.PortBindings}}'
```

Observed results:

- The container declared `80/tcp`.
- `PortBindings={}` indicated that no host port mapping was configured.
- `docker port` returned no published-port mapping.

### Key concept

An exposed container port is not the same as a published host port. A container can have a service listening internally without making it accessible through a host port.

## 2. Publish a container port

Create a dedicated test container:

```bash
docker run -d --name docker-lab04-nginx -p 8085:80 nginx:alpine
```

Verify its mapping:

```bash
docker port docker-lab04-nginx
```

Observed output:

```text
80/tcp -> 0.0.0.0:8085
80/tcp -> [::]:8085
```

Test HTTP connectivity:

```bash
curl -I http://localhost:8085
```

Observed result: `HTTP/1.1 200 OK`.

### Key concept

The mapping `8085:80` means host port `8085` forwards to container port `80`.

- `0.0.0.0` represents all IPv4 interfaces.
- `::` represents the IPv6 wildcard address.

Binding to all interfaces can expose a service beyond the local machine, depending on the host network and firewall. For local-only testing, consider publishing as `127.0.0.1:8085:80`.

## 3. Inspect container environment variables

```bash
docker inspect docker-lab04-nginx \
  --format '{{range .Config.Env}}{{println .}}{{end}}'
```

The Nginx image included variables such as `PATH`, `NGINX_VERSION`, and package-release metadata.

Environment variables can configure application behaviour, but the application must be written to read and use each variable.

## 4. Pass environment variables to a container

```bash
docker run --rm \
  --name docker-lab04-env \
  -e APP_ENV=production \
  -e DATABASE_HOST=db.internal \
  -e DATABASE_PORT=5432 \
  alpine:latest \
  sh -c 'echo "APP_ENV=$APP_ENV"; echo "DATABASE_HOST=$DATABASE_HOST"; echo "DATABASE_PORT=$DATABASE_PORT"'
```

Observed output:

```text
APP_ENV=production
DATABASE_HOST=db.internal
DATABASE_PORT=5432
```

The `-e` option passes environment variables into the container. The `--rm` option removes the temporary container after it exits.

These are demonstration values. Setting `DATABASE_HOST` does not create a database or establish a database connection.

## 5. Reproduce a missing-configuration failure

```bash
docker run --rm alpine:latest sh -c '
if [ -z "$DATABASE_HOST" ]; then
  echo "ERROR: DATABASE_HOST is not set"
  exit 1
else
  echo "DATABASE_HOST=$DATABASE_HOST"
fi
'
```

Observed result:

```text
ERROR: DATABASE_HOST is not set
```

The script exited with status `1` because the required variable was missing.

## 6. Fix the configuration

```bash
docker run --rm -e DATABASE_HOST=db.internal alpine:latest sh -c '
if [ -z "$DATABASE_HOST" ]; then
  echo "ERROR: DATABASE_HOST is not set"
  exit 1
else
  echo "DATABASE_HOST=$DATABASE_HOST"
fi
'
```

Observed result:

```text
DATABASE_HOST=db.internal
```

The check passed because the variable was supplied.

## 7. Inspect the final container configuration

```bash
docker inspect docker-lab04-nginx \
  --format 'Status={{.State.Status}} RestartPolicy={{.HostConfig.RestartPolicy.Name}} Ports={{json .NetworkSettings.Ports}}'
```

Observed findings:

- Status: `running`
- Restart policy: `no`
- Container port: `80/tcp`
- Published host port: `8085`
- Host bindings: `0.0.0.0` and `::`

The restart policy `no` means Docker will not automatically restart the container if it stops.

## 8. Production troubleshooting workflow

When an application is unreachable or fails to start:

1. Confirm that the container is running.
2. Verify that the application listens on the expected container port and interface.
3. Inspect published port mappings.
4. Test the service locally with `curl`.
5. Inspect the container's environment variables.
6. Check for missing or incorrectly named configuration keys.
7. Review application logs and exit status.
8. Check restart policy and deployment configuration.
9. Avoid exposing sensitive configuration values in logs or shared terminal output.

### Security note

Do not put passwords, API keys, or other secrets directly into shell commands or ordinary environment variables without considering exposure risks. Use a suitable secrets-management mechanism for production workloads.

## Interview takeaways

- `EXPOSE` documents a container port; `-p` publishes a port to the host.
- `docker port` and `docker inspect` help verify port mappings.
- Environment variables provide runtime configuration when the application supports them.
- Missing configuration can cause startup failures or application errors.
- `--rm` removes a container after it exits.
- Restart policies influence recovery behaviour.
- A running container does not guarantee application health.

## Completion checklist

- [x] Inspected exposed and published ports
- [x] Published host port `8085` to container port `80`
- [x] Verified HTTP response `200 OK`
- [x] Inspected container environment variables
- [x] Passed custom environment variables to a container
- [x] Reproduced and fixed a missing-variable failure
- [x] Inspected restart policy and final port configuration