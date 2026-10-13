# Lab 19: Linux Text Processing and Log Analysis

## Objective

Practice analyzing application access logs using Linux text-processing commands to identify HTTP errors, failing endpoints, and slow requests.

## Production Scenario

An application is experiencing errors and slow responses. The SRE team needs to identify which endpoints are failing most frequently and which requests have high latency.

## Environment

* OS: Ubuntu 24.04
* Environment: Docker container
* Log file: `/opt/myapp/logs/access.log`
* Tools: `grep`, `awk`, `sort`, `uniq`

## Step 1: Create a Sample Access Log

Created a separate access log containing timestamps, severity levels, HTTP methods, endpoints, status codes, and response times.

```bash
cat /opt/myapp/logs/access.log
```

## Step 2: Filter Error Logs

```bash
grep 'ERROR' /opt/myapp/logs/access.log
```

**Purpose:** Display only entries marked `ERROR`.

**Finding:** Four error entries were identified.

## Step 3: Extract HTTP Status Codes

```bash
awk '{print $5}' /opt/myapp/logs/access.log
```

**Purpose:** Extract the fifth field, which contains the HTTP status code.

## Step 4: Count HTTP Status Codes

```bash
awk '{print $5}' /opt/myapp/logs/access.log | sort | uniq -c
```

**Results:**

| Status code | Count |
| ----------- | ----: |
| 200         |     4 |
| 500         |     4 |
| 503         |     2 |

Six of the ten sample requests returned 5xx status codes. This is a 60% server-error rate in this illustrative dataset.

## Step 5: Identify the Most Frequently Failing Endpoints

```bash
awk '$5 >= 500 {print $4}' /opt/myapp/logs/access.log | sort | uniq -c | sort -nr
```

**Results:**

| Endpoint        | 5xx errors |
| --------------- | ---------: |
| `/api/payments` |          3 |
| `/api/orders`   |          2 |
| `/api/users`    |          1 |

**Finding:** `/api/payments` had the most server errors and should be investigated first for error-related impact.

## Step 6: Rank Requests by Latency

```bash
awk '{print $6, $4, $5}' /opt/myapp/logs/access.log | sort -nr
```

**Finding:** The `/api/orders` endpoint had the slowest requests, with response times of 5,000 ms and 5,100 ms. Both returned status `503`.

## Step 7: Filter Requests Slower Than One Second

```bash
awk '{
  latency = $6
  sub(/ms$/, "", latency)
  if ((latency + 0) > 1000) {
    print "Latency:", latency "ms", "| Endpoint:", $4, "| Status:", $5
  }
}' /opt/myapp/logs/access.log
```

**Purpose:** Remove the `ms` suffix, convert the latency to a number, and display requests exceeding 1,000 ms.

**Results:** Two requests matched the threshold, both involving `/api/orders`.

## Key Commands Learned

| Command    | Purpose                                      |
| ---------- | -------------------------------------------- |
| `grep`     | Search for matching text                     |
| `awk`      | Extract fields and filter records            |
| `sort`     | Sort output                                  |
| `uniq -c`  | Count consecutive duplicate lines            |
| `sort -nr` | Sort numerically in descending order         |
| `sub()`    | Replace a matching pattern in an `awk` value |
| `\|`       | Pass one command's output to another         |

## Troubleshooting Findings

* `/api/payments` had the highest count of 5xx errors.
* `/api/orders` had the highest latency and returned `503`.
* Error frequency and response latency are different signals and should be investigated separately.
* These findings identify investigation priorities but do not establish the root cause. Further application, dependency, and infrastructure evidence would be required.

## Production Relevance

Log analysis helps SRE engineers narrow an incident to affected endpoints, quantify errors, investigate latency, and prioritize further troubleshooting.

In production, these commands should be combined with metrics, traces, deployment history, and dependency health checks.

## Troubleshooting Workflow

**Filter logs → Extract fields → Count errors → Rank endpoints → Investigate latency → Gather further evidence → Document findings**

## Lab Status

Completed hands-on practice with Linux text processing and access-log analysis.
