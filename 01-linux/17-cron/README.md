# Linux Lab 17: Cron Jobs and Scheduled Tasks

## Objective

Learn how to schedule recurring tasks in Linux using cron and verify their execution through logs.

## Production scenario

An application needs a health check to run automatically every minute. An engineer should not need to run the script manually.

## Environment

* Ubuntu 24.04 running in Docker
* Bash health-check script: `/opt/myapp/scripts/health-check.sh`
* Application HTTP server on port 8080
* Cron scheduler

## 1. Install cron

```bash
apt update
apt install -y cron
```

Verify the commands:

```bash
command -v cron
command -v crontab
```

## 2. Start the cron service

```bash
service cron start
ps -ef | grep '[c]ron'
```

The process listing confirmed that the cron daemon was running.

## 3. Prepare a log file

```bash
mkdir -p /opt/myapp/logs
touch /opt/myapp/logs/cron-health-check.log
```

Run the health check manually and append its output:

```bash
/opt/myapp/scripts/health-check.sh >> /opt/myapp/logs/cron-health-check.log 2>&1
```

* `>>` appends output to the file.
* `2>&1` redirects standard error to the same destination.

## 4. Schedule the health check

Install the cron entry without requiring a text editor:

```bash
echo '* * * * * /opt/myapp/scripts/health-check.sh >> /opt/myapp/logs/cron-health-check.log 2>&1' | crontab -
```

Verify the saved schedule:

```bash
crontab -l
```

The expression `* * * * *` means the job runs every minute.

## 5. Troubleshoot the HTTP health check

The first manual log entries showed:

* Process: RUNNING
* Port 8080: LISTENING
* HTTP: UNHEALTHY

The HTTP request returned an empty reply even though a TCP connection was established.

After restarting the Python HTTP server with its output redirected to a log file, the request returned `HTTP/1.0 200 OK`.

The health-check script then reported:

* Process: RUNNING
* Port 8080: LISTENING
* HTTP: HEALTHY
* Overall Status: HEALTHY
* Exit code: `0`

## 6. Verify scheduled execution

Inspect the log:

```bash
tail -n 30 /opt/myapp/logs/cron-health-check.log
```

The log contained earlier unhealthy results and a later healthy result, demonstrating the value of retaining historical output when troubleshooting.

## Key concepts learned

* Cron schedules recurring tasks.
* `crontab -l` displays the current user's scheduled jobs.
* `crontab -` installs a schedule from standard input.
* `>>` appends output; `>` overwrites a file.
* `2>&1` captures error output alongside normal output.
* A process can be running while its HTTP endpoint is unhealthy.
* A health check detects failure; it does not automatically repair the application.

## Production relevance

Cron is commonly used for scheduled maintenance, cleanup jobs, reports, and periodic operational checks. Production jobs should have appropriate permissions, bounded execution time, useful logging, and a plan for handling failures.

For this lab, the job runs as root inside a disposable container. Production systems should generally use a dedicated least-privilege account when possible.

## Troubleshooting workflow

**Schedule → Scheduler process → Script execution → Logs → Application health**

## Key takeaway

Automating a task is only part of the job. An SRE must also verify that it runs on schedule, inspect its results, and investigate failures.
