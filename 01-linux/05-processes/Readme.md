# Linux Lab 05 — Processes & High CPU Troubleshooting

## Objective

Learn how to inspect and troubleshoot Linux processes.

In this lab, we simulated a production incident where a process consumed almost 100% CPU.

We learned how to:

* List running processes
* Identify CPU-heavy processes
* Understand PIDs
* Inspect a specific process
* Stop a process gracefully
* Verify that the problem was resolved
* Understand when `kill -9` may be necessary

---

## Production Scenario

Imagine an application server becomes slow.

Users report:

> "The application is responding very slowly."

One possible cause is a process consuming excessive CPU.

Instead of immediately restarting the server, we investigate the running processes.

The troubleshooting approach is:

```text
Server is slow
     ↓
Check processes
     ↓
Find high CPU process
     ↓
Identify PID
     ↓
Inspect process
     ↓
Stop or fix the process
     ↓
Verify
```

---

# 1. List Running Processes

Started with:

```bash
ps
```

This shows a snapshot of processes associated with the current terminal/session.

Then used:

```bash
ps aux
```

This provides a broader view of running processes.

Important fields include:

| Field     | Meaning                  |
| --------- | ------------------------ |
| `USER`    | User running the process |
| `PID`     | Process ID               |
| `%CPU`    | CPU usage                |
| `%MEM`    | Memory usage             |
| `STAT`    | Process state            |
| `COMMAND` | Command/program          |

---

# 2. Find High CPU Processes

Used:

```bash
ps aux --sort=-%cpu | head
```

This sorts processes by CPU usage, with the highest CPU consumers first.

This is useful during a CPU-related incident.

---

# 3. Simulate a High CPU Incident

Created a CPU-intensive process:

```bash
yes > /dev/null &
```

The `&` runs the command in the background.

The shell returned a PID:

```text
[1] 14
```

The important value was:

```text
PID = 14
```

The `yes` command continuously generates output.

Redirecting it to:

```text
/dev/null
```

discards that output while allowing the process to continue consuming CPU.

---

# 4. Identify the High CPU Process

Ran:

```bash
ps aux --sort=-%cpu | head
```

The result showed:

```text
root  14  99.9  ... yes
```

This gave us the evidence:

```text
Process: yes
PID: 14
CPU: approximately 100%
```

This was our simulated production problem.

---

# 5. Important Troubleshooting Lesson — Verify the PID

During the investigation, the process list also showed the `ps` command itself.

A temporary diagnostic command can briefly appear near the top of the CPU list.

An initial inspection was attempted against PID `15`, but that process had already exited.

The actual high-CPU process was PID `14`.

This demonstrated an important troubleshooting principle:

> Process lists change continuously. Always verify that the PID you are investigating still belongs to the process you identified.

---

# 6. Inspect the Specific Process

Used:

```bash
ps -p 14 -o pid,ppid,user,%cpu,%mem,stat,etime,cmd
```

This allows us to inspect a specific process.

Important fields:

| Field   | Meaning              |
| ------- | -------------------- |
| `PID`   | Process ID           |
| `PPID`  | Parent Process ID    |
| `USER`  | Process owner        |
| `%CPU`  | CPU usage            |
| `%MEM`  | Memory usage         |
| `STAT`  | Process state        |
| `ETIME` | Elapsed running time |
| `CMD`   | Command              |

This is more useful than simply knowing that CPU is high because it gives us information about the actual process.

---

# 7. Stop the Problematic Process

Once the process was identified, we used:

```bash
kill 14
```

By default, `kill` sends `SIGTERM`.

This asks the process to terminate gracefully.

The shell confirmed:

```text
[1]+ Terminated yes > /dev/null
```

---

# 8. Verify the Process Stopped

Checked the PID:

```bash
ps -p 14
```

The process was no longer running.

Then checked CPU usage again:

```bash
ps aux --sort=-%cpu | head
```

The `yes` process was gone.

The remaining high CPU percentage shown briefly for the `ps` command itself was caused by the diagnostic command while it was executing. It was not a persistent application problem.

---

# 9. `kill` vs `kill -9`

The normal approach is:

```bash
kill <PID>
```

This sends `SIGTERM`.

The process gets an opportunity to exit cleanly.

If a process refuses to terminate and investigation indicates that forceful termination is appropriate, an escalation may be:

```bash
kill -9 <PID>
```

`kill -9` sends `SIGKILL`.

Unlike `SIGTERM`, the process cannot catch or handle `SIGKILL`.

Therefore:

```text
kill <PID>
     ↓
SIGTERM
     ↓
Graceful termination
     ↓
Check again
     ↓
Still running?
     ↓
Investigate
     ↓
Escalate if appropriate
     ↓
kill -9 <PID>
```

In production, `kill -9` should not be the automatic first response.

---

# Useful Commands

### List processes

```bash
ps
```

### List detailed processes

```bash
ps aux
```

### Find high CPU processes

```bash
ps aux --sort=-%cpu | head
```

### Interactive process monitoring

```bash
top
```

Press `q` to exit `top`.

### Inspect one process

```bash
ps -p <PID> -o pid,ppid,user,%cpu,%mem,stat,etime,cmd
```

### Gracefully terminate

```bash
kill <PID>
```

### Force termination

```bash
kill -9 <PID>
```

---

# Production Troubleshooting Pattern

When someone reports:

> "The server is slow."

Do not immediately restart the server.

Start by gathering evidence.

```text
1. Observe
      ↓
2. Check CPU / memory
      ↓
3. Identify suspicious process
      ↓
4. Record the PID
      ↓
5. Inspect the process
      ↓
6. Determine what the process is doing
      ↓
7. Take the smallest appropriate action
      ↓
8. Verify the result
```

For a CPU incident:

```bash
ps aux --sort=-%cpu | head
```

is a useful first investigation command.

---

# Production Relevance

High CPU can be caused by many things, including:

* Application bugs
* Infinite loops
* Excessive computation
* Unexpected workloads
* Background jobs
* Misconfigured processes
* Traffic spikes
* Runaway scripts

Finding a high-CPU process identifies **where to investigate**, but does not automatically explain **why** the process is consuming CPU.

For example:

```text
High CPU
   ↓
Process A
```

does not necessarily mean:

```text
Process A is broken.
```

We still need to understand what the process is supposed to be doing.

This distinction is important in production troubleshooting.

---

# Key Takeaways

1. A Linux process is a running instance of a program.
2. Every process has a PID.
3. `ps` provides a snapshot of running processes.
4. `top` provides interactive process monitoring.
5. `%CPU` helps identify CPU-heavy processes.
6. Always verify the PID before taking action.
7. `kill <PID>` normally sends `SIGTERM`.
8. `kill -9 <PID>` sends `SIGKILL` and should be treated as an escalation.
9. A high-CPU process is evidence of a problem location, not necessarily the root cause.
10. Always verify that the system recovered after taking action.

---

# Troubleshooting Principle

The main lesson from this lab:

```text
Symptom
  ↓
"Server is slow"
  ↓
Gather evidence
  ↓
Find high CPU process
  ↓
Identify PID
  ↓
Inspect process
  ↓
Take controlled action
  ↓
Verify
```

This same troubleshooting approach will be used throughout the remaining SRE/DevOps labs.
