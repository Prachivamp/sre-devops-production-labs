# Linux Lab 02 — Files, Directories & Searching

## Objective

Learn how to create, copy, move, remove, inspect, and locate files and directories in Linux.

The lab focuses on a common production troubleshooting scenario: an application cannot find its configuration file.

## Environment

* Host: macOS
* Linux environment: Ubuntu 24.04
* Runtime: Docker
* Repository: `sre-devops-production-labs`

## Commands Practiced

```bash
touch
cp
mv
rm
find
cat
head
tail
ls
```

## Application Structure

Created an example application structure:

```text
/opt/myapp/
├── backup/
├── config/
│   └── app.conf
└── logs/
```

Created the configuration file:

```bash
touch /opt/myapp/config/app.conf
```

Added configuration:

```text
DATABASE_HOST=db.internal
DATABASE_PORT=5432
APP_ENV=production
```

## File Operations

### `touch`

Creates an empty file when the file does not already exist.

```bash
touch /opt/myapp/config/app.conf
```

### `cp`

Copies a file while keeping the original.

```bash
cp /opt/myapp/config/app.conf /opt/myapp/backup/app.conf
```

### `mv`

Moves or renames a file.

```bash
mv /opt/myapp/config/app.conf /opt/myapp/backup/app.conf
```

### `find`

Searches for files and directories.

```bash
find /opt/myapp -name "app.conf"
```

Example result:

```text
/opt/myapp/backup/app.conf
```

### `head`

Displays the beginning of a file.

```bash
head -n 2 /opt/myapp/config/app.conf
```

### `tail`

Displays the end of a file.

```bash
tail -n 2 /opt/myapp/config/app.conf
```

### `cat`

Displays the contents of a file.

```bash
cat /opt/myapp/config/app.conf
```

## Troubleshooting Scenario

### Problem

The application reports that its configuration file cannot be found.

The application expects:

```text
/opt/myapp/config/app.conf
```

### Investigation

The expected directory was checked:

```bash
ls -la /opt/myapp/config
```

The configuration file was missing.

Instead of assuming that the file was deleted, the filesystem was searched:

```bash
find /opt/myapp -name "app.conf"
```

The file was found at:

```text
/opt/myapp/backup/app.conf
```

### Finding

The configuration file had been moved from the expected location into the backup directory.

The file was restored:

```bash
mv /opt/myapp/backup/app.conf /opt/myapp/config/app.conf
```

The configuration was then verified with:

```bash
cat /opt/myapp/config/app.conf
```

## Configuration Change Investigation

A configuration change was deliberately introduced:

```text
DATABASE_PORT=3306
```

`tail` was used to inspect the end of the configuration file:

```bash
tail -n 2 /opt/myapp/config/app.conf
```

The active configuration was compared with the backup copy.

This demonstrated a simple but useful troubleshooting technique: compare a potentially modified file with a known-good copy.

The known-good configuration was restored:

```bash
cp /opt/myapp/backup/app.conf /opt/myapp/config/app.conf
```

## Production Relevance

File and directory operations are fundamental to Linux administration and SRE work.

During incidents, engineers commonly need to:

* Locate missing configuration files
* Find application files
* Create backups before making changes
* Move or restore files
* Inspect large files
* Check the beginning or end of logs
* Search a directory tree

A common troubleshooting mistake is assuming that a missing file was deleted. The file may instead have been moved, renamed, or placed in another directory.

## Troubleshooting Pattern

```text
Problem
   ↓
Check expected location
   ↓
File is missing
   ↓
Search filesystem with find
   ↓
Locate file
   ↓
Inspect file
   ↓
Restore or correct location
   ↓
Verify
```

## Key Takeaways

* `touch` creates files.
* `cp` copies files.
* `mv` moves or renames files.
* `find` searches for files and directories.
* `cat` displays file contents.
* `head` shows the beginning of a file.
* `tail` shows the end of a file.
* Always investigate before assuming a file was deleted.
* Backups can provide a known-good version for comparison or recovery.

## Production Mindset

The important lesson from this lab is not memorizing commands.

The troubleshooting approach is:

```text
Observe → Search → Inspect → Compare → Fix → Verify
```

This same approach will be used throughout the SRE/DevOps labs.
