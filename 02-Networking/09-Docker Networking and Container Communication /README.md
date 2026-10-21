# Lab 09: Docker Networking and Container Communication

## Objective

Understand how Docker containers communicate with each other, compare the default bridge network with a user-defined bridge network, and troubleshoot connectivity using container IP addresses and DNS names.

## Environment

- Host: macOS
- Main container: `sre-linux-lab` (Ubuntu)
- Test container: `lab09-web` (`nginx:alpine`)
- Docker network: `lab09-network`
- Tools: Docker CLI and `curl`

## 1. Inspect Existing Docker Networks

```bash
docker network ls
```

Docker showed several networks, including `bridge`, `host`, and `none`, along with application-specific networks.

**Key observation:** Docker networks isolate and connect containers according to their network configuration.

## 2. Inspect the Main Container

```bash
docker inspect sre-linux-lab --format '{{json .NetworkSettings.Networks}}'
```

Initially, the main container was connected to the default bridge network:

- Container IP: `172.17.0.2`
- Gateway: `172.17.0.1`

## 3. Start an Nginx Test Container

```bash
docker run -d --name lab09-web nginx:alpine
```

Inspect its network configuration:

```bash
docker inspect lab09-web --format '{{json .NetworkSettings.Networks}}'
```

Initially, Nginx was connected to the default bridge network with IP `172.17.0.3`.

## 4. Test Communication by IP Address

From the main container, run this command on the Mac terminal:

```bash
docker exec sre-linux-lab curl -I --max-time 5 http://172.17.0.3
```

**Result:** `HTTP/1.1 200 OK`

The main container could reach Nginx using its IP address.

## 5. Test Communication by Container Name on the Default Bridge

```bash
docker exec sre-linux-lab curl -I --connect-timeout 3 --max-time 5 http://lab09-web
```

**Result:** Name resolution timed out.

On Docker's default bridge network, automatic container-name resolution is not provided in the same way as on user-defined bridge networks. Therefore, IP-based connectivity can work even when name-based connectivity does not.

## 6. Create a User-Defined Bridge Network

```bash
docker network create lab09-network
```

Connect both containers:

```bash
docker network connect lab09-network sre-linux-lab
docker network connect lab09-network lab09-web
```

A repeated connection attempt for `sre-linux-lab` returned an endpoint-already-exists error because the container was already connected. This was harmless.

## 7. Inspect the New Network

```bash
docker network inspect lab09-network
```

Observed configuration:

| Property | Value |
|---|---|
| Driver | `bridge` |
| Subnet | `172.22.0.0/16` |
| Gateway | `172.22.0.1` |
| `sre-linux-lab` IP | `172.22.0.2` |
| `lab09-web` IP | `172.22.0.3` |

Both containers were connected to `lab09-network`.

**Important:** Containers can be attached to multiple networks and have a separate IP address on each network.

## 8. Test Communication by Container Name

Run:

```bash
docker exec sre-linux-lab curl -I --connect-timeout 3 --max-time 5 http://lab09-web
```

**Result:** `HTTP/1.1 200 OK`

Then retrieve the response body:

```bash
docker exec sre-linux-lab curl -sS --max-time 5 http://lab09-web/
```

**Result:** The default Nginx welcome page was returned successfully.

This confirms that the main container can resolve `lab09-web` and communicate with it over the user-defined bridge network.

## What I Learned

- Docker bridge networks allow containers to communicate over virtual networking.
- Containers on the default bridge can communicate by IP when connectivity permits, but automatic name resolution differs from that of user-defined bridge networks.
- User-defined bridge networks provide Docker-managed DNS resolution for container names and network aliases.
- Containers attached to the same user-defined network can generally communicate directly without publishing their ports to the host.
- Containers attached to multiple networks have a separate network address for each network.
- Container IP addresses can change, so service or container names are generally preferable for communication within a user-defined network.

## Production Troubleshooting Workflow

When one container cannot reach another:

1. **Check network membership**
   ```bash
   docker network ls
   docker network inspect lab09-network
   ```

2. **Inspect the container's network configuration**
   ```bash
   docker inspect sre-linux-lab --format '{{json .NetworkSettings.Networks}}'
   ```

3. **Test DNS/name resolution and connectivity**
   ```bash
   docker exec sre-linux-lab curl -v --connect-timeout 3 --max-time 5 http://lab09-web/
   ```

4. **Check whether the destination service is listening** and verify its port and application logs.

5. **Distinguish DNS failures from connection failures.** A name-resolution timeout differs from a TCP connection refusal or an HTTP error.

6. **Check port publishing only when host-to-container access is required.** Containers on the same suitable Docker network do not normally need host port publishing to communicate with one another.

## Conclusion

I compared container-to-container communication on Docker's default bridge and a user-defined bridge network. IP-based communication worked on the default bridge, while name-based communication succeeded after both containers joined `lab09-network`. This demonstrated Docker network inspection, DNS-based service discovery, and a practical connectivity troubleshooting workflow.