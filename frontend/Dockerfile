## Multi-stage Dockerfile to build and run TanStack Start (SSR + client) on Node 24-alpine

# --- Build stage ---
FROM node:24-alpine AS builder
WORKDIR /app

# Install dependencies with caching
COPY package*.json ./
RUN npm ci --no-audit --no-fund || npm install --no-audit --no-fund

# Copy source and build
COPY . .
RUN npm run build

# --- Production runtime stage ---
FROM node:24-alpine AS prod
ENV NODE_ENV=production
WORKDIR /app

# Copy package files and install production dependencies only
COPY package*.json ./
RUN npm ci --omit=dev --no-audit --no-fund || npm install --omit=dev --no-audit --no-fund

# Copy the built output from builder
COPY --from=builder /app/dist ./dist

# Start the SSR server (serves both server and client bundles)
EXPOSE 3000
CMD ["node", "dist/server/server.js"]

# Keep alias for backward compatibility
FROM prod AS runner

# --- Development stage ---
FROM node:24-alpine AS dev
ENV NODE_ENV=development
WORKDIR /app
COPY package*.json ./
RUN npm ci --no-audit --no-fund || npm install --no-audit --no-fund
COPY . .
EXPOSE 3000 9229
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

