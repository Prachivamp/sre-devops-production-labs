# Linux Lab 18: Archives and Backups

## Objective

Learn to create, inspect, validate, and restore compressed backups of application configuration and logs.

## Production scenario

Before a deployment or configuration change, an engineer needs a backup that can be verified and restored if the change causes a problem.

## Environment

* Ubuntu 24.04 running in Docker
* GNU tar 1.35
* gzip compression
* Application configuration under `/opt/myapp/config`
* Logs under `/opt/myapp/logs`

## 1. Create a backup

```bash
mkdir -p /opt/myapp/backups

tar -czvf /opt/myapp/backups/myapp-backup.tar.gz \
  -C /opt/myapp config logs
```

The archive includes the application configuration and logs.

## 2. Inspect and validate the archive

List its contents:

```bash
tar -tzvf /opt/myapp/backups/myapp-backup.tar.gz
```

Check the archive size:

```bash
ls -lh /opt/myapp/backups/myapp-backup.tar.gz
```

Test gzip integrity:

```bash
gzip -t /opt/myapp/backups/myapp-backup.tar.gz
echo $?
```

An exit code of `0` indicates that the gzip integrity test succeeded.

## 3. Simulate a bad configuration change

Save a copy of the original configuration:

```bash
cp /opt/myapp/config/app.conf /tmp/app.conf.before
```

Introduce an incorrect port:

```bash
echo "DATABASE_PORT=9999" >> /opt/myapp/config/app.conf
```

Inspect the changed file:

```bash
cat /opt/myapp/config/app.conf
```

## 4. Preview and restore the backup

Preview the archived configuration without extracting it:

```bash
tar -xOf /opt/myapp/backups/myapp-backup.tar.gz config/app.conf
```

Restore the original file:

```bash
tar -xzvf /opt/myapp/backups/myapp-backup.tar.gz \
  -C /opt/myapp config/app.conf
```

Verify the contents:

```bash
cat /opt/myapp/config/app.conf
```

Compare the restored file against the saved copy:

```bash
diff -u /tmp/app.conf.before /opt/myapp/config/app.conf
```

No output from `diff` means the file contents match.

## 5. Verify metadata

```bash
ls -l /opt/myapp/config/app.conf
```

The restored file retained `appuser:appuser` ownership and `640` permissions in this lab.

When restoring in production, verify ownership, permissions, access controls, and application functionality. Metadata restoration can depend on extraction options and privileges.

## Commands learned

* `tar -czvf`: create a gzip-compressed archive
* `tar -tzvf`: inspect archive contents
* `tar -xOf`: preview a file inside an archive
* `tar -xzvf`: extract archived files
* `gzip -t`: test gzip integrity
* `diff -u`: compare file contents
* `ls -lh`: inspect file size
* `ls -l`: inspect ownership and permissions

## Production relevance

Backups support recovery from failed deployments, accidental configuration changes, and data loss. A backup should be verified, stored securely, and tested through actual restoration.

For important production data, use off-host or remote storage, retention policies, access controls, and periodic restore drills. A backup stored only on the same host may be lost with that host.

## Troubleshooting workflow

**Back up → Inspect → Validate → Change → Restore → Compare → Verify**

## Key takeaway

A backup is useful only when it can be recovered. Creating an archive is the beginning; validating and restoring it proves that the recovery process works.
