# Lab 02 — Docker CLI and Container Troubleshooting

## Objective

Practise inspecting Docker containers and investigating stopped containers using read-only diagnostic commands.

## 1. List containers

```bash
docker ps
docker ps -a
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
```

- `docker ps` lists running containers.
- `docker ps -a` includes stopped and created containers.
- `--format` displays selected fields in a readable table.

## 2. Inspect container state

```bash
docker inspect pulsecart-api-compose \
  --format 'Status={{.State.Status}} ExitCode={{.State.ExitCode}} OOMKilled={{.State.OOMKilled}} Error={{.State.Error}} FinishedAt={{.State.FinishedAt}}'
```

Example findings from this lab:

- Status: `exited`
- Exit code: `137`
- OOMKilled: `false`

Exit code 137 is consistent with `SIGKILL`, but does not independently identify the cause. `OOMKilled=false` means Docker did not record this container as OOM-killed.

## 3. Review application logs

```bash
docker logs --tail 50 pulsecart-api-compose
```

The retained logs showed the Flask application starting and a successful `200` response from `/db-health`.

A successful historical response does not prove the application was healthy when the container stopped. Logs may not contain the termination event.

## 4. Check restart policy and memory configuration

```bash
docker inspect pulsecart-api-compose \
  --format 'Image={{.Config.Image}} RestartPolicy={{.HostConfig.RestartPolicy.Name}} MemoryLimit={{.HostConfig.Memory}}'
```

Observed results:

- Image: `pulsecart-platform-api`
- Restart policy: `no`
- Memory limit: `0`

A restart policy of `no` means Docker will not automatically restart the container. A memory limit of `0` means no explicit container-level memory limit was configured; it does not mean host memory is unlimited.

## 5. Check historical Docker events

```bash
docker events \
  --since "2026-09-09T00:00:00" \
  --until "2026-09-11T00:00:00" \
  --filter container=pulsecart-api-compose
```

No events were returned. Docker event history is limited, so the relevant events may no longer be available.

## 6. Production troubleshooting workflow

1. Identify the affected container and current state.
2. Inspect exit code, timestamps, and recorded OOM status.
3. Review application logs.
4. Inspect restart policy, resource limits, and container configuration.
5. Check Docker events and host-level monitoring when available.
6. Correlate findings with deployment history, operator actions, and application metrics.
7. State what is confirmed, what remains unknown, and what evidence is needed next.

## Incident conclusion

The container exited with code 137, while Docker reported `OOMKilled=false`. The last retained logs showed the Flask application starting and returning HTTP 200 for `/db-health`. The restart policy was `no`, and no explicit container memory limit was configured.

The exact termination cause could not be established from the available evidence. No restart, deletion, or configuration change was performed during this investigation.

## Interview takeaways

- Exit code 137 is not proof of an OOM kill.
- Container state and application health are different signals.
- Restart policies affect recovery behaviour.
- `docker inspect`, `docker logs`, and `docker events` provide complementary evidence.
- A good incident report separates confirmed facts from hypotheses.

## Completion checklist

- [x] Listed containers and interpreted their states
- [x] Inspected exit code and OOM status
- [x] Reviewed application logs
- [x] Checked restart policy and memory configuration
- [x] Queried historical Docker events
- [x] Documented findings without changing the existing container