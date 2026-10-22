# Docker Production Labs — SRE/DevOps

## Objective

Build practical Docker skills for SRE/DevOps interviews and production support. Each lab includes hands-on commands, expected results, troubleshooting, key learnings, and interview questions.

## Progress Tracker

- [ ] Lab 01 — Docker Architecture and Core Concepts
- [ ] Lab 02 — Docker CLI and Container Lifecycle
- [ ] Lab 03 — Image Management, Tags and Layers
- [ ] Lab 04 — Ports, Environment Variables and Container Configuration
- [ ] Lab 05 — Volumes, Bind Mounts and Data Persistence
- [ ] Lab 06 — Dockerfiles and Image Builds
- [ ] Lab 07 — Multi-Stage Builds and Image Optimization
- [ ] Lab 08 — Docker Compose and Multi-Container Applications
- [ ] Lab 09 — Container Logs and Debugging
- [ ] Lab 10 — Health Checks, Restart Policies and Startup Failures
- [ ] Lab 11 — CPU, Memory, OOM Kills and Resource Limits
- [ ] Lab 12 — Container Storage and Safe Cleanup
- [ ] Lab 13 — Docker Networking Integration and DNS
- [ ] Lab 14 — Docker Security Best Practices
- [ ] Lab 15 — Registries, Image Versioning and Rollback Basics
- [ ] Lab 16 — Production Incident Troubleshooting Capstone

## Standard Lab Format

Every lab should cover:

1. Objective and production relevance
2. Architecture and important concepts
3. Hands-on commands
4. Expected output and verification
5. Common failures and troubleshooting
6. Root-cause analysis and recovery
7. Interview questions and answers
8. Cleanup instructions, where applicable

## Production Troubleshooting Checklist

When a containerized application fails, investigate in this order:

1. Container state and exit code
2. Application logs and startup command
3. Image, configuration and environment variables
4. Listening port and published port mapping
5. Network membership, DNS and dependencies
6. Health checks and restart behavior
7. CPU, memory, OOM events and disk usage
8. Security permissions and access
9. Recovery verification and incident documentation

## Completion Criteria

A lab is complete when the hands-on exercise works, the failure scenario is understood, recovery is verified, the README is saved, and the changes are committed and pushed to GitHub.

## Related Module

See `../02-Networking/` for dedicated networking fundamentals and network troubleshooting labs.