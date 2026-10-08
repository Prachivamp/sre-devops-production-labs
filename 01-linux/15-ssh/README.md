# Linux Lab 15 — SSH Troubleshooting

## Objective

Learn how to troubleshoot SSH connectivity and authentication problems on a Linux server.

This lab covers:

* SSH client vs SSH server
* Checking whether SSH is installed
* Checking whether `sshd` is running
* Checking whether port 22 is listening
* Testing an SSH connection
* Understanding authentication failures
* Inspecting effective SSH configuration
* Understanding `PermitRootLogin`
* Configuring SSH key authentication
* Verifying successful SSH access

---

## Production Scenario

Imagine an engineer reports:

> "I can't SSH into the server."

The goal is to determine which layer is failing:

```text
SSH software
     ↓
SSH service
     ↓
Port 22
     ↓
Network connection
     ↓
Authentication
     ↓
SSH configuration
     ↓
Successful login
```

---

## Environment

* Ubuntu 24.04
* Docker container
* OpenSSH
* Container hostname: `c6cd124e0208`

---

# Step 1 — Check Whether SSH Is Installed

Initially, both commands returned no output:

```bash
command -v ssh
command -v sshd
```

This showed that the SSH client and server were not installed.

Installed the SSH server:

```bash
apt update
apt install -y openssh-server
```

After installation:

```bash
command -v ssh
```

Result:

```text
/usr/bin/ssh
```

And:

```bash
command -v sshd
```

Result:

```text
/usr/sbin/sshd
```

### Lesson

Installing a package does not necessarily mean its service is running.

---

# Step 2 — Check Listening Ports

Checked listening TCP ports:

```bash
ss -lntp
```

Initially, there was no SSH listener on port 22.

---

# Step 3 — Start SSH Server

This Docker container does not use `systemd` as PID 1, so `systemctl` is not the appropriate way to manage the service here.

Created the required runtime directory:

```bash
mkdir -p /run/sshd
```

Initially tried:

```bash
sshd
```

This returned:

```text
sshd re-exec requires execution with an absolute path
```

The installed binary was located at:

```text
/usr/sbin/sshd
```

Started it using the absolute path:

```bash
/usr/sbin/sshd
```

---

# Step 4 — Verify Port 22

Checked:

```bash
ss -lntp
```

Result:

```text
LISTEN  0  128  0.0.0.0:22  0.0.0.0:*  users:(("sshd",pid=1125,fd=3))
LISTEN  0  128  [::]:22     [::]:*     users:(("sshd",pid=1125,fd=4))
```

This confirmed that `sshd` was listening on port 22.

### Interpretation

```text
0.0.0.0:22
```

means SSH is listening on port 22 on all IPv4 interfaces.

```text
[::]:22
```

means SSH is listening on port 22 for IPv6 as well.

---

# Step 5 — Verify SSH Client

Checked the SSH client version:

```bash
ssh -V
```

Result:

```text
OpenSSH_9.6p1 Ubuntu-3ubuntu13.19, OpenSSL 3.0.13 30 Jan 2024
```

Current user:

```bash
whoami
```

Result:

```text
root
```

---

# Step 6 — Test SSH Connection

Attempted to connect to the local SSH server:

```bash
ssh root@127.0.0.1
```

The SSH server was reachable and presented its host key.

After accepting the host key, SSH requested a password.

The password authentication failed:

```text
Permission denied, please try again.
```

### Important Observation

This proved that the problem was **not simply port 22 connectivity**.

The SSH connection had already reached the server.

The failure was at the authentication layer.

---

# Step 7 — Check Root Account Status

Checked the root password status:

```bash
passwd -S root
```

Initially:

```text
root L ...
```

`L` indicated that the root account password was locked.

For the purposes of this lab, a temporary root password was configured:

```bash
passwd root
```

Then:

```bash
passwd -S root
```

showed:

```text
root P ...
```

`P` indicated that a password was configured.

However, SSH password authentication still failed.

This demonstrated an important troubleshooting principle:

> Fixing one suspected cause does not mean the investigation is finished. Re-test and continue narrowing the problem.

---

# Step 8 — Inspect SSH Configuration

Checked the main SSH configuration file:

```bash
grep -E '^(PermitRootLogin|PasswordAuthentication)' /etc/ssh/sshd_config
```

There was no output because those directives were not explicitly defined in that file.

Instead of guessing, checked the **effective configuration**:

```bash
sshd -T | grep -E '^(permitrootlogin|passwordauthentication)'
```

Result:

```text
permitrootlogin without-password
passwordauthentication yes
```

This was the key discovery.

---

# Understanding `PermitRootLogin without-password`

The setting:

```text
permitrootlogin without-password
```

means root cannot authenticate using a password.

Root login is permitted through non-password authentication methods such as SSH public keys.

Therefore:

```text
passwordauthentication yes
```

does not mean that root is allowed to log in using a password.

The specific `PermitRootLogin` policy still restricts root password authentication.

---

# Step 9 — Check SSH Authentication Methods

Checked:

```bash
sshd -T | grep -E '^(permitrootlogin|pubkeyauthentication|passwordauthentication)'
```

Result:

```text
permitrootlogin without-password
pubkeyauthentication yes
passwordauthentication yes
```

This showed that:

* Password authentication is enabled generally.
* Public-key authentication is enabled.
* Root password authentication is specifically restricted.
* Root public-key authentication is allowed.

---

# Step 10 — Configure SSH Key Authentication

Generated an Ed25519 SSH key:

