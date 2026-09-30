# Linux Lab 09 — Logs & Log Troubleshooting

## Objective

Learn how to investigate application logs, identify errors, understand surrounding events, monitor logs in real time, and collect evidence during an application incident.

## Scenario

An application is running, but users report that requests are failing.

Instead of immediately assuming the application or database is down, we investigate the application logs to determine:

* What happened?
* When did it happen?
* What happened immediately before and after the error?
* Did the application recover?
* Are new errors still occurring?
* How large is the log file?

---

## Environment

* OS: Ubuntu 24.04 LTS
* Environment: Docker container
* User: root
* Application log: `/opt/myapp/logs/app.log`

---

## 1. Create an Application Log

Created the application log directory:

```bash
mkdir -p /opt/myapp/logs
```

Created a sample application log containing normal events, errors, warnings, and recovery:

```text
2026-09-30 14:00:01 INFO Application started
2026-09-30 14:00:05 INFO Health check passed
2026-09-30 14:00:10 INFO Processing request
2026-09-30 14:00:15 INFO Processing request
2026-09-30 14:00:20 ERROR Database connection failed
2026-09-30 14:00:21 ERROR Database connection timeout
2026-09-30 14:00:25 WARN Retrying database connection
2026-09-30 14:00:30 INFO Database connection restored
2026-09-30 14:00:35 INFO Processing request
```

---

## 2. Inspect the Complete Log

```bash
cat /opt/myapp/logs/app.log
```

This is useful for a small log file, but production logs can contain thousands or millions of lines.

Therefore, we normally narrow the investigation.

---

## 3. Check Recent Events

```bash
tail -n 5 /opt/myapp/logs/app.log
```

Output showed:

```text
2026-09-30 14:00:20 ERROR Database connection failed
2026-09-30 14:00:21 ERROR Database connection timeout
2026-09-30 14:00:25 WARN Retrying database connection
2026-09-30 14:00:30 INFO Database connection restored
2026-09-30 14:00:35 INFO Processing request
```

### Why `tail`?

When troubleshooting an active application, recent events are often more relevant than the entire historical log.

---

## 4. Find Errors

```bash
grep ERROR /opt/myapp/logs/app.log
```

Result:

```text
2026-09-30 14:00:20 ERROR Database connection failed
2026-09-30 14:00:21 ERROR Database connection timeout
```

This quickly identifies log entries containing `ERROR`.

---

## 5. Find Errors and Warnings

```bash
grep -E 'ERROR|WARN' /opt/myapp/logs/app.log
```

Result:

```text
2026-09-30 14:00:20 ERROR Database connection failed
2026-09-30 14:00:21 ERROR Database connection timeout
2026-09-30 14:00:25 WARN Retrying database connection
```

---

## 6. Get Context Around an Error

Used:

```bash
grep -n -C 2 ERROR /opt/myapp/logs/app.log
```

Output:

```text
3-2026-09-30 14:00:10 INFO Processing request
4-2026-09-30 14:00:15 INFO Processing request
5:2026-09-30 14:00:20 ERROR Database connection failed
6:2026-09-30 14:00:21 ERROR Database connection timeout
7-2026-09-30 14:00:25 WARN Retrying database connection
8-2026-09-30 14:00:30 INFO Database connection restored
```

### Understanding the command

```text
-n
```

Shows line numbers.

```text
-C 2
```

Shows two lines of context before and after the match.

The sequence revealed:

```text
Normal requests
      ↓
Database connection failure
      ↓
Connection timeout
      ↓
Retry
      ↓
Database connection restored
```

---

## 7. Important Troubleshooting Lesson

The log proves that there was a database connection problem.

It does **not** prove why the connection failed.

Possible causes could include:

* Database unavailable
* Network connectivity problem
* DNS resolution problem
* Firewall/security rules
* Incorrect database address
* Incorrect credentials
* Connection exhaustion
* Database overload

Therefore:

> A log message is evidence, not automatically the root cause.

This is an important SRE troubleshooting principle.

---

## 8. Monitor Logs in Real Time

Used:

