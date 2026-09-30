# ---- build: Vite menghasilkan file statis di /app/dist ----
FROM node:22-alpine AS build
WORKDIR /app

COPY package.json package-lock.json* ./
# npm ci kalau package-lock.json sudah di-commit (disarankan: hasil build konsisten), npm install kalau belum.
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

COPY . .
# Tertanam saat build. Default "/api/v1" = alamat relatif ke domain yang sama; nginx di bawah
# meneruskannya ke backend, jadi image tidak perlu dibuild ulang kalau domain berubah.
ARG VITE_API_URL=/api/v1
ENV VITE_API_URL=$VITE_API_URL
# npm run build = vue-tsc (cek tipe) + vite build. Error tipe = build image gagal.
RUN npm run build

# ---- runtime: nginx menyajikan SPA + proxy /api ke backend ----
FROM nginx:stable-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD wget -qO /dev/null http://127.0.0.1/healthz || exit 1
