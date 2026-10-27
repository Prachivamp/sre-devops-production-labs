# Lab 08 — Docker Compose and Multi-Container Applications

## Objective

Build and troubleshoot a multi-container application using Docker Compose. The lab uses a Python Flask API and PostgreSQL database to practice service discovery, startup dependencies, health checks, logs, failure recovery, and persistent storage.

## Architecture

- **API:** Python 3.12, Flask, and psycopg2; listens on port `5001`.
- **Database:** PostgreSQL 16; listens on port `5432` inside the Compose network.
- **Networking:** The API connects to the database using the Compose service hostname `db`.
- **Port publishing:** The API is available locally at `127.0.0.1:5001`. PostgreSQL's port is not published to the host.
- **Persistence:** PostgreSQL stores its data in the named volume `lab08-postgres-data`.

## Files

```text
08-Docker Compose and Multi-Container Applications/
├── api/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── compose.yaml
└── README.md
```

## 1. Configure and validate Compose

The Compose configuration defines two services: `api` and `db`.

The API uses environment variables for its database connection. The database uses a named volume, a health check, and a restart policy.

Set the local lab password in the same terminal session:

```bash
export DB_PASSWORD='Lab08_LocalOnly_ChangeMe_2026'
```

Validate the Compose configuration:

```bash
docker compose config --quiet
```

No output indicates that the configuration passed validation.

**Security note:** The password above is for this local lab only. Do not reuse it for real services or commit real credentials to Git. For a production setup, use an appropriate secrets-management mechanism.

## 2. Build and start the services

Build the API image:

```bash
docker compose build api
```

Start both services:

```bash
docker compose up -d
```

Inspect service status:

```bash
docker compose ps
```

Wait for PostgreSQL to report `healthy`.

Inspect logs:

```bash
docker compose logs --tail=30 api
docker compose logs --tail=30 db
```

The API logs show the Flask development server starting. This is suitable for this learning lab, not a production deployment. Production applications should use an appropriate production WSGI server and deployment configuration.

## 3. Test the API

Test the home endpoint:

```bash
curl -i http://127.0.0.1:5001/
```

**Observed result:** HTTP 200 OK with a JSON response identifying `lab08-api`.

Test database connectivity:

```bash
curl -i http://127.0.0.1:5001/db-health
```

**Observed result:** HTTP 200 OK with:

```json
{"database":"connected"}
```

## 4. Understand Compose service discovery

The API connects to PostgreSQL using:

```text
DB_HOST=db
DB_PORT=5432
```

The hostname `db` refers to the database service on the Compose network. Containers on that network can use service names to communicate without hard-coding container IP addresses.

Port `5432` is the database's container port. It does not need to be published on the host for the API container to access it over the Compose network.

## 5. Simulate a database outage

Stop only the database service:

```bash
docker compose stop db
```

Inspect the services:

```bash
docker compose ps -a
```

Test the API home endpoint:

```bash
curl -i http://127.0.0.1:5001/
```

**Observed result:** The home endpoint continued returning HTTP 200 OK while the database was stopped.

Test the database health endpoint:

```bash
curl -i http://127.0.0.1:5001/db-health
```

**Observed result:** HTTP 503 Service Unavailable.

Inspect API logs:

```bash
docker compose logs --tail=20 api
```

The logs showed:

```text
psycopg2.OperationalError:
could not translate host name "db" to address:
Name or service not known
```

### Diagnosis

The API process remained available, but the database-dependent operation failed. While the database container was stopped, its service endpoint was unavailable through Compose DNS, and the API could not resolve the hostname `db`.

The observed error was a hostname-resolution failure, rather than proof of a database authentication failure or a connection-refused error.

## 6. Restore database connectivity

Start PostgreSQL again:

```bash
docker compose start db
```

Check service health:

```bash
docker compose ps
```

Wait until the database reports `healthy`, then test again:

```bash
curl -i http://127.0.0.1:5001/db-health
```

**Observed result:** HTTP 200 OK with:

```json
{"database":"connected"}
```

### Recovery lesson

The API recovered its database connectivity without requiring an API container restart.

The Compose setting `depends_on` with `condition: service_healthy` helps order initial startup. It does not automatically stop or restart the API whenever PostgreSQL becomes unhealthy. Applications need appropriate connection handling, timeouts, error responses, and recovery behavior.

## 7. Verify named-volume persistence

Create a test table:

```bash
docker compose exec db psql -U lab08user -d lab08db \
  -c "CREATE TABLE IF NOT EXISTS lab08_persistence_test (id SERIAL PRIMARY KEY, message TEXT);"
```

Insert a row:

```bash
docker compose exec db psql -U lab08user -d lab08db \
  -c "INSERT INTO lab08_persistence_test (message) VALUES ('Data survives container restart');"
```

Read the row:

```bash
docker compose exec db psql -U lab08user -d lab08db \
  -c "SELECT * FROM lab08_persistence_test;"
```

Restart PostgreSQL:

```bash
docker compose restart db
```

Wait until it reports `healthy`, then query the table again:

```bash
docker compose exec db psql -U lab08user -d lab08db \
  -c "SELECT * FROM lab08_persistence_test;"
```

**Observed result:** The inserted row remained present after the database container restart.

### Persistence lesson

The named volume `lab08-postgres-data` stores PostgreSQL data independently of the container's writable layer. Restarting the container does not remove the data.

This test verified persistence across a restart; it did not test deleting and recreating the container.

## 8. Troubleshooting commands

| Command | Purpose |
|---|---|
| `docker compose ps -a` | Inspect service and container states |
| `docker compose logs --tail=30 api` | Inspect API errors |
| `docker compose logs --tail=30 db` | Inspect database startup and runtime logs |
| `docker compose config --quiet` | Validate Compose configuration |
| `docker compose exec db pg_isready -U lab08user -d lab08db` | Check PostgreSQL readiness |
| `docker compose exec db psql -U lab08user -d lab08db -c "SELECT 1;"` | Verify a simple database query |
| `curl -i http://127.0.0.1:5001/db-health` | Test API-to-database connectivity |

## Key takeaways

- Docker Compose manages related services through one configuration.
- Compose service names provide DNS-based service discovery.
- Container ports and host-published ports serve different purposes.
- Health checks help determine when a dependency is ready.
- `depends_on` startup conditions do not provide complete runtime dependency recovery.
- HTTP status codes and container logs help isolate failures.
- Named volumes preserve database data across container restarts.
- Production applications need production-grade serving, secret handling, and resilient dependency management.

## Lab status

- [x] Compose configuration validated
- [x] API and PostgreSQL started
- [x] API endpoint tested
- [x] Database connectivity verified
- [x] Database outage reproduced
- [x] API logs inspected
- [x] Database connectivity restored
- [x] Named-volume persistence verified across restart
