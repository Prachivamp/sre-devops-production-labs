# Lab 05 — Volumes, Bind Mounts and Data Persistence

## Objective
Understand Docker named volumes, bind mounts, data persistence, and read-only mounts through hands-on testing.

## 1. Named volume creation
Created an isolated Docker volume:

```bash
docker volume create docker-lab05-data
docker volume inspect docker-lab05-data
```

Existing volumes were left untouched to protect potentially important application and database data.

## 2. Verify data persistence

Wrote a file into the named volume:

```bash
docker run --rm \
  --name docker-lab05-writer \
  -v docker-lab05-data:/data \
  alpine:latest \
  sh -c 'echo "Docker volume persistence test" > /data/test.txt && cat /data/test.txt'
```

Read the file from a separate container:

```bash
docker run --rm \
  --name docker-lab05-reader \
  -v docker-lab05-data:/data \
  alpine:latest \
  cat /data/test.txt
```

**Result:** The second container returned the same text. This confirmed that the data persisted in the named volume after the writer container was removed.

## 3. Bind mount demonstration

Created a host directory and configuration file:

```bash
mkdir -p docker-lab05-bind-demo
echo "Configuration loaded from the Mac host" > docker-lab05-bind-demo/app.conf
```

Mounted the directory read-only:

```bash
docker run --rm \
  --name docker-lab05-bind-test \
  --mount "type=bind,source=$(pwd)/docker-lab05-bind-demo,target=/config,readonly" \
  alpine:latest \
  cat /config/app.conf
```

**Result:** The container successfully read the configuration file from the host.

## 4. Read-only mount troubleshooting

Attempted to modify the mounted file:

```bash
docker run --rm \
  --name docker-lab05-readonly-test \
  --mount "type=bind,source=$(pwd)/docker-lab05-bind-demo,target=/config,readonly" \
  alpine:latest \
  sh -c 'echo "modified" >> /config/app.conf'
```

**Observed error:**

```text
sh: can't create /config/app.conf: Read-only file system
```

**Diagnosis:** This was expected behavior, not an application failure. The mount was explicitly configured as read-only.

## Key concepts

- A **named volume** is managed by Docker and can persist beyond a container's lifecycle.
- A **bind mount** maps a specific host path into a container.
- The container's writable layer is separate from mounted persistent storage.
- A **read-only mount** prevents writes through that mount.
- `docker run --rm` removes the temporary container when it exits; it does not automatically delete a named volume.
- Before changing or deleting a volume, identify which containers use it and protect any important data.

## Production troubleshooting checklist

1. Check whether the application data is stored in the container layer, a named volume, or a bind mount.
2. Inspect mounts using `docker inspect <container>`.
3. Verify the host source path and container destination.
4. Check whether the mount is read-only and whether file permissions permit the intended operation.
5. Never remove a volume until its ownership, usage, and data-retention requirements are understood.

## Outcome

Successfully demonstrated named-volume persistence, host-to-container bind mounting, and read-only mount enforcement using disposable Alpine containers.
