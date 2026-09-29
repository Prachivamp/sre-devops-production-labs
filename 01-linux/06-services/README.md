# Linux Lab 06 — Services & Application Availability

## Objective

Learn how to troubleshoot a Linux application that has stopped running.

In this lab, we simulated a production incident where an application was running normally, then stopped unexpectedly.

We practiced:

* Checking whether an application process is running
* Using logs as evidence
* Confirming an outage
* Starting the application again
* Verifying both the process and application behavior
* Understanding the role of service managers such as `systemd`

---

## Production Scenario

Imagine an application server reports:

> "The application is down."

Instead of immediately restarting the entire server, we investigate the application itself.

Our troubleshooting approach:

```text
Application is down
       ↓
Check process
       ↓
Check logs
       ↓
Confirm outage
       ↓
Start application
       ↓
Verify process
       ↓
Verify application behavior
```

---

# Environment

* Ubuntu 24.04
* Running inside Docker
* User: `root`

---

# Important Environment Limitation

Before starting the service exercise, we checked PID 1:

```bash
ps -p 1 -o pid,comm,args
```

The result was:

```text
PID COMMAND COMMAND
1   bash    /bin/bash
```

This means the container is not running `systemd` as PID 1.

Therefore, commands such as:

```bash
systemctl status
systemctl start
systemctl stop
```

would not represent a normal `systemd` environment in this container.

Rather than pretending that `systemctl` works here, this lab uses a real background application process to demonstrate the underlying service-management and troubleshooting concepts.

Actual `systemd` administration will be practiced later on a proper Linux VM/server environment.

---

# 1. Create the Application

Created an application directory:

```bash
mkdir -p /opt/myapp/service
```

Created a simple application script:

```bash
cat > /opt/myapp/service/app.sh <<'EOF'
#!/bin/bash

while true
do
    echo "$(date) - application is running" >> /opt/myapp/service/app.log
    sleep 5
done
EOF
```

Made it executable:

```bash
chmod +x /opt/myapp/service/app.sh
```

---

# 2. Start the Application

Started the application in the background:

```bash
/opt/myapp/service/app.sh &
```

The shell returned a PID.

For example:

```text
[1] 13
```

The PID can be different each time.

---

# 3. Verify the Application Process

Used:

```bash
ps aux | grep '[a]pp.sh'
```

The process appeared similar to:

```text
root  13  ... /bin/bash /opt/myapp/service/app.sh
```

This confirmed that the application process was running.

---

# 4. Verify Application Behavior

The application writes a heartbeat to:

```text
/opt/myapp/service/app.log
```

Checked the log with:

```bash
tail -n 5 /opt/myapp/service/app.log
```

The log contained entries such as:

```text
application is running
application is running
application is running
```

The timestamps changed every five seconds.

This gave us two useful signals:

```text
Process exists
      +
Expected application activity
      =
Application appears healthy
```

---

# 5. Simulate an Application Failure

We deliberately stopped the application.

First, we identified its PID:

```bash
ps aux | grep '[a]pp.sh'
```

The application had PID `13` during the exercise.

Stopped it:

```bash
kill 13
```

The shell reported:

```text
[1]+ Terminated /opt/myapp/service/app.sh
```

---

# 6. Confirm the Application Is Down

Checked for the process:

```bash
ps aux | grep '[a]pp.sh'
```

There was no output.

This showed that the application process was no longer running.

---

# 7. Check the Application Logs

Checked the last entries:

```bash
tail -n 5 /opt/myapp/service/app.log
```

The final entries were:

```text
Tue Sep 29 21:08:15 UTC 2026 - application is running
Tue Sep 29 21:08:20 UTC 2026 - application is running
Tue Sep 29 21:08:25 UTC 2026 - application is running
Tue Sep 29 21:08:30 UTC 2026 - application is running
Tue Sep 29 21:08:35 UTC 2026 - application is running
```

After waiting and checking again, there were no new heartbeat entries.

This gave us two independent pieces of evidence:

```text
Process check → application process absent
Log check     → heartbeat stopped
```

Therefore, the application outage was confirmed.

---

# 8. Recover the Application

Started the application again:

