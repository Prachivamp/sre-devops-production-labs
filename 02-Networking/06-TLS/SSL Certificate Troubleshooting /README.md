# Lab 06: TLS and SSL Certificate Troubleshooting

## 1. Objective

Learn how TLS establishes secure connections and how to troubleshoot common HTTPS certificate failures using OpenSSL.

This lab covers:

- Inspecting server certificates
- Verifying a TLS handshake and certificate chain
- Identifying expired certificates
- Detecting hostname mismatches
- Applying a systematic TLS troubleshooting workflow

## 2. Environment and Tools

- Operating system: Ubuntu 24.04 inside Docker
- Client tools: OpenSSL
- Test endpoints: Google and BadSSL
- HTTPS port: TCP 443

Check the OpenSSL version:

```bash
openssl version
```

## 3. Lab 1 — Inspect a TLS Certificate

### Command

```bash
openssl s_client -connect google.com:443 -servername google.com </dev/null 2>/dev/null | openssl x509 -noout -subject -issuer -dates
```

### Observed output

```text
subject=CN = *.google.com
issuer=C = US, O = Google Trust Services, CN = WE2
notBefore=Sep 28 18:38:33 2026 GMT
notAfter=Dec 21 18:38:32 2026 GMT
```

### Explanation

- **Subject:** Identifies the certificate's subject. Here, the certificate uses the wildcard name `*.google.com`.
- **Issuer:** Identifies the certificate authority that issued the certificate.
- **notBefore:** The beginning of the certificate's validity period.
- **notAfter:** The expiration date and time.
- **SNI:** The `-servername` option sends the requested hostname during the TLS handshake so the server can select the appropriate certificate.

### Production relevance

When investigating HTTPS failures, inspect the certificate's validity dates, issuer, subject, and hostname coverage. A certificate can be expired, not yet valid, untrusted, or issued for the wrong hostname.

## 4. Lab 2 — Verify a Successful TLS Handshake

### Command

```bash
openssl s_client -connect google.com:443 -servername google.com -verify_return_error </dev/null
```

### Important observed output

```text
Verification: OK
New, TLSv1.3, Cipher is TLS_AES_256_GCM_SHA384
Verify return code: 0 (ok)
DONE
```

### Explanation

- `CONNECTED`: The connection to the server was established.
- `Verification: OK`: Certificate verification succeeded.
- `TLSv1.3`: The negotiated TLS protocol version.
- `TLS_AES_256_GCM_SHA384`: The negotiated cipher suite.
- `Verify return code: 0 (ok)`: The certificate verification completed successfully.

The certificate chain contained the server certificate and intermediate certificates leading to a trusted root.

### Production relevance

A successful TCP connection does not guarantee a successful TLS handshake. The client and server must also agree on TLS parameters, and the certificate must pass the client's validation checks.

## 5. Lab 3 — Troubleshoot an Expired Certificate

### Command

```bash
openssl s_client -connect expired.badssl.com:443 -servername expired.badssl.com -verify_return_error </dev/null
```

### Observed error

```text
verify error:num=10:certificate has expired
Verification error: certificate has expired
```

The output also showed:

```text
notAfter=Apr 12 23:59:59 2015 GMT
```

### Root cause

The server presented a certificate that had expired. Because `-verify_return_error` was enabled, OpenSSL aborted the handshake when certificate verification failed.

### Troubleshooting steps

1. Inspect the certificate expiration date.
2. Check the certificate renewal process.
3. Verify that the renewed certificate was deployed to the correct server or load balancer.
4. Check whether all replicas or endpoints are serving the updated certificate.
5. Review certificate monitoring and renewal logs.

**Security note:** Do not disable certificate verification as a production workaround.

## 6. Lab 4 — Troubleshoot a Hostname Mismatch

### Command

```bash
openssl s_client -connect wrong.host.badssl.com:443 -servername wrong.host.badssl.com -verify_hostname wrong.host.badssl.com -verify_return_error </dev/null
```

### Observed error

```text
verify error:num=62:hostname mismatch
Verification error: hostname mismatch
```

The certificate subject shown in the output was:

```text
CN = *.badssl.com
```

### Root cause

The certificate presented by the server did not match the hostname the client was instructed to verify.

The `-verify_hostname` option explicitly checks whether the certificate is valid for the requested hostname.

