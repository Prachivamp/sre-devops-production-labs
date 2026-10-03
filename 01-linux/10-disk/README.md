# Linux Lab 10 — Disk Usage & Troubleshooting

## Objective

Learn how to investigate disk usage on a Linux system when an application/server reports that disk space is running low.

The goal is to understand how to:

* Check filesystem-level disk usage
* Identify which directories are consuming space
* Drill down to the exact large file
* Safely investigate before deleting anything
* Verify disk usage after cleanup
* Understand the production importance of log rotation and retention

---

## Scenario

An application server is suspected to be consuming too much disk space.

The application is located under:

```text
/opt/myapp
```

We want to answer:

> Where is the disk space being consumed?

Instead of guessing, we investigate from the filesystem down to the individual file.

---

## Environment

* Ubuntu 24.04 LTS
* Running inside Docker
* User: `root`
* Application directory: `/opt/myapp`

---

# 1. Check Filesystem Usage

We first checked the root filesystem:

```bash
df -h /
```

Result:

```text
Filesystem      Size  Used Avail Use% Mounted on
overlay         224G  4.7G  208G   3% /
```

### What `df` tells us

`df` shows filesystem-level disk usage.

Important columns:

| Column     | Meaning                |
| ---------- | ---------------------- |
| Size       | Total filesystem size  |
| Used       | Space currently used   |
| Avail      | Available space        |
| Use%       | Percentage used        |
| Mounted on | Filesystem mount point |

In this case, the filesystem was only using **3%**, so the filesystem was not actually close to full.

---

# 2. Find Large Application Directories

We then investigated the application directory:

```bash
du -sh /opt/myapp/*
```

Result:

```text
8.0K    /opt/myapp/backup
8.0K    /opt/myapp/config
101M    /opt/myapp/logs
20K     /opt/myapp/service
12K     /opt/myapp/shared
```

This narrowed our investigation to:

```text
/opt/myapp/logs
```

The logs directory was consuming approximately **101 MB**.

---

# 3. Identify the Large File

We drilled down into the logs directory:

```bash
du -sh /opt/myapp/logs/*
```

Result:

```text
4.0K    /opt/myapp/logs/app.log
100M    /opt/myapp/logs/large-app.log
```

We identified the large file:

```text
/opt/myapp/logs/large-app.log
```

Size:

```text
100M
```

This was the file responsible for the large amount of disk usage inside the application's log directory.

---

# 4. Simulate Log Growth

The large log file was deliberately created for this lab to simulate an application generating excessive logs:

```bash
dd if=/dev/zero of=/opt/myapp/logs/large-app.log bs=1M count=100
```

Output:

```text
100+0 records in
100+0 records out
104857600 bytes copied
```

We then verified:

```bash
du -sh /opt/myapp/logs/large-app.log
```

Result:

```text
100M    /opt/myapp/logs/large-app.log
```

This simulated a common production problem where application logs grow continuously and consume disk space.

---

# 5. Safe Cleanup

Because this file was deliberately created for the lab, we removed it:

```bash
rm /opt/myapp/logs/large-app.log
```

Then verified the log directory:

```bash
du -sh /opt/myapp/logs
```

Result:

```text
8.0K    /opt/myapp/logs
```

We also checked the filesystem again:

```bash
df -h /
```

Result:

```text
Filesystem      Size  Used Avail Use% Mounted on
overlay         224G  4.7G  208G   3% /
```

The disk usage returned to the previous level.

---

# 6. Important `df` vs `du` Difference

This is an important Linux troubleshooting concept.

### `df`

```bash
df -h
```

Answers:

> How much space is being used on the filesystem?

### `du`

```bash
du -sh /path/*
```

Answers:

> Which directories/files are consuming the space?

A useful troubleshooting pattern is:

```text
df
 ↓
Identify filesystem
 ↓
du
 ↓
Identify large directory
 ↓
du again
 ↓
Identify large file
 ↓
Investigate before cleanup
 ↓
Verify
```

---

# 7. `/proc` Warning During `du`

While running:

```bash
du -sh /*
```

we saw messages similar to:

```text
du: cannot access '/proc/...': No such file or directory
```

This happened because `/proc` is a dynamic virtual filesystem.

Processes and file descriptors can disappear while `du` is scanning them.

This does not automatically indicate a disk problem.

---

# 8. Production Consideration — Don't Blindly Delete Logs

In a real production environment, we should **not immediately run**:

```bash
rm application.log
```

just because it is large.

First determine:

* Is the application still writing to the file?
* Is the log required for troubleshooting?
* Is there a log retention policy?
* Is log rotation configured?
* Can old logs be compressed?
* Is the log shipped to a centralized logging system?
* Is the file currently held open by a running process?

Production systems commonly use log rotation, retention and/or centralized log collection rather than manually deleting active logs.

A deleted file can also remain open by a running process, meaning disk space may not immediately be recovered.

---

# 9. Production Troubleshooting Approach

If an alert says:

> Disk usage is above 90%

A reasonable first investigation is:

```bash
df -h
```

Identify the affected filesystem.

Then:

```bash
du -sh /*
```

Identify the large top-level directory.

Then progressively drill down:

```bash
du -sh /var/*
du -sh /var/log/*
```

or the relevant application directory:

```bash
du -sh /opt/myapp/*
du -sh /opt/myapp/logs/*
```

Finally inspect suspicious files:

```bash
ls -lh /path/to/file
```

Only after understanding the cause should remediation be performed.

---

# Key Commands

```bash
df -h
```

Check filesystem disk usage.

```bash
du -sh /path
```

Check total disk usage of a directory.

```bash
du -sh /path/*
```

Find which files/directories are consuming space.

```bash
ls -lh
```

View human-readable file sizes.

---

# Interview Takeaway

### Question

**How would you troubleshoot a Linux server with high disk utilization?**

### Answer

> First, I would use `df -h` to identify which filesystem is running out of space. Then I would use `du -sh` to drill down through directories and identify where the space is being consumed. Once I find the large files, I would investigate whether they are logs, application data, temporary files, or something else before taking any cleanup action. For logs, I would check the application's log rotation and retention configuration rather than blindly deleting active files. Finally, I would verify the filesystem usage after remediation.

---

# What I Learned

* `df` shows filesystem-level disk usage.
* `du` helps identify where disk space is being consumed.
* Troubleshooting should move from broad to specific.
* Large application logs can cause disk growth.
* Files should not be deleted blindly in production.
* Log rotation and retention are important operational practices.
* Always verify the system after remediation.

---

## Troubleshooting Pattern

```text
PROBLEM
   ↓
Observe
   ↓
df -h
   ↓
Identify filesystem
   ↓
du -sh
   ↓
Find large directory
   ↓
Find large file
   ↓
Understand the cause
   ↓
Fix safely
   ↓
Verify
```

This follows the overall lab philosophy:

> **What is happening → How to investigate → Why it is happening → How to fix it → How to verify it**
