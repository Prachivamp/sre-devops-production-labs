# Linux Lab 08 — Environment Variables

## Objective

Understand how Linux environment variables provide runtime configuration to applications and how missing environment variables can cause application startup failures.

## Scenario

An application requires the following configuration:

```text
DATABASE_HOST=db.internal
DATABASE_PORT=5432
APP_ENV=production
```

The application works when these variables are available, but fails when `DATABASE_HOST` is missing.

The goal is to:

* Understand shell variables
* Understand environment variables
* Understand `export`
* Understand variable inheritance by child processes
* Troubleshoot a missing environment variable
* Verify application configuration

---

## Environment

* OS: Ubuntu 24.04 LTS
* Environment: Docker container
* User: root

---

## 1. Inspect the Environment

```bash
printenv
```

Environment variables are configuration values made available to processes.

Examples:

```text
PATH
HOME
HOSTNAME
TERM
```

---

## 2. Create Application Configuration

```bash
export APP_ENV=production
export DATABASE_HOST=db.internal
export DATABASE_PORT=5432
```

Verify:

```bash
echo "$APP_ENV"
echo "$DATABASE_HOST"
echo "$DATABASE_PORT"
```

Expected:

```text
production
db.internal
5432
```

We can also inspect database-related variables:

```bash
env | grep '^DATABASE_'
```

---

## 3. Shell Variable vs Environment Variable

A shell variable can exist without being exported.

Example:

```bash
TEST_CONFIG=hello
```

The current shell can see it:

```bash
echo "$TEST_CONFIG"
```

But a child process cannot see it:

```bash
sh -c 'echo "Child process sees TEST_CONFIG=${TEST_CONFIG:-NOT_SET}"'
```

Result:

```text
Child process sees TEST_CONFIG=NOT_SET
```

Now export the variable:

```bash
export TEST_CONFIG
```

Run the child process again:

```bash
sh -c 'echo "Child process sees TEST_CONFIG=${TEST_CONFIG:-NOT_SET}"'
```

Result:

```text
Child process sees TEST_CONFIG=hello
```

### Key concept

```text
Shell variable
      |
      | export
      v
Environment variable
      |
      v
Child process / Application
```

This is important because applications generally receive configuration through their process environment.

---

## 4. Create an Application Configuration Check

Created:

```text
/opt/myapp/service/check-config.sh
```

The script validates required configuration:

```bash
#!/bin/bash

if [ -z "$DATABASE_HOST" ]; then
    echo "ERROR: DATABASE_HOST is missing"
    exit 1
fi

if [ -z "$DATABASE_PORT" ]; then
    echo "ERROR: DATABASE_PORT is missing"
    exit 1
fi

echo "Configuration OK"
echo "Environment: ${APP_ENV:-NOT_SET}"
echo "Database: $DATABASE_HOST:$DATABASE_PORT"
```

Make it executable:

```bash
chmod +x /opt/myapp/service/check-config.sh
```

Run it:

```bash
/opt/myapp/service/check-config.sh
```

Result:

```text
Configuration OK
Environment: production
Database: db.internal:5432
```

---

## 5. Simulate a Production Configuration Failure

Instead of permanently changing the shell environment, we removed `DATABASE_HOST` only from the environment of this process:

```bash
env -u DATABASE_HOST /opt/myapp/service/check-config.sh
```

Result:

```text
ERROR: DATABASE_HOST is missing
```

This simulated an application starting with incomplete configuration.

---

## 6. Troubleshooting

The troubleshooting process was:

### Step 1 — Check the environment

```bash
env | grep '^DATABASE_'
```

### Step 2 — Check a specific variable

```bash
printenv DATABASE_HOST
```

### Step 3 — Check another required variable

```bash
printenv DATABASE_PORT
```

The current shell still contained:

```text
DATABASE_HOST=db.internal
DATABASE_PORT=5432
```

The important discovery was that:

```bash
env -u DATABASE_HOST /opt/myapp/service/check-config.sh
```

removes the variable only from the environment of that particular process.

It does not remove the variable from the current shell.

---

## 7. Recovery Verification

After restoring the normal environment, the application check was run again:

```bash
/opt/myapp/service/check-config.sh
```

Result:

```text
Configuration OK
Environment: production
Database: db.internal:5432
```

The application configuration was successfully restored.

---

## Production Relevance

Environment variables are commonly used to provide runtime configuration to applications.

They are especially important in:

* Docker containers
* Kubernetes
* CI/CD pipelines
* Cloud deployments
* Application startup configuration
* Different environments such as development, staging, and production

A deployment can fail even when the application code is correct if required environment variables are missing or incorrect.

Examples:

```text
DATABASE_HOST
DATABASE_PORT
API_URL
APP_ENV
LOG_LEVEL
```

### Important troubleshooting principle

Do not immediately assume the application code is broken.

First verify the runtime configuration:

```text
Application failure
      ↓
Check environment
      ↓
Check required variables
      ↓
Check values
      ↓
Check how the process was started
      ↓
Fix configuration
      ↓
Verify application behavior
```

---

## Key Commands

| Command              | Purpose                                               |
| -------------------- | ----------------------------------------------------- |
| `printenv`           | Display environment variables                         |
| `printenv VAR`       | Display a specific environment variable               |
| `env`                | Display the process environment                       |
| `env \| grep`        | Filter environment variables                          |
| `export VAR=value`   | Create/export an environment variable                 |
| `export VAR`         | Export an existing shell variable                     |
| `unset VAR`          | Remove a variable from the current shell              |
| `env -u VAR command` | Run a command without a specific environment variable |

---

## Interview Takeaways

### What is the difference between a shell variable and an environment variable?

A shell variable belongs to the current shell. An exported environment variable is also passed to child processes.

### Why is `export` important?

Because applications launched by the shell need exported variables to receive those values through their process environment.

### How would you troubleshoot an application saying a configuration variable is missing?

Start by checking:

```bash
printenv VARIABLE_NAME
env | grep VARIABLE_NAME
```

Then verify how the application was started and whether the variable was actually provided to that process.

---

## What I Practiced

* [x] Inspect environment variables
* [x] Create environment variables
* [x] Use `export`
* [x] Understand shell vs environment variables
* [x] Test child-process inheritance
* [x] Create an application configuration check
* [x] Simulate a missing configuration variable
* [x] Troubleshoot the failure
* [x] Verify recovery

## Troubleshooting Pattern

```text
PROBLEM
   ↓
Observe
   ↓
Check environment
   ↓
Identify missing configuration
   ↓
Test hypothesis
   ↓
Fix
   ↓
Verify
   ↓
Document
```
