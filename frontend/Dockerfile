# PolyChat Frontend Dockerfile
# Multi-stage build: Node (build) -> Nginx (serve)

# ── Build stage ───────────────────────────────────────────────────────────────
FROM node:20-alpine AS build
WORKDIR /app

# Install dependencies first (better layer caching)
COPY package.json package-lock.json* ./
RUN npm install

# Copy source and build
COPY . .
# Setting VITE_API_BASE_URL to relative /api/v1 so Nginx can proxy it correctly
ENV VITE_API_BASE_URL=/api/v1
RUN npm run build

# ── Production stage ──────────────────────────────────────────────────────────
FROM nginx:alpine AS production

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/

# Copy built assets from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
