# Linux Lab 11 — Memory & RAM Troubleshooting

## Objective

Learn how to investigate Linux memory usage and identify processes consuming significant RAM.

This lab covers:

* Checking memory usage with `free`
* Understanding `used`, `free`, `buff/cache`, and `available`
* Identifying memory-consuming processes
* Understanding RSS
* Creating controlled memory pressure
* Verifying system recovery
* Understanding when memory usage is actually a problem

---

## Scenario

An application server is reported to be slow and potentially consuming too much memory.

The first question should not be:

> "Should I restart the server?"

Instead, investigate:

> "How much memory is actually available, and which process is consuming it?"

---

## Environment

* Ubuntu 24.04 LTS
* Running inside Docker
* Memory available to the environment: approximately 3.8 GiB
* Swap: approximately 1 GiB

---

# 1. Establish a Memory Baseline

We started with:

```bash
free -h
```

Initial result:

```text
Mem:           3.8Gi       465Mi       3.2Gi       568Ki       282Mi       3.4Gi
Swap:          1.0Gi          0B       1.0Gi
```

### Important columns

| Column     | Meaning                                      |
| ---------- | -------------------------------------------- |
| total      | Total memory available                       |
| used       | Memory currently used                        |
| free       | Completely unused memory                     |
| shared     | Shared memory usage                          |
| buff/cache | Memory used for buffers/cache                |
| available  | Estimated memory available for new workloads |

### Important lesson

`free` memory is not the most important number by itself.

Linux intentionally uses memory for filesystem caches and other purposes.

For many troubleshooting situations, `available` is more useful because it estimates how much memory can still be given to applications without significant memory pressure.

---

# 2. Check Which Processes Use Memory

We ran:

```bash
ps aux --sort=-%mem | head
```

Initially, the container had no significant memory-consuming process.

The `ps` command itself appeared temporarily at the top because the process list is dynamic.

This is similar to CPU troubleshooting: diagnostic commands can briefly appear in their own output.

---

# 3. Create Controlled Memory Pressure

Python was not installed in the minimal Ubuntu container, and the `stress` command was also unavailable.

We therefore installed `stress-ng` specifically for this controlled lab:

```bash
apt update
apt install -y stress-ng
```

Verified:

```bash
command -v stress-ng
```

Result:

```text
/usr/bin/stress-ng
```

---

# 4. Allocate 500 MB of Memory

We deliberately created a controlled memory workload:

```bash
stress-ng --vm 1 --vm-bytes 500M --vm-keep --timeout 60s &
```

Meaning:

* `--vm 1` → one memory worker
* `--vm-bytes 500M` → target 500 MB
* `--vm-keep` → keep memory allocated
* `--timeout 60s` → automatically stop after 60 seconds
* `&` → run in the background

---

# 5. Observe Memory Usage

While the workload was running:

```bash
free -h
```

showed approximately:

```text
Mem:           3.8Gi       1.1Gi       2.3Gi       2.8Mi       610Mi       2.8Gi
Swap:          1.0Gi          0B       1.0Gi
```

Compared with our baseline, memory usage increased significantly.

However, there was still approximately 2.8 GiB available.

Swap usage remained:

```text
0B
```

So the system was not under severe memory pressure.

---

# 6. Identify the Memory-Consuming Process

We ran:

```bash
ps aux --sort=-%mem | head
```

The important process was:

```text
PID   %MEM   RSS      COMMAND
516   12.8   514136   stress-ng-vm [run]
```

The process had an RSS of approximately 514 MB.

---

# 7. What is RSS?

RSS stands for:

> Resident Set Size

It represents the amount of a process's memory that is currently resident in physical memory.

In this lab:

```text
RSS ≈ 514 MB
```

which closely matched our deliberate 500 MB allocation.

RSS is therefore useful when investigating which process is actually occupying physical RAM.

---

# 8. Wait for the Test to Finish

The test was configured for 60 seconds:

```text
--timeout 60s
```

After approximately one minute, `stress-ng` reported:

```text
successful run completed
```

The process terminated automatically.

---

# 9. Verify Recovery

After the memory workload ended:

```bash
free -h
```

showed approximately:

```text
Mem:           3.8Gi       568Mi       2.8Gi       568Ki       608Mi       3.3Gi
Swap:          1.0Gi          0B       1.0Gi
```

Swap remained at:

```text
0B
```

The system returned close to its original memory state.

This demonstrates an important operational principle:

> Always verify the system after remediation or after a temporary workload ends.

---

# 10. Memory Troubleshooting Pattern

When investigating a server with suspected memory problems:

```text
PROBLEM
   ↓
Check memory
   ↓
free -h
   ↓
Is available memory actually low?
   ↓
Identify processes
   ↓
ps aux --sort=-%mem
   ↓
Identify high-memory process
   ↓
Investigate RSS / process behavior
   ↓
Determine cause
   ↓
Remediate
   ↓
Verify recovery
```

---

# 11. What Can Cause High Memory Usage?

A high-memory process does not automatically mean there is a memory leak.

Possible causes include:

* Higher application traffic
* Large workloads
* Large caches
* JVM/application heap configuration
* Memory leak
* Too many processes
* Incorrect application configuration
* Batch jobs
* Temporary spikes
* Insufficient memory allocated to the server

The process must be investigated in context.

---

# 12. Production Consideration

In production, do not immediately restart or kill a high-memory process.

First collect evidence:

```bash
free -h
ps aux --sort=-%mem | head
```

Then investigate the application and process further.

Useful questions include:

* Is the memory usage expected for this workload?
* Has memory usage been increasing continuously?
* Did traffic increase?
* Did a deployment happen recently?
* Is the process leaking memory?
* Is the configured application heap too large?
* Is the server actually running out of available memory?
* Is swap being used?
* Are multiple processes consuming memory?

The goal is to identify the cause rather than simply treating the symptom.

---

# Key Commands

### Check memory

```bash
free -h
```

### Find memory-heavy processes

```bash
ps aux --sort=-%mem | head
```

### Find a specific process

```bash
ps -p <PID>
```

### Check process memory details

```bash
ps -p <PID> -o pid,ppid,user,%cpu,%mem,vsz,rss,stat,etime,cmd
```

---

# Interview Takeaway

### Question

**How would you troubleshoot high memory usage on a Linux server?**

### Answer

> First, I would use `free -h` to check total, used, available memory and swap usage. I would pay particular attention to available memory rather than assuming high used memory is automatically a problem because Linux uses memory for cache. Then I would identify memory-consuming processes using `ps aux --sort=-%mem` and investigate their RSS and behavior. I would correlate the memory usage with application workload, recent deployments, traffic, and application configuration before deciding on remediation. Finally, I would verify that memory usage returns to a healthy state after the fix.

---

# What I Learned

* `free -h` provides a quick memory overview.
* `available` is often more useful than `free` when assessing memory pressure.
* Linux uses memory for filesystem cache.
* `ps aux --sort=-%mem` helps identify memory-heavy processes.
* RSS helps understand a process's resident physical memory usage.
* High memory usage does not automatically mean a memory leak.
* Swap usage is an important signal when investigating memory pressure.
* Always investigate before restarting or killing processes.
* Always verify the system after remediation.

---

## Lab Philosophy

```text
What is happening?
        ↓
How much memory is available?
        ↓
Which process is consuming it?
        ↓
Why is it consuming that memory?
        ↓
What should be changed?
        ↓
Did the system recover?
```
