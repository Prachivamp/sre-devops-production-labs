cat > 03-networking/README.md <<'EOF'
# Phase 2: Networking Production Labs

## Objective

Build practical networking and production troubleshooting skills for SRE and DevOps roles.

These labs focus on understanding network behavior, diagnosing connectivity failures, and following a structured troubleshooting process.

## Networking Lab Index

| Lab | Topic | Status |
|---|---|---|
| 01 | IP Addresses, Routes, and Connectivity | Completed |
| 02 | TCP Ports, Listening Sockets, and Connection Troubleshooting | Completed |
| 03 | DNS Troubleshooting | Planned |
| 04 | TCP Connection Troubleshooting | Planned |
| 05 | HTTP and HTTPS Troubleshooting | Planned |
| 06 | TLS/SSL Certificate Troubleshooting | Planned |
| 07 | Linux Firewall and Access Rules | Planned |
| 08 | Packet Capture Fundamentals with tcpdump | Planned |
| 09 | Docker Networking and Container Communication | Planned |
| 10 | Reverse Proxy and Load Balancer Troubleshooting | Planned |
| 11 | Network Performance: Latency, Packet Loss, and Throughput | Planned |
| 12 | Production Network Incident Simulation | Planned |

## Learning Approach

Each lab will include:

1. **Objective** — what we are learning and why it matters.
2. **Hands-on commands** — tested in our lab environment.
3. **Expected output** — what success or failure looks like.
4. **Troubleshooting** — how to identify the failing layer.
5. **Production relevance** — common SRE/DevOps incident scenarios.
6. **Interview takeaways** — how to explain the issue and resolution.
7. **Documentation** — findings recorded in the lab README.

## Core Troubleshooting Workflow

**Observe the symptom → Check connectivity → Check DNS → Check routes and ports → Test the application → Inspect logs → Identify the root cause → Verify recovery → Document findings**

## Progress

- [x] Lab 01: IP Addresses, Routes, and Connectivity
- [x] Lab 02: TCP Ports, Listening Sockets, and Connection Troubleshooting
- [ ] Lab 03: DNS Troubleshooting

## Notes

- Labs are designed for hands-on learning, not just memorizing commands.
- Record actual command output and findings in each lab's README.
- Planned labs may be adjusted as new troubleshooting gaps are identified.
EOF

git status --short