# Production images are built linux/arm64 by deploy.yml (buildx --platform, ADR 038);
# no platform pin here so CI runners and local hosts build their native arch.
#
# pnpm is installed directly (not via corepack): the corepack bundled with this
# node image verifies registry signatures against npm's rotated (stale) keys and
# fails closed, so `corepack enable` cannot download pnpm in a fresh build.
FROM node:20.17-alpine AS deps
WORKDIR /app
# Husky's `prepare` hook has no .git to install into inside the image.
ENV HUSKY=0
RUN npm install -g pnpm@9.12.0
# Every workspace member's manifest must be present for a frozen install —
# the lockfile records all importers (apps/web, packages/*, e2e).
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY apps/web/package.json apps/web/
COPY packages/api-types/package.json packages/api-types/
COPY packages/config/package.json packages/config/
COPY e2e/package.json e2e/
RUN pnpm install --frozen-lockfile

FROM node:20.17-alpine AS build
WORKDIR /app
ENV HUSKY=0
RUN npm install -g pnpm@9.12.0
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/apps/web/node_modules ./apps/web/node_modules
COPY --from=deps /app/packages ./packages
COPY --from=deps /app/e2e ./e2e
COPY . .
RUN pnpm --filter @taskflow/web build

FROM nginx:1.27-alpine AS runtime
COPY --from=build /app/apps/web/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
