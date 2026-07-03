FROM node:20-alpine

WORKDIR /app
RUN corepack enable

COPY apps/web/package.json ./package.json
RUN pnpm install --no-frozen-lockfile

COPY apps/web ./

EXPOSE 3000
CMD ["pnpm", "dev"]
