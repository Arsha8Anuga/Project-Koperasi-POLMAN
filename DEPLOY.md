# Deploy ke Portainer (Docker)

Satu stack berisi 4 container (backend, AI engine, kasir, admin). MongoDB **tidak** ikut stack; backend memakai server Mongo yang sudah ada (zenahost) lewat `MONGODB_URI`.

```text
 pengguna ──HTTPS──► reverse proxy (NPM / Traefik / Caddy)
                        │ kasir.<domain>  → host:8081
                        │ admin.<domain>  → host:8082
                        ▼
             ┌──────── stack "koperasi" ────────┐
             │ kasir  (nginx :80)  ─┐            │
             │ admin  (nginx :80)  ─┼─ /api/ ──► backend (uvicorn :8000, tidak di-publish)
             │ ai-engine (worker, tanpa port)    │        │
             └──────────────────────┴────────────┘        │
                      │ baca transaksi, tulis insights    │
                      ▼                                   ▼
                  MongoDB replica set (db-proj-aec3.zenahost.my.id:40008)
```

- Frontend memanggil API di **domain yang sama** (`/api/v1`). Nginx di container kasir/admin meneruskannya ke `backend:8000`. Hasilnya: tidak perlu CORS, dan image frontend tidak perlu dibuild ulang kalau domain berganti.
- Port 8000 backend tidak dibuka ke luar. Swagger (`/docs`) juga tidak bisa diakses dari internet; itu disengaja.
- Rahasia (`MONGODB_URI`, `JWT_SECRET`) hanya diisi di Portainer, tidak ada di repo maupun di image.
- Foto produk yang diunggah disimpan di **named volume `media`** (Portainer → Volumes → `koperasi_media`), dibuat otomatis saat deploy. Jangan dihapus saat membersihkan stack, dan ikut di-backup bersama database.

## File yang terlibat

| File | Isi |
|---|---|
| `docker-compose.yml` | Definisi stack (dibaca Portainer dari repo) |
| `stack.env.example` | Daftar environment variable yang harus diisi di Portainer |
| `backend/Dockerfile` | Python 3.11 slim, dependensi dari `requirements.txt` (tanpa pytest/ruff), user non-root, healthcheck `/health` |
| `frontend-*/Dockerfile` | Build Vite di Node 22 (`npm run build` = vue-tsc + vite), hasilnya disajikan `nginx:stable-alpine` |
| `ai-engine/Dockerfile` | Worker Python 3.11 + numpy + pymongo; healthcheck = denyut di `ai_engine_status` |
| `frontend-*/nginx.conf` | SPA fallback, proxy `/api/` → backend, cache aset, header keamanan (**identik** di kedua app) |

## 1. Sebelum deploy (di laptop)

1. `npm install` lalu `npm run build` di `frontend-kasir` dan `frontend-admin` harus lolos. Build di Docker menjalankan perintah yang sama, jadi kalau di laptop gagal, di Portainer juga gagal.
2. **Commit `package-lock.json`** kedua frontend. Dengan lock file, Docker memakai `npm ci` sehingga versi paket di server sama persis dengan di laptop.
3. Push ke branch yang akan di-deploy (misalnya `main`).
4. Pastikan server Portainer bisa menjangkau MongoDB zenahost (port 40008 tidak diblokir firewall untuk IP server Portainer). Cek dari server:
   ```bash
   docker run --rm mongo:7 mongosh "<MONGODB_URI>" --eval 'db.adminCommand({ping:1}); rs.status().ok'
   ```
   Keduanya harus `1`.

## 2. Buat stack di Portainer

**Stacks → Add stack**

| Isian | Nilai |
|---|---|
| Name | `koperasi` |
| Build method | **Repository** |
| Repository URL | URL repo GitHub (mis. `https://github.com/<org>/KOPMAN`) |
| Repository reference | `refs/heads/main` |
| Compose path | `docker-compose.yml` |
| Authentication | Aktifkan kalau repo **private**: username GitHub + *Personal Access Token* (scope `repo` / read-only contents) |
| Environment variables | Klik **Advanced mode**, tempel isi `stack.env.example` yang sudah diisi nilai asli |

Lalu **Deploy the stack**. Build pertama agak lama (install npm + vue-tsc) — normal 3–8 menit. Server dengan RAM < 2 GB bisa kehabisan memori saat build Vite; kalau build mati tanpa pesan jelas, itu penyebabnya.

