# Decision 038: Containerization Strategy

**Status:** Decided

**Category:** Stack Foundations

**Question:** Do we ship container images, and how are they built?

**Options considered:**
- Docker with a Dockerfile per app
- Platform-native builds
- Buildpacks

**Decision:** Docker. Each app has its own Dockerfile:
- `apps/api/Dockerfile` — Python 3.12 slim base, installs deps, copies app, runs Uvicorn.
- `apps/web/Dockerfile` — Multi-stage: Node to build, nginx to serve static assets.
- `docker-compose.yml` — dev topology (hot reload, bind mounts).
- `docker-compose.prod.yml` — production topology (built images, no bind mounts, nginx as public entry).

Images are built for `linux/arm64` (matching EC2 t4g.small) in CI via `docker buildx` with QEMU emulation. Images are pushed to Amazon ECR.

**Rationale:** Docker is required by the local-dev constraint and fits naturally with Compose on EC2. ARM64 targeting matters — building an amd64 image on CI and shipping it to a t4g instance either fails or runs under emulation. ECR keeps images in the same region as the host at no egress cost.
