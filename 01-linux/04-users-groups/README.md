# Linux Lab 04 — Users & Groups

## Objective

Learn how Linux users and groups control access to shared application resources.

In this lab, we simulate two applications that need access to the same deployment directory while preventing unrelated users from accessing it.

The lab focuses on:

* Creating users
* Creating groups
* Adding users to groups
* Group-based permissions
* Shared directories
* `setgid` on directories
* Least-privilege access
* Troubleshooting permission problems

---

## Environment

* Ubuntu 24.04
* Running inside Docker
* User: `root`

---

## Scenario

Imagine two applications:

```text
app1
app2
```

Both applications need access to:

```text
/opt/myapp/shared
```

We want:

```text
app1  → access
app2  → access
outsider → no access
```

Instead of granting permissions to individual users, we create a shared group:

```text
appteam
```

and add both application users to it.

---

# 1. Create Application Users

Created two users:

```bash
useradd -m app1
useradd -m app2
```

Verified them:

```bash
id app1
id app2
```

Both users initially had their own primary groups.

---

# 2. Create the Application Group

Created a shared group:

```bash
groupadd appteam
```

Verified:

```bash
getent group appteam
```

---

# 3. Add Users to the Group

Added both application users to `appteam`:

```bash
usermod -aG appteam app1
usermod -aG appteam app2
```

Verified:

```bash
id app1
id app2
```

Both users now belonged to:

```text
appteam
```

### Important

The `-a` option in:

```bash
usermod -aG
```

is important.

It appends the supplementary group instead of replacing the user's existing supplementary groups.

---

# 4. Create the Shared Application Directory

Created:

```bash
mkdir -p /opt/myapp/shared
```

Created a test deployment file:

```bash
echo "version=1.0" > /opt/myapp/shared/app.version
```

---

# 5. Assign the Group Ownership

Changed the group ownership of the shared directory:

```bash
chown -R root:appteam /opt/myapp/shared
```

Verified:

```bash
ls -ld /opt/myapp/shared
ls -l /opt/myapp/shared/app.version
```

The group was now:

```text
appteam
```

---

# 6. Allow Group Access

Set the directory permissions:

```bash
chmod 770 /opt/myapp/shared
```

This gives:

```text
owner  → rwx
group  → rwx
others → ---
```

So users outside the group cannot access the directory.

---

# 7. Test Access Between Applications

As `app1`, created a deployment file:

```bash
su -s /bin/bash app1 -c "echo 'deployed by app1' > /opt/myapp/shared/deployment.txt"
```

Initially, the file looked like:

```text
-rw-rw-r-- 1 app1 app1 deployment.txt
```

This revealed an important issue.

Although `app2` could read the file, it was not necessarily doing so because of the `appteam` group. The file's group was still `app1`, and the `others` permission allowed reading.

This is an important troubleshooting lesson:

> A successful access test does not always prove that the intended permission mechanism is responsible.

---

# 8. Enable Setgid on the Shared Directory

Changed the directory permissions:

```bash
chmod 2770 /opt/myapp/shared
```

The leading `2` enables the **setgid** bit on the directory.

Verified:

```bash
ls -ld /opt/myapp/shared
```

The directory showed:

```text
drwxrws---
```

The `s` indicates the setgid bit.

With setgid enabled, newly created files inside the directory inherit the directory's group.

---

# 9. Recreate the Deployment File

Removed the previous file:

```bash
rm /opt/myapp/shared/deployment.txt
```

Created it again as `app1`:

```bash
su -s /bin/bash app1 -c "echo 'deployed by app1' > /opt/myapp/shared/deployment.txt"
```

Checked ownership:

```bash
ls -l /opt/myapp/shared/deployment.txt
```

The file now belonged to:

```text
app1 appteam
```

This confirmed that the directory's setgid behavior was working.

---

# 10. Verify app2 Access

Tested access as `app2`:

```bash
su -s /bin/bash app2 -c "cat /opt/myapp/shared/deployment.txt"
```

