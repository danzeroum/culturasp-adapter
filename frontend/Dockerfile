# Multi-stage: build the SPA with Node, then serve it with nginx. nginx also
# reverse-proxies the API, so the browser stays same-origin — no CORS and no
# API host baked into the bundle.
FROM node:22-alpine AS build
WORKDIR /app
# The bundle calls the API same-origin (/v1, /health, …); nginx proxies it.
ENV VITE_API_BASE=""
# @playwright/test is a devDependency used only by the E2E suite; don't pull a
# browser during the image build.
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