Setelah jalan, di **Containers** keempatnya harus berstatus *healthy*. `ai-engine` butuh ±1 menit sebelum healthy (menunggu denyut pertama). `backend` *unhealthy* hampir selalu berarti Mongo tidak terjangkau atau `MONGODB_URI` salah (cek **Logs** container backend).

## 3. Domain & HTTPS (reverse proxy)

Arahkan DNS `kasir.<domain>` dan `admin.<domain>` (A record) ke IP server, lalu di reverse proxy:

**Nginx Proxy Manager** — *Proxy Hosts → Add*:

| Domain | Forward | Opsi |
|---|---|---|
| `kasir.<domain>` | `http` · `<ip-server>` · `8081` | SSL: Request new certificate, Force SSL, HTTP/2 |
| `admin.<domain>` | `http` · `<ip-server>` · `8082` | sama |

Kalau NPM berjalan sebagai container di **server yang sama**, boleh juga memasukkan NPM ke network stack (`koperasi_default`) dan forward ke `kasir:80` / `admin:80`; dengan begitu `ports` di compose bisa dihapus agar aplikasi hanya bisa dibuka lewat HTTPS.

**Traefik** (kalau yang dipakai Traefik): hapus `ports`, tambahkan label di service `kasir`/`admin`, misalnya:
```yaml
    labels:
      - traefik.enable=true
      - traefik.http.routers.kasir.rule=Host(`kasir.<domain>`)
      - traefik.http.routers.kasir.entrypoints=websecure
      - traefik.http.routers.kasir.tls.certresolver=letsencrypt
      - traefik.http.services.kasir.loadbalancer.server.port=80
```
dan pasang service ke network milik Traefik.

## 4. Isi data (sekali)

Portainer → **Containers → koperasi-backend-1 → Console → Connect** (`/bin/sh`), lalu:

```bash
python -m scripts.seed --reset --yes      # data demo ke MONGODB_DB (default koperasi_demo)
# atau hanya akun awal tanpa data demo:
python -m scripts.create_initial_users
```

Akun: `owner`, `logistik`, `admin`, `kasir1`, `kasir2` — password `koperasi123`. **Ganti password** lewat menu Pengguna kalau URL-nya dibagikan ke luar tim.

Seed otomatis mengantrekan perhitungan AI; dalam ±10 detik engine memprosesnya (lihat menu **Admin → AI Engine** atau Logs container `ai-engine`). Tanpa seed, engine menghitung sendiri tiap 15 menit.

Cek: buka `https://kasir.<domain>` → login `kasir1`; buka `https://admin.<domain>` → login `owner` → menu Laporan menampilkan chart.

## 5. Update setelah ada commit baru

Push ke `main` → Portainer → stack `koperasi` → **Pull and redeploy** (centang opsi re-pull/re-build bila ada). Opsional: aktifkan **GitOps updates** (polling) di pengaturan stack supaya redeploy otomatis setiap ada commit.

`JWT_SECRET` jangan diganti-ganti: mengganti nilainya membuat semua orang yang sedang login langsung keluar.

## Troubleshooting

| Gejala | Penyebab umum |
|---|---|
| Build gagal di tahap `npm run build` | Error TypeScript/vue-tsc — jalankan `npm run build` di laptop dan perbaiki dulu |
| Build gagal `npm ci` | `package-lock.json` tidak cocok dengan `package.json` — jalankan `npm install` di laptop, commit lock file |
| Halaman terbuka, login → "Terjadi kesalahan jaringan" / 502 | Container backend mati/unhealthy → lihat Logs backend |
| Backend log `ServerSelectionTimeoutError` / `not primary` | Mongo tidak terjangkau dari server, URI salah, atau password belum di-URL-encode (`+` → `%2B`) |
| Backend log `jwt_secret  String should have at least 32 characters` | `JWT_SECRET` terlalu pendek |
| Refresh di halaman selain `/` → 404 | `nginx.conf` tidak ter-copy (cek `try_files ... /index.html`) |
| Saran "sering dibeli bersama" / prediksi stok kosong | Engine belum pernah menghitung: cek status di Admin → AI Engine; engine *offline* → lihat Logs `ai-engine` (biasanya `MONGODB_URI`/`MONGODB_DB` beda dengan backend) |
| IP di audit trail selalu IP proxy | Reverse proxy tidak mengirim `X-Forwarded-For` (NPM sudah mengirim secara default) |