Result:

```text
deployed by app1
```

Therefore `app2` could access the file through the shared `appteam` group.

---

# 11. Enforce Least Privilege

The file initially had:

```text
-rw-rw-r--
```

The final `r--` meant users outside the owner/group could still read it.

We removed that access:

```bash
chmod 660 /opt/myapp/shared/deployment.txt
```

Final permissions:

```text
-rw-rw----
```

Meaning:

```text
owner  → read/write
group  → read/write
others → no access
```

---

# 12. Verify app2 Still Works

```bash
su -s /bin/bash app2 -c "cat /opt/myapp/shared/deployment.txt"
```

Result:

```text
deployed by app1
```

`app2` still had access because it belongs to `appteam`.

---

# 13. Verify an Unrelated User Is Denied

Created another user:

```bash
useradd outsider
```

Tested:

```bash
su -s /bin/bash outsider -c "cat /opt/myapp/shared/deployment.txt"
```

Result:

```text
Permission denied
```

This confirmed the intended access model.

---

# Final Access Model

```text
                 /opt/myapp/shared
                         |
                      appteam
                     /       \
                  app1       app2
                   |           |
                 access      access

                outsider
                    |
                 denied
```

---

# Important Commands

| Command        | Purpose                                |
| -------------- | -------------------------------------- |
| `useradd`      | Create a user                          |
| `groupadd`     | Create a group                         |
| `usermod -aG`  | Add a user to a supplementary group    |
| `id`           | Display user and group information     |
| `getent group` | Inspect group information              |
| `chown`        | Change ownership                       |
| `chmod`        | Change permissions                     |
| `su`           | Run a command as another user          |
| `ls -l`        | Inspect file permissions and ownership |

---

# `chmod` vs `chown`

These commands solve different problems.

### `chown`

Changes ownership:

```bash
chown app1:appteam deployment.txt
```

### `chmod`

Changes permissions:

```bash
chmod 660 deployment.txt
```

Think:

```text
chown → Who owns it?

chmod → What can they do?
```

---

# Troubleshooting Pattern

When a user receives:

```text
Permission denied
```

do not immediately change permissions.

First investigate:

```bash
id <user>
ls -ld <directory>
ls -l <file>
```

Then determine:

1. Which user is running the application?
2. Which groups does the user belong to?
3. Who owns the file?
4. Which group owns the file?
5. What permissions does the file have?
6. Can the user traverse the parent directories?
7. Is the intended group actually being used?

Then make the smallest appropriate change.

---

# Production Relevance

This pattern is common on Linux servers.

Examples include:

* Application deployment directories
* Shared application configuration
* Log directories
* Build artifacts
* Shared storage
* CI/CD deployment users
* Service accounts
* Application teams sharing resources

A production system should generally avoid giving broad permissions such as:

```bash
chmod 777
```

when a specific user/group permission model can solve the problem.

A better approach is:

```text
Users
   ↓
Groups
   ↓
Ownership
   ↓
Least-privilege permissions
   ↓
Application access
```

---

# Key Takeaways

1. Linux access control is based heavily on users, groups, ownership, and permissions.
2. Groups are useful when multiple users need the same access.
3. `usermod -aG` adds users to supplementary groups.
4. `chown` controls ownership.
5. `chmod` controls permissions.
6. A directory's setgid bit can make newly created files inherit the directory's group.
7. Successful access does not always prove the intended permission path is working.
8. Always inspect ownership and permissions when troubleshooting `Permission denied`.
9. Avoid overly broad permissions when group-based access can provide least privilege.

---

## Troubleshooting Principle

The main lesson from this lab:

```text
Permission denied
       ↓
Check the user
       ↓
Check group membership
       ↓
Check directory permissions
       ↓
Check file ownership
       ↓
Check file permissions
       ↓
Identify the actual access path
       ↓
Fix the smallest required problem
       ↓
Verify with the affected user
```

This is the same troubleshooting mindset we will continue using throughout the SRE/DevOps labs.
