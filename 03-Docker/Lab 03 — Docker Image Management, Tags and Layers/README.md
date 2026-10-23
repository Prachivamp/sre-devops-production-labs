# Lab 03 — Docker Image Management, Tags and Layers

## Objective

Understand Docker images, tags, image metadata, build history, architecture, and storage usage through hands-on exercises.

## 1. List local images

```bash
docker images
```

This displays locally available images and their tags, IDs, sizes, and usage information.

Examples observed in this environment:

- `nginx:alpine`
- `hashicorp/http-echo:1.0`
- `ubuntu:24.04`
- `mongo:latest`
- `postgres:16`

Docker Desktop may show disk usage and content size separately. These values are not necessarily interchangeable because images can share layers and storage is managed by Docker.

## 2. Inspect image metadata

```bash
docker image inspect nginx:alpine \
  --format 'ID={{.Id}} Tags={{json .RepoTags}} OS={{.Os}} Architecture={{.Architecture}} Created={{.Created}}'
```

Observed results:

- OS: `linux`
- Architecture: `arm64`
- Tag: `nginx:alpine`
- Image ID begins with `sha256:892bb2152464`

Image metadata helps identify the platform and image configuration. Architecture matters when deploying across ARM64 and AMD64 environments.

## 3. Create an additional image tag

```bash
docker image tag nginx:alpine nginx:lab03-test
docker images nginx
```

Both references displayed the same image ID:

`892bb2152464`

Verify using:

```bash
docker image inspect nginx:alpine nginx:lab03-test \
  --format '{{.RepoTags}} {{.Id}}'
```

Both references resolved to:

`sha256:892bb2152464f0c5d8972593a5f5afaf8054552580b699d95f8ff4af08c2d33d`

### Key takeaway

Tagging does not rebuild the image. It creates another reference to the same local image.

Tags are mutable references, so a tag name alone does not guarantee immutable image content. Production deployments may pin an image by digest for reproducibility.

## 4. Inspect image build history

```bash
docker history nginx:alpine
```

The history showed instructions and metadata associated with the image, including `RUN`, `COPY`, `ADD`, `ENV`, `EXPOSE`, `ENTRYPOINT`, and `CMD`.

| Instruction | Purpose |
|---|---|
| `RUN` | Executes commands while building the image |
| `COPY` | Copies files into the image |
| `ADD` | Adds files or archives and supports additional source handling |
| `ENV` | Defines environment variables |
| `EXPOSE` | Documents the intended container port |
| `ENTRYPOINT` | Defines the main executable or entrypoint |
| `CMD` | Supplies the default command or arguments |

Some history entries displayed `<missing>`. This is normal for many images and does not automatically indicate a broken image.

The sizes displayed by `docker history` represent history-layer contributions, not necessarily the total image size or unique disk usage.

## 5. Check image architecture

```bash
docker image inspect nginx:alpine \
  --format 'OS={{.Os}} Architecture={{.Architecture}} ID={{.Id}}'
```

Observed result:

- OS: `linux`
- Architecture: `arm64`

This matches the ARM64 Linux environment used by Docker Desktop on this Apple Silicon Mac.

When deploying to different CPU architectures, verify that the image supports the target platform. Multi-platform images can provide platform-specific variants.

## 6. Inspect Docker storage usage

```bash
docker system df
```

Observed snapshot:

| Resource | Total | Active | Reported size | Reclaimable |
|---|---:|---:|---:|---:|
| Images | 13 | 11 | 4.269 GB | 51.14 MB |
| Containers | 15 | 7 | 470 MB | 439 MB |
| Local volumes | 8 | 3 | 734.7 MB | 469.7 MB |
| Build cache | 25 | 0 | 549.2 MB | 16.26 MB |

These values are a snapshot and can change as containers, images, volumes, and build cache change.

### Important safety lesson

Reclaimable storage is not a recommendation to delete resources. Stopped containers may contain useful diagnostic evidence, and volumes may contain persistent application data.

Inspect resource ownership and dependencies before cleanup.

## 7. Production troubleshooting checklist

When an image-related issue occurs:

1. Check the image name and tag.
2. Inspect the image ID and platform.
3. Review image history when investigating build behaviour.
4. Verify compatibility with the target architecture.
5. Compare image size and storage usage.
6. Check whether a tag was updated or points to unexpected content.
7. Prefer pinned digests when immutable image identity is required.
8. Avoid deleting images, containers, or volumes without checking dependencies.

## Interview takeaways

- Images are templates; containers are running or stopped instances created from them.
- Tags are movable references, while image digests identify specific content.
- Image layers can be shared, reducing redundant storage and transfer.
- `docker history` helps investigate image build history.
- `EXPOSE` does not publish a port to the host.
- Architecture mismatches can prevent an image from running on the target platform.
- Docker's reclaimable storage estimate does not establish whether deleting a resource is safe.

## Completion checklist

- [x] Listed local images
- [x] Inspected image metadata
- [x] Created and verified an additional image tag
- [x] Reviewed image build history
- [x] Checked image architecture
- [x] Inspected Docker storage usage
- [x] Avoided deleting existing lab resources
