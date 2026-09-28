# Linux Lab 03 — Permissions & Ownership

## Objective

Understand Linux file permissions and ownership and troubleshoot a common production problem:

> `Permission denied`

The lab demonstrates how an application user can be unable to read a configuration file because the file is owned by the wrong user.

## Environment

* Host: macOS
* Linux environment: Ubuntu 24.04
* Runtime: Docker
* Repository: `sre-devops-production-labs`

## Commands Practiced

```bash
ls -l
ls -ld
chmod
chown
useradd
id
su
cat
```

## Linux Permission Model

Linux permissions are represented using three categories:

```text
owner
group
others
```

The three basic permissions are:

```text
r = read
w = write
x = execute
```

For example:

```text
-rw-r--r--
```

can be interpreted as:

```text
rw-  r--  r--
 │    │    │
 │    │    └── others
 │    └────── group
 └─────────── owner
```

Therefore:

```text
owner  → read + write
group  → read
others → read
```

## Hands-on Setup

Created an application configuration file:

```bash
mkdir -p /opt/myapp/config
echo "DATABASE_HOST=db.internal" > /opt/myapp/config/app.conf
```

Initial permissions:

```text
-rw-r--r-- 1 root root ... app.conf
```

The file was initially owned by `root`.

## Troubleshooting Scenario

### Problem

The application cannot read its configuration file.

The application runs as:

```text
appuser
```

The configuration file was intentionally restricted:

```bash
chmod 600 /opt/myapp/config/app.conf
```

Result:

```text
-rw------- 1 root root ... app.conf
```

An application running as `appuser` attempted to read the file:

```bash
su -s /bin/bash appuser -c "cat /opt/myapp/config/app.conf"
```

The result was:

```text
cat: /opt/myapp/config/app.conf: Permission denied
```

## Investigation

First, the application user was checked:

```bash
id appuser
```

The file ownership was checked:

```bash
ls -l /opt/myapp/config/app.conf
```

The parent directories were also checked:

```bash
ls -ld /opt/myapp
ls -ld /opt/myapp/config
```

The directory permissions allowed the application user to traverse the directories.

The file itself was the problem.

It was owned by:

```text
root:root
```

with permissions:

```text
rw-------
```

Therefore only `root` could read the file.

## Fix

The configuration file ownership was changed to the application user:

```bash
chown appuser:appuser /opt/myapp/config/app.conf
```

The file then became:

```text
-rw------- 1 appuser appuser ... app.conf
```

The application user was able to read the configuration successfully:

```bash
su -s /bin/bash appuser -c "cat /opt/myapp/config/app.conf"
```

Result:

```text
DATABASE_HOST=db.internal
```

## Setting Appropriate Permissions

The permissions were then changed to:

```bash
chmod 640 /opt/myapp/config/app.conf
```

Result:

```text
-rw-r----- 1 appuser appuser ... app.conf
```

This means:

```text
owner → read + write
group → read
others → no access
```

The application user could still read the file.

A separate `testuser` was created and used to verify that unauthorized users could not read the configuration:

```bash
useradd testuser
su -s /bin/bash testuser -c "cat /opt/myapp/config/app.conf"
```

Result:

```text
Permission denied
```

## `chmod` Numeric Permissions

Linux permissions can be represented numerically.

```text
read    = 4
write   = 2
execute = 1
```

Therefore:

```text
6 = 4 + 2 = read + write
4 = read
0 = no permissions
```

So:

```text
640
```

means:

```text
owner  = 6 → read + write
group  = 4 → read
others = 0 → no access
```

## `chmod` vs `chown`

These commands solve different problems.

### `chmod`

Changes permissions:

```bash
chmod 640 app.conf
```

### `chown`

Changes ownership:

```bash
chown appuser:appuser app.conf
```

A useful troubleshooting question is:

> Is the problem the permissions, or is the file owned by the wrong user/group?

## Production Relevance

Permission problems are extremely common in Linux production environments.

They can occur when:

* A deployment runs under the wrong user
* A configuration file is copied with incorrect ownership
* A service changes users
* A log directory has incorrect permissions
* A container runs with a different UID
* Files are restored from a backup with unexpected ownership

A common mistake is fixing permission problems with:

```bash
chmod 777
```

This grants excessive access and can create security problems.

Instead:

1. Identify the application user.
2. Check file ownership.
3. Check file permissions.
4. Check parent directory permissions.
5. Grant only the access actually required.
6. Verify using the same user that runs the application.

## Troubleshooting Pattern

```text
Permission denied
       ↓
Check application user
       ↓
Check file owner/group
       ↓
Check file permissions
       ↓
Check parent directories
       ↓
Identify mismatch
       ↓
Fix ownership or permissions
       ↓
Test as application user
       ↓
Verify unauthorized access remains blocked
```

## Key Takeaways

* Linux permissions control who can read, write, and execute files.
* Permissions apply to owner, group, and others.
* `chmod` changes permissions.
* `chown` changes ownership.
* `ls -l` shows file ownership and permissions.
* `ls -ld` is useful for inspecting directory permissions.
* Applications should generally run as dedicated non-root users.
* `chmod 777` should not be used as a default fix.
* Always verify the fix using the actual application user.

## Production Mindset

When you see:

```text
Permission denied
```

don't immediately change permissions.

First ask:

```text
Who is running the application?
Who owns the file?
What permissions does the file have?
Can the application user traverse the parent directories?
What is the minimum access required?
```

Then:

```text
Investigate → Identify → Fix → Verify
```
