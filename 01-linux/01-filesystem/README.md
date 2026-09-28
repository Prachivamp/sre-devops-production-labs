# Linux Lab 01 — Filesystem Fundamentals

## Objective

Understand the basic Linux filesystem structure and learn how to locate application files, configuration, and logs.

## Environment

* Host: macOS
* Linux environment: Ubuntu 24.04
* Runtime: Docker
* Repository: `sre-devops-production-labs`

## Commands Practiced

```bash
whoami
pwd
ls
ls -la
mkdir
echo
cat
grep
```

## Linux Directories Observed

### `/etc`

Contains system and application configuration.

### `/var`

Contains data that changes during normal system operation. `/var/log` is particularly important for troubleshooting.

### `/tmp`

Used for temporary files.

### `/home`

Contains normal users' home directories.

### `/root`

Home directory of the root user.

### `/proc`

Provides information about processes and kernel/system state.

### `/opt`

Can be used for optional application software. In this lab, an example application directory was created under `/opt/myapp`.

## Hands-on Exercise

Created an example application structure:

```text
/opt/myapp/
├── config/
└── logs/
    └── app.log
```

Created an application log:

```bash
echo "Application started successfully" > /opt/myapp/logs/app.log
```

Added simulated application errors:

```bash
echo "ERROR: Database connection failed" >> /opt/myapp/logs/app.log
echo "ERROR: Database connection timeout" >> /opt/myapp/logs/app.log
```

Inspected the log:

```bash
cat /opt/myapp/logs/app.log
```

Searched for errors:

```bash
grep ERROR /opt/myapp/logs/app.log
```

## Troubleshooting Scenario

### Problem

An application is experiencing intermittent failures.

### Investigation

The application log was inspected to identify errors.

`grep` was used to filter the log and display only lines containing `ERROR`.

### Findings

The log contained:

```text
ERROR: Database connection failed
ERROR: Database connection timeout
```

This indicates that the application experienced database connectivity problems.

### Important Note

The log evidence shows database connection errors, but this exercise does not establish the underlying root cause of the database problem. Further investigation would be required.

## Production Relevance

Linux filesystem knowledge is fundamental to SRE and DevOps work.

During production incidents, engineers frequently need to locate:

* Configuration files
* Application files
* Logs
* Temporary files
* User data
* Disk-consuming directories

Log investigation is also a common first step when an application is failing.

## Key Takeaways

* `/` is the root of the Linux filesystem.
* `/etc` commonly contains configuration.
* `/var` contains changing system/application data.
* `/var/log` is important for troubleshooting.
* `/tmp` is used for temporary data.
* `/home` contains user home directories.
* `/proc` exposes process and kernel information.
* `grep` can filter text and is extremely useful for log investigation.
