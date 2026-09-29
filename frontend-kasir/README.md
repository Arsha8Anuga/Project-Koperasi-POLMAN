# frontend-kasir — Aplikasi Kasir (POS)

Vue 3 + TypeScript + Vite + Pinia + Tailwind v4 + shadcn-vue. Dipakai role **KASIR**.

## Menjalankan

```bash
npm install
cp .env.example .env.local        # VITE_API_URL=http://localhost:8000/api/v1
npm run dev                       # http://localhost:5173
npm run build                     # vue-tsc (cek tipe) + vite build — WAJIB lolos sebelum PR
```

## UI: shadcn-vue

Komponen dasar diambil dari [shadcn-vue](https://www.shadcn-vue.com) (gaya *new-york*, berbasis reka-ui) dan
**disalin ke `src/components/ui/`** — kodenya milik kita, bukan dependensi npm.

| Aturan | Contoh |
|---|---|
| Pakai komponen `ui/` dulu sebelum membuat sendiri | `Button`, `Card`, `Input`, `Field`, `Badge`, `Table`, `Dialog`, `Empty`, `Skeleton` |
| Import dari folder komponennya | `import { Button } from '@/components/ui/button'` |
| Ikon dari `@lucide/vue`, nama berakhiran `Icon` | `import { PlusIcon } from '@lucide/vue'` → `<PlusIcon />` |
| Warna **hanya** lewat token tema | `bg-primary`, `text-muted-foreground`, `border-border`, `bg-card`, `text-destructive`, `text-success` |
| Jangan warna mentah | ~~`bg-white`~~ ~~`text-slate-600`~~ (mode gelap jadi rusak) |
| Notifikasi | `toast.success('…')` dari `vue-sonner` (Toaster sudah dipasang di `App.vue`) |
| Gabung class | `cn('…', props.class)` dari `@/lib/utils` |

Menambah komponen shadcn lain: `npx shadcn-vue@latest add <nama>` (konfigurasi di `components.json`).
Varian tambahan proyek: `Badge` → `soft`, `success`, `warning`, `danger`; `Alert` → `success`, `warning`.

## Tema

Token warna ada di `src/style.css` (abu · navy · biru tua, mode terang & gelap). File ini, `composables/useTheme.ts`,
`lib/utils.ts`, `utils/format.ts`, `components/common/{ThemeToggle,UserMenu,PagePagination,BrandMark}.vue`, dan isi
`components/ui/` yang sama **harus identik** di `frontend-kasir` dan `frontend-admin` — ubah di satu app, salin ke app lain.
