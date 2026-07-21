# Container Security Hardening (Minimal)

## Purpose
Reduce what a container can do and what it contains, so that code execution inside it yields as little as possible.

## Core Techniques

### 1. Shrink the Image and Drop Root
```dockerfile
# ❌ Before — full OS, root, build tooling baked in
FROM python:3.12
COPY . /app
RUN pip install -r /app/requirements.txt
CMD ["python", "/app/main.py"]
```
```dockerfile
# ✅ After — multi-stage, non-root, minimal runtime
FROM python:3.12-slim AS build
WORKDIR /app
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin app
COPY --from=build /install /usr/local
COPY --chown=10001:10001 . /app
USER 10001
WORKDIR /app
CMD ["python", "main.py"]
```
The build stage keeps compilers, headers, and package caches out of the shipped image. A numeric `USER` matters: Kubernetes `runAsNonRoot` validates the numeric UID and cannot resolve a username at admission time.

### 2. Never Put Secrets in a Layer
```dockerfile
# ❌ The token is in the layer forever — ENV and later RUN rm do not remove it
ARG NPM_TOKEN
RUN echo "//registry.npmjs.org/:_authToken=$NPM_TOKEN" > .npmrc && npm ci

# ✅ BuildKit secret mount — never written to any layer
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci
```
Build with `docker build --secret id=npmrc,src=$HOME/.npmrc .`, and audit what actually shipped with `docker history --no-trunc myapp:1.4.2`.

### 3. Pin Base Images by Digest
`FROM python:3.12-slim` resolves to a different image over time; `FROM node:latest` is unreproducible by construction. You cannot say what shipped, cannot reproduce a build, and a rollback may not restore the bits you had.

```dockerfile
FROM python:3.12-slim@sha256:<digest>   # immutable; renovate bots can bump it
```

### 4. Constrain the Runtime
```yaml
securityContext:                 # pod level
  runAsNonRoot: true
  runAsUser: 10001
  fsGroup: 10001
  seccompProfile: {type: RuntimeDefault}
containers:
  - name: api
    image: registry.example.com/api@sha256:<digest>
    securityContext:             # container level
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities: {drop: ["ALL"]}
    volumeMounts:
      - {name: tmp, mountPath: /tmp}
volumes:
  - name: tmp
    emptyDir: {}
```
`allowPrivilegeEscalation: false` sets `no_new_privs`, blocking setuid binaries from gaining privilege. `drop: ["ALL"]` removes even the default set — most apps need none; a listener on a port below 1024 needs `NET_BIND_SERVICE`, or better, just listen on 8080.

### 5. Scan in CI and Again on a Schedule
```bash
trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 myapp:$SHA
```
Gate the build on reachable Critical/High, and re-scan running images nightly — a CVE published after your last deploy is invisible to a build-time-only scan. Triage the output with the vulnerability-assessment skill; do not fail builds on unfixable findings.

## Warning Signs

- No `USER` in the Dockerfile, or a username instead of a numeric UID
- `FROM ...:latest` or any unpinned tag in a production image
- `docker history` shows tokens, `.git`, `.env`, or SSH keys in a layer
- Containers running with `privileged: true` or the default capability set
- `readOnlyRootFilesystem` unset, so an attacker can drop a binary anywhere
- Compilers, `curl`, and a package manager present in the runtime image
- Secrets injected as env vars readable via `/proc/1/environ` or a crash dump
- Namespaces without a Pod Security Admission label, so anything can be scheduled
- Image scanning only at build time, never against what is actually running
