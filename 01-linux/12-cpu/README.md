# Linux Lab 12 — CPU & Load Troubleshooting

## Objective

Learn how to investigate a Linux server that appears slow because of high CPU usage.

This lab focuses on:

* Checking CPU utilization
* Identifying CPU-heavy processes
* Investigating a specific process using its PID
* Safely stopping a problematic process
* Understanding load average
* Comparing load average with the number of CPUs
* Using `/proc/loadavg`
* Verifying that the system recovered after the incident

---

## Production Scenario

An application server is reported as slow.

The first suspicion is high CPU usage.

As an SRE/DevOps engineer, the goal is not simply to restart the server. We need to:

1. Observe the system
2. Identify whether CPU is actually the problem
3. Find the process responsible
4. Investigate the process
5. Take the appropriate corrective action
6. Verify recovery
7. Document the incident

---

## Environment

* Ubuntu 24.04 LTS
* Running inside Docker
* Container name: `sre-linux-lab`
* Host machine: macOS

---

# 1. Check CPU Count

Command:

```bash
nproc
```

Output:

```text
8
```

The container sees **8 CPUs**.

This is important when interpreting load average.

---

# 2. Check CPU Baseline

Command:

```bash
top
```

Initial CPU output showed:

```text
%Cpu(s): 0.0 us, 0.0 sy, 0.0 ni, 100.0 id, 0.0 wa, 0.0 hi, 0.0 si, 0.0 st
```

Important fields:

* `us` — CPU used by user processes
* `sy` — CPU used by the kernel
* `id` — CPU idle
* `wa` — CPU waiting for I/O
* `st` — CPU stolen by another virtualized workload

At the beginning of the test, CPU was essentially **100% idle**, so there was no CPU pressure.

---

# 3. Simulate a High CPU Process

To reproduce a common production problem, start the `yes` command in the background:

```bash
yes > /dev/null &
```

This produced a process with PID `11`.

The command continuously generates output, which causes the process to consume significant CPU.

---

# 4. Find the Highest CPU Process

Command:

```bash
ps aux --sort=-%cpu | head
```

Relevant output:

```text
USER PID %CPU %MEM VSZ RSS TTY STAT START TIME COMMAND
root 11 99.9 0.0 2272 1152 pts/0 R 12:24 0:39 yes
```

The important observation was:

```text
PID: 11
CPU: 99.9%
COMMAND: yes
```

This identified PID `11` as the CPU-intensive process.

---

# 5. Investigate the Process

Instead of immediately killing a process, inspect it first.

Command:

```bash
ps -p 11 -o pid,ppid,user,%cpu,%mem,stat,etime,cmd
```

Output:

```text
PID  PPID USER %CPU %MEM STAT ELAPSED CMD
11   1    root 99.9 0.0  R    31:54   yes
```

### Interpretation

* `PID 11` — process ID
* `PPID 1` — parent process ID
* `USER root` — process is running as root
* `%CPU 99.9` — consuming approximately one CPU core
* `%MEM 0.0` — memory is not the problem
* `STAT R` — process is currently running
* `ELAPSED 31:54` — process had been running for around 32 minutes
* `CMD yes` — confirms the command responsible

This confirmed that the CPU issue was caused by the `yes` process.

---

# 6. Stop the Problematic Process

The process was intentionally created for this lab, so it was safe to terminate.

Command:

```bash
kill 11
```

`kill` sends `SIGTERM` by default.

This gives a normal process an opportunity to terminate cleanly.

---

# 7. Verify the Process Is Gone

Command:

```bash
ps -p 11
```

The process was no longer running.

We then checked the CPU-consuming processes again:

```bash
ps aux --sort=-%cpu | head
```

The `yes` process was no longer present.

This is important because a fix should always be followed by verification.

---

# 8. Check Load Average

Command:

```bash
uptime
```

Output:

```text
load average: 0.42, 0.92, 0.96
```

The three values represent:

```text
1 minute | 5 minutes | 15 minutes
```

Load average represents the amount of work that is runnable or waiting in the system.

It should not be treated as the same thing as CPU utilization.

---

# 9. Compare Load With CPU Count

The system had:

```text
8 CPUs
```

A load average of:

```text
0.96
```

is therefore relatively low on an 8-CPU system.

A useful mental model is:

```text
CPU count = 8

Load ≈ 1
```

means roughly one unit of runnable workload for eight available CPUs.

If a system with 8 CPUs had a sustained load significantly above 8, that would be a stronger indication that work is queuing.