```bash
/opt/myapp/service/app.sh &
```

The new process received PID `115` during this exercise.

Verified:

```bash
ps aux | grep '[a]pp.sh'
```

The application was running again.

---

# 9. Verify Application Recovery

Checked the application log:

```bash
tail -n 3 /opt/myapp/service/app.log
```

New heartbeat entries appeared:

```text
Tue Sep 29 21:11:01 UTC 2026 - application is running
Tue Sep 29 21:11:06 UTC 2026 - application is running
Tue Sep 29 21:11:11 UTC 2026 - application is running
```

This confirmed that the application was not merely running as a process; it was actually performing its expected behavior.

---

# Process Check vs Application Health

A useful production lesson from this lab:

Checking only:

```bash
ps aux | grep '[a]pp.sh'
```

does not prove that the application is healthy.

A process can exist while the application itself is:

* Hung
* Unable to connect to a dependency
* Returning errors
* Not processing requests
* Stuck in an internal loop

Therefore, stronger verification uses multiple signals:

```text
Process exists
       +
Logs are updating
       +
Expected application behavior
       =
Stronger evidence of recovery
```

---

# Service Managers

In production Linux environments, applications are commonly managed by a service manager.

One widely used service manager is `systemd`.

Typical commands include:

```bash
systemctl status <service>
systemctl start <service>
systemctl stop <service>
systemctl restart <service>
systemctl enable <service>
```

Conceptually:

```text
Service Manager
      ↓
Application Process
      ↓
Application
      ↓
Logs / Health / Requests
```

A service manager can also provide capabilities such as:

* Starting services
* Stopping services
* Restarting services
* Starting services during boot
* Restarting failed services
* Managing dependencies
* Integrating with system logs

We will practice actual `systemctl` commands on a proper Linux environment later.

---

# Useful Commands From This Lab

### Find an application process

```bash
ps aux | grep '[a]pp.sh'
```

### Inspect a process

```bash
ps -p <PID> -o pid,ppid,user,%cpu,%mem,stat,etime,cmd
```

### Stop a process

```bash
kill <PID>
```

### Start a background process

```bash
/path/to/application &
```

### Inspect recent logs

```bash
tail -n 5 /path/to/application.log
```

---

# Troubleshooting Pattern

When an application is reported as down:

```text
1. Observe the symptom
        ↓
2. Check whether the process exists
        ↓
3. Check application logs
        ↓
4. Confirm the outage
        ↓
5. Start/restart the application
        ↓
6. Verify the process
        ↓
7. Verify application behavior
```

Do not stop at:

```text
"Process is running."
```

Instead ask:

> "Is the application actually working?"

---

# Production Relevance

This workflow is common when troubleshooting:

* Web applications
* API servers
* Background workers
* Message consumers
* Scheduled services
* Database-related services
* CI/CD agents
* Monitoring agents

A real production incident might look like:

```text
User reports application is down
             ↓
Check service status
             ↓
Check process
             ↓
Check recent logs
             ↓
Identify failure
             ↓
Recover service
             ↓
Verify health
             ↓
Investigate why it stopped
```

The recovery is only part of the incident.

A good SRE also asks:

> Why did the application stop?

That question leads to root-cause investigation and prevention.

---

# Key Takeaways

1. A running process does not automatically mean an application is healthy.
2. Check both process state and application behavior.
3. Logs are useful evidence when investigating outages.
4. `ps` helps determine whether a process exists.
5. `kill` can be used to stop a process.
6. Always verify recovery after restarting an application.
7. Production systems commonly use service managers such as `systemd`.
8. Our Docker container uses `bash` as PID 1, so actual `systemctl` behavior must be practiced in a proper systemd-based Linux environment.
9. Recovery should be followed by investigation into why the service stopped.

---

# Troubleshooting Principle

The main lesson from this lab:

```text
Application Down
      ↓
Check Process
      ↓
Check Logs
      ↓
Confirm Outage
      ↓
Recover
      ↓
Verify Process
      ↓
Verify Application Behavior
      ↓
Investigate Root Cause
```

This is the troubleshooting mindset we will continue using throughout the SRE/DevOps labs.