### Troubleshooting steps

1. Confirm the hostname the client is requesting.
2. Inspect the certificate's Subject Alternative Name (SAN) entries.
3. Verify the hostname against the certificate's SAN entries.
4. Check SNI and virtual-host configuration.
5. If a load balancer or reverse proxy terminates TLS, verify the certificate configured on that endpoint.

**Important:** Modern hostname verification relies on Subject Alternative Name (SAN) entries. Do not rely on the Common Name alone when validating certificates.

## 7. Understanding the TLS Handshake

A simplified HTTPS connection follows this sequence:

1. The client resolves the hostname through DNS.
2. The client establishes a TCP connection to port 443.
3. The client and server negotiate TLS parameters.
4. The server presents its certificate chain.
5. The client validates the certificate chain, validity period, and hostname.
6. The handshake completes and secure communication begins.
7. HTTP requests and responses travel through the encrypted connection.

A failure at the certificate-validation stage can prevent the application request from proceeding, even when DNS and TCP connectivity are working.

## 8. Common TLS Errors

| Error or symptom | What to investigate |
|---|---|
| Certificate has expired | Certificate validity dates and renewal/deployment |
| Certificate is not yet valid | Validity dates and system clock |
| Hostname mismatch | Requested hostname, SAN entries, and SNI |
| Unable to get local issuer certificate | Missing intermediate certificates or trust-store configuration |
| Self-signed certificate error | Certificate trust and internal CA configuration |
| TLS handshake failure | Protocol versions, cipher compatibility, certificate configuration, and server logs |
| Connection timeout | Routing, firewall rules, server reachability, or overloaded endpoints |

These symptoms indicate where to investigate; confirm the root cause using evidence from the client, server, and network.

## 9. Production TLS Troubleshooting Workflow

When an application reports an HTTPS or certificate error:

1. **DNS:** Confirm the hostname resolves to the expected endpoint.
2. **TCP:** Check connectivity to port 443.
3. **TLS:** Inspect the handshake and certificate-validation errors.
4. **Certificate:** Check expiration, SAN, issuer, trust chain, and system time.
5. **Endpoint:** Check certificates on the load balancer, reverse proxy, and application servers.
6. **Recent changes:** Review certificate renewals, deployments, DNS changes, and TLS configuration changes.
7. **Monitoring:** Correlate the failure with certificate-expiration alerts, request errors, and affected endpoints.

Useful diagnostic commands:

```bash
# Inspect certificate details
openssl s_client -connect example.com:443 -servername example.com </dev/null 2>/dev/null | openssl x509 -noout -subject -issuer -dates

# Verify a TLS connection and certificate chain
openssl s_client -connect example.com:443 -servername example.com -verify_return_error </dev/null

# Verify the hostname explicitly
openssl s_client -connect example.com:443 -servername example.com -verify_hostname example.com -verify_return_error </dev/null

# Test HTTPS and inspect the HTTP response
curl -v --max-time 10 https://example.com/
```

Replace `example.com` with the hostname being investigated.

## 10. Important Observation About OpenSSL Output

During the two intentionally failed tests, the output contained explicit verification errors but also showed a final line saying `Verify return code: 0 (ok)`.

For those failed sessions, the explicit errors were:

- `certificate has expired`
- `hostname mismatch`

Do not conclude that verification succeeded solely from the final summary line when other output indicates a failed handshake. Use `-verify_return_error`, inspect the verification error, and corroborate the result with the handshake outcome.

## 11. Key Learnings

- TLS provides encryption and server authentication for HTTPS.
- TCP connectivity and TLS success are separate checks.
- Certificates have validity periods and hostname requirements.
- Certificate chains must lead to a trusted certificate authority.
- SNI helps a server select the appropriate certificate.
- `openssl s_client` is useful for examining TLS connections and certificate errors.
- Certificate renewal and deployment should be monitored to prevent production outages.
- Never bypass certificate validation as a permanent production fix.

## 12. Lab Completion Checklist

- [x] Inspected a real HTTPS certificate.
- [x] Verified a successful TLS 1.3 handshake.
- [x] Reproduced an expired-certificate error.
- [x] Reproduced a hostname-mismatch error.
- [x] Documented the production troubleshooting workflow.

**Status:** Hands-on tests completed.

**Next lab:** Lab 07 — Linux Firewall and Access Rules.