However, load average should never be interpreted using a fixed threshold alone. CPU utilization, I/O wait, process state, workload type, and the trend must also be investigated.

---

# 10. Inspect `/proc/loadavg`

Linux exposes load information through `/proc`.

Command:

```bash
cat /proc/loadavg
```

Output:

```text
0.18 0.34 0.67 1/260 22
```

Interpretation:

```text
0.18   → 1-minute load
0.34   → 5-minute load
0.67   → 15-minute load
1/260  → runnable processes / total processes
22     → most recently created process PID
```

The load had decreased compared with the earlier `uptime` output.

This was consistent with the CPU-intensive process having been stopped.

---

# 11. CPU Utilization vs Load Average

These are related but different concepts.

### CPU utilization

Answers:

> How busy are the CPUs?

Useful commands:

```bash
top
ps aux --sort=-%cpu
```

### Load average

Answers more broadly:

> How much work is competing for CPU or waiting in relevant system queues?

Useful commands:

```bash
uptime
cat /proc/loadavg
```

Therefore:

```text
High CPU
    ↓
Look for CPU-heavy processes

High load
    ↓
Check CPU count
    ↓
Check CPU utilization
    ↓
Check process states
    ↓
Investigate CPU contention / I/O / blocked processes
```

---

# 12. Important Production Lesson

Do not assume:

> "CPU is high, so restart the server."

Instead:

```text
Observe
  ↓
Gather evidence
  ↓
Identify the process
  ↓
Understand the process
  ↓
Take the least disruptive corrective action
  ↓
Verify recovery
  ↓
Find the underlying cause
```

In a real production incident, the correct action could be very different depending on what the process is.

For example:

* A legitimate application consuming CPU may require scaling or optimization.
* A runaway process may need to be restarted.
* A batch job may be expected to consume CPU.
* High load with low CPU utilization may require investigation of I/O or blocked processes.
* Repeated CPU spikes may indicate an application or capacity problem rather than a one-time incident.

---

# Key Commands Learned

| Command               | Purpose                              |
| --------------------- | ------------------------------------ |
| `nproc`               | Show available CPU count             |
| `top`                 | Real-time system/process monitoring  |
| `ps aux`              | Show running processes               |
| `ps aux --sort=-%cpu` | Find CPU-heavy processes             |
| `ps -p PID -o ...`    | Inspect a specific process           |
| `kill PID`            | Gracefully terminate a process       |
| `uptime`              | Show system uptime and load average  |
| `cat /proc/loadavg`   | Read kernel load-average information |

---

# Troubleshooting Pattern

For a slow server suspected of having CPU problems:

```text
PROBLEM
Server is slow
     ↓
OBSERVE
top
     ↓
IDENTIFY
ps aux --sort=-%cpu
     ↓
INVESTIGATE
ps -p PID -o ...
     ↓
ACTION
kill/restart/scale/fix as appropriate
     ↓
VERIFY
top / ps / uptime
     ↓
DOCUMENT
Root cause + fix + prevention
```

---

# Interview Question

### Q: A server is slow. How would you troubleshoot high CPU?

A strong answer:

> "I would first check CPU utilization and load average using tools such as `top` and `uptime`. Then I would identify the processes consuming the most CPU using `ps aux --sort=-%cpu`. I would inspect the suspicious process using its PID, understand whether the CPU usage is expected, and then take the least disruptive corrective action. After the fix, I would verify CPU and load recovery and investigate the underlying cause to prevent recurrence."

### Q: What is the difference between CPU utilization and load average?

> "CPU utilization tells me how busy the CPUs are, while load average represents the amount of work that is runnable or waiting. I also need to compare load average with the number of CPUs and investigate process states and I/O when the numbers don't tell the same story."

---

# Final Takeaways

* A process using nearly 100% CPU does not necessarily mean the entire server is overloaded.
* Always check the number of available CPUs.
* `ps` helps identify CPU-heavy processes.
* Inspect a process before taking action.
* `kill` sends SIGTERM by default.
* Always verify that the problem actually disappeared after the fix.
* CPU utilization and load average are different metrics.
* Load average must be interpreted relative to CPU count and system behavior.
* `/proc/loadavg` provides kernel-level load information.
* Production troubleshooting should be evidence-driven rather than based on assumptions.

---

## Production Mindset

The goal is not to memorize Linux commands.

The goal is to answer:

> **What is happening → How do I prove it → Why is it happening → What is the safest fix → How do I verify the fix → How do I prevent it?**
