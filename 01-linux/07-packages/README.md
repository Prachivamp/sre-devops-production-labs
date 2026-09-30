# Linux Lab 07 — Package Management

## Objective

Learn how to investigate, install, remove, and verify Linux packages using Ubuntu's package management tools.

The lab simulates a common production problem:

> An application or troubleshooting script requires a command, but the command is not installed on the server.

---

## Environment

* OS: Ubuntu 24.04.5 LTS
* Architecture: ARM64
* Environment: Docker container
* Package manager: APT
* Package database: `dpkg`

---

## Scenario

The `curl` command was required on the server, but it was not installed.

Initial checks:

```bash
command -v curl
```

No output was returned.

Then:

```bash
dpkg -l curl
```

Result:

```text
dpkg-query: no packages found matching curl
```

This confirmed that the `curl` package was not installed.

---

## Step 1 — Check the Operating System

```bash
cat /etc/os-release
```

Result:

```text
PRETTY_NAME="Ubuntu 24.04.5 LTS"
VERSION_ID="24.04"
VERSION_CODENAME=noble
```

---

## Step 2 — Refresh Package Metadata

```bash
apt update
```

This downloaded the latest package metadata from the configured Ubuntu repositories.

Important:

```text
apt update
```

does **not** install or upgrade packages.

It refreshes the local information about available packages.

The command reported:

```text
4 packages can be upgraded.
```

We did not upgrade them because upgrading packages is a separate operational decision.

---

## Step 3 — Install curl

```bash
apt install -y curl
```

APT installed `curl` along with its required dependencies.

Some dependencies included:

* `libcurl4t64`
* `openssl`
* `ca-certificates`
* `libssh`
* `libnghttp2`
* LDAP/Kerberos-related libraries

This demonstrated that installing one package can also install supporting dependencies.

---

## Step 4 — Verify the Installation

### Check command location

```bash
command -v curl
```

Result:

```text
/usr/bin/curl
```

### Check the installed version

```bash
curl --version
```

Result included:

```text
curl 8.5.0
```

### Check package state

```bash
dpkg -l curl
```

Result:

```text
ii  curl  8.5.0-2ubuntu10.15  arm64
```

The `ii` state indicates that the package is installed.

---

## Step 5 — Check Installed Packages Using APT

```bash
apt list --installed 2>/dev/null | grep '^curl/'
```

Result:

```text
curl/noble-updates,noble-security,now 8.5.0-2ubuntu10.15 arm64 [installed]
```

This showed that the installed package was available from Ubuntu's `noble-updates` / `noble-security` repositories.

---

# Troubleshooting Exercise

To simulate a real operational problem, `curl` was deliberately removed.

## Remove the package

```bash
apt remove -y curl
```

APT reported:

```text
The following packages will be REMOVED:
  curl
```

After removal, running:

```bash
curl --version
```

produced:

```text
bash: /usr/bin/curl: No such file or directory
```

This simulated a missing dependency or command.

---

## Interesting Troubleshooting Detail — Bash Command Cache

Immediately after removing `curl`,:

```bash
command -v curl
```

still returned:

```text
/usr/bin/curl
```

However:

```bash
curl --version
```

failed because the executable had actually been removed.

This demonstrated that Bash can cache command locations.

We investigated this using:

```bash
ls -l /usr/bin/curl
```

and:

```bash
type curl
```

Then cleared the Bash command cache:

```bash
hash -r
```

After clearing the cache:

```bash
command -v curl
```

no longer reported the removed executable.

### Lesson

A command lookup result should not always be treated as proof that the executable is currently functional.

Verify the actual system state.

---

# Recovery

The missing package was restored:

```bash
apt install -y curl
```

Then the installation was verified again.

### Command location

```bash
command -v curl
```

Result:

```text
/usr/bin/curl
```

### Version

```bash
curl --version
```

Result:

```text
curl 8.5.0
```

### Package state

```bash
dpkg -l curl
```

Result:

```text
ii  curl  8.5.0-2ubuntu10.15  arm64
```

The binary was also executed directly:

```bash
/usr/bin/curl
```

It executed successfully and displayed curl's usage information.

---

# Important Commands

| Command                 | Purpose                               |
| ----------------------- | ------------------------------------- |
| `apt update`            | Refresh available package metadata    |
| `apt install <package>` | Install a package                     |
| `apt remove <package>`  | Remove a package                      |
| `apt list --installed`  | List installed packages               |
| `dpkg -l <package>`     | Inspect package installation state    |
| `command -v <command>`  | Find the command executable           |
| `hash -r`               | Clear Bash's cached command locations |

---

# Production Relevance

Package management is an important part of Linux operations.

A production server may fail because:

* a required package was never installed
* a package was accidentally removed
* a deployment image is missing a dependency
* a package installation failed
* package repositories are unavailable
* package metadata is outdated
* a dependency has an incompatible version

A useful troubleshooting flow is:

```text
Application/Script fails
        ↓
Identify missing command
        ↓
command -v <command>
        ↓
Check package state
        ↓
dpkg -l <package>
        ↓
Refresh package metadata
        ↓
apt update
        ↓
Install required package
        ↓
apt install <package>
        ↓
Verify
        ↓
command -v
version check
package state
        ↓
Confirm application recovery
```

---

# Key Takeaways

1. `apt update` refreshes package information; it does not install updates.
2. `apt install` installs packages and required dependencies.
3. `apt remove` removes a package.
4. `dpkg -l` can be used to inspect package state.
5. `command -v` helps locate executables.
6. A command lookup result does not always prove the executable is currently functional.
7. `hash -r` clears Bash's cached command locations.
8. Always verify a change after making it.
9. Package dependencies matter in production environments.
10. Troubleshooting should be based on evidence rather than assumptions.

---

## Troubleshooting Pattern Practiced

```text
PROBLEM
   ↓
Observe
   ↓
Gather evidence
   ↓
Identify missing dependency
   ↓
Install/fix
   ↓
Verify
   ↓
Confirm recovery
   ↓
Document
```

This is the same general troubleshooting approach that will be used throughout the SRE/DevOps labs.