```bash
ssh-keygen -t ed25519
```

The key pair was created under:

```text
/root/.ssh/
```

The important files were:

```text
id_ed25519
id_ed25519.pub
```

### Security Note

The private key:

```text
id_ed25519
```

must never be shared.

Only the public key:

```text
id_ed25519.pub
```

should be placed in `authorized_keys`.

---

# Step 11 — Configure `authorized_keys`

Created the SSH directory:

```bash
mkdir -p /root/.ssh
```

Added the public key:

```bash
cat /root/.ssh/id_ed25519.pub >> /root/.ssh/authorized_keys
```

Configured secure permissions:

```bash
chmod 700 /root/.ssh
chmod 600 /root/.ssh/authorized_keys
```

Verified:

```bash
ls -ld /root/.ssh
ls -l /root/.ssh/authorized_keys
```

Result:

```text
drwx------ ... /root/.ssh
-rw------- ... /root/.ssh/authorized_keys
```

The duplicate public-key entry created during the exercise was removed so that only one authorized key remained.

---

# Step 12 — Test SSH Key Authentication

Tested SSH while explicitly disabling password authentication:

```bash
ssh -o PreferredAuthentications=publickey -o PasswordAuthentication=no root@127.0.0.1
```

The login succeeded.

Verified the user:

```bash
whoami
```

Result:

```text
root
```

Verified the hostname:

```bash
hostname
```

Result:

```text
c6cd124e0208
```

This confirmed successful SSH key authentication.

---

# Complete Troubleshooting Flow

The incident can be represented as:

```text
"I can't SSH into the server."
             ↓
Is SSH installed?
             ↓
        ssh / sshd
             ↓
Is sshd running?
             ↓
        sshd process
             ↓
Is port 22 listening?
             ↓
        ss -lntp
             ↓
Can the client reach port 22?
             ↓
        ssh
             ↓
Does authentication succeed?
             ↓
        Permission denied
             ↓
Check account status
             ↓
Check effective SSH configuration
             ↓
PermitRootLogin = without-password
             ↓
Root password authentication blocked
             ↓
Use SSH public-key authentication
             ↓
Successful login ✅
```

---

# Important SSH Commands

### Check SSH client

```bash
ssh -V
```

### Locate SSH binaries

```bash
command -v ssh
command -v sshd
```

### Check listening ports

```bash
ss -lntp
```

### Check SSH process

```bash
ps aux | grep '[s]shd'
```

### Check effective SSH configuration

```bash
sshd -T
```

### Check specific SSH settings

```bash
sshd -T | grep -E '^(permitrootlogin|pubkeyauthentication|passwordauthentication)'
```

### Test SSH connection

```bash
ssh user@server
```

### Test using only public-key authentication

```bash
ssh -o PreferredAuthentications=publickey -o PasswordAuthentication=no user@server
```

---

# Connection vs Authentication

A critical troubleshooting distinction:

## Connection failure

Examples:

```text
Connection refused
Connection timed out
No route to host
```

These point toward problems involving:

* Network connectivity
* Routing
* Firewall
* Port availability
* SSH service

Useful checks:

```bash
ping
ss -lntp
ip route
```

---

## Authentication failure

Example:

```text
Permission denied
```

The SSH server was reached, but authentication failed.

Possible causes include:

* Incorrect username
* Incorrect password
* Locked account
* Invalid SSH key
* Incorrect `authorized_keys`
* Incorrect file permissions
* SSH authentication policy
* Root login restrictions

Useful checks:

```bash
passwd -S user
sshd -T
ls -la ~/.ssh
```

---

# Production Security Lessons

Although this lab used root for simplicity, directly allowing root password SSH access is generally a poor production practice.

A more secure approach is usually:

```text
SSH key authentication
        +
normal user account
        +
sudo for privileged operations
```

For production systems, SSH access should also be protected using appropriate network controls, key management, logging, and access policies.

Never expose a temporary lab password or private SSH key in GitHub.

---

# Interview-Ready Answer

### Question

> "You cannot SSH into a production server. How would you troubleshoot it?"

### Answer

> "I'd troubleshoot it layer by layer. First I'd verify network connectivity and whether port 22 is reachable. On the server, if I have another access path, I'd check whether the SSH daemon is running and whether port 22 is listening using `ss -lntp`. If the connection reaches the SSH server but authentication fails with permission denied, I'd investigate the username, account status, SSH keys, `authorized_keys` permissions, and the effective SSH configuration using `sshd -T`. I'd identify whether password or public-key authentication is allowed and check any root-login restrictions. After fixing the issue, I'd verify the SSH connection and confirm successful authentication."

---

# Key Takeaways

* SSH client and SSH server are different components.
* Installing `openssh-server` does not automatically mean `sshd` is running.
* `ss -lntp` is useful for verifying whether port 22 is listening.
* A successful TCP/SSH connection does not guarantee successful authentication.
* `Permission denied` after reaching the SSH server usually means an authentication or authorization issue.
* `sshd -T` shows the effective SSH configuration.
* `PermitRootLogin without-password` prevents root password authentication.
* SSH public-key authentication is preferable to root password authentication.
* SSH private keys must never be committed to GitHub.
* Always verify recovery after making a change.

---

## Troubleshooting Philosophy

The main lesson from this lab is:

```text
Don't guess.
Observe → Gather evidence → Narrow the layer → Test the hypothesis → Fix → Verify
```

This same approach applies to SSH, applications, databases, Kubernetes, networking, and most production incidents.