```bash
tail -f /opt/myapp/logs/app.log
```

`-f` means **follow the file**.

The command continues running and displays new log entries as they are written.

A new log entry was generated from another terminal:

```text
2026-09-30 14:01:00 INFO New request received
```

The event appeared immediately in the `tail -f` terminal.

Stopped the command with:

```text
Ctrl+C
```

---

## 9. Monitor Only Errors in Real Time

Used:

```bash
tail -f /opt/myapp/logs/app.log | grep ERROR
```

Then generated:

```text
2026-09-30 14:02:00 INFO Health check passed
2026-09-30 14:02:05 ERROR Database connection failed
```

The `INFO` message was filtered out.

The error appeared:

```text
2026-09-30 14:02:05 ERROR Database connection failed
```

### Why this is useful

During an incident, an application may produce a large number of normal log messages.

Filtering the stream allows us to focus on the events relevant to the investigation.

---

## 10. Check Log Size

Count the number of log lines:

```bash
wc -l /opt/myapp/logs/app.log
```

Result:

```text
13 /opt/myapp/logs/app.log
```

Check disk usage:

```bash
du -h /opt/myapp/logs/app.log
```

Result:

```text
4.0K    /opt/myapp/logs/app.log
```

### Production relevance

Log files continuously grow.

If logs are not rotated, compressed, or shipped elsewhere, they can eventually consume significant disk space.

This can lead to a separate production incident:

```text
Application generates logs
        ↓
Log file grows
        ↓
Disk usage increases
        ↓
Disk becomes full
        ↓
Applications may start failing
```

We will investigate this properly later in the **Disk Usage** lab.

---

## Production Troubleshooting Workflow

A basic log investigation can follow this pattern:

```text
Incident
   ↓
Check recent logs
   ↓
tail
   ↓
Search for errors
   ↓
grep
   ↓
Inspect surrounding context
   ↓
grep -C
   ↓
Watch new events
   ↓
tail -f
   ↓
Filter important events
   ↓
grep ERROR
   ↓
Form a hypothesis
   ↓
Test the hypothesis
   ↓
Fix
   ↓
Verify recovery
```

---

## Key Commands

| Command                      | Purpose                  |
| ---------------------------- | ------------------------ |
| `cat file`                   | Read a file              |
| `tail file`                  | Show the end of a file   |
| `tail -n 5 file`             | Show the last 5 lines    |
| `tail -f file`               | Follow new log entries   |
| `grep ERROR file`            | Find errors              |
| `grep -E 'ERROR\|WARN' file` | Find multiple patterns   |
| `grep -n file`               | Show line numbers        |
| `grep -C 2 pattern file`     | Show surrounding context |
| `wc -l file`                 | Count lines              |
| `du -h file`                 | Show disk usage          |

---

## Interview Takeaways

### How would you investigate an application failure?

Start with recent application logs:

```bash
tail -n 100 /path/to/app.log
```

Then search for errors:

```bash
grep ERROR /path/to/app.log
```

Then inspect surrounding events:

```bash
grep -n -C 3 ERROR /path/to/app.log
```

For an active incident:

```bash
tail -f /path/to/app.log
```

### What is the difference between `tail` and `tail -f`?

`tail` displays the current end of the file.

`tail -f` continues watching the file and displays new lines as they are written.

### Does a database connection error prove that the database is down?

No.

It proves that the application experienced a database connection problem. The actual cause requires further investigation.

---

## What I Practiced

* [x] Read application logs
* [x] Inspect recent log entries
* [x] Search for errors with `grep`
* [x] Search for errors and warnings
* [x] Display line numbers
* [x] Inspect surrounding context
* [x] Monitor logs in real time
* [x] Filter live logs
* [x] Count log lines
* [x] Check log disk usage
* [x] Reconstruct an incident from timestamps
* [x] Distinguish evidence from root cause

## Troubleshooting Principle

```text
Don't ask:
"What does this error prove?"

Ask:
"What does this error tell me,
and what evidence do I need next?"
```

This prevents premature root-cause assumptions during production incidents.
