# frontend-admin — Panel Admin

Vue 3 + TypeScript + Vite + Pinia + Tailwind v4 + shadcn-vue + Chart.js. Dipakai role **OWNER**, **LOGISTIK**, **ADMIN**.

## Menjalankan

```bash
npm install
cp .env.example .env.local        # VITE_API_URL=http://localhost:8000/api/v1
npm run dev                       # http://localhost:5174
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

## Pola halaman (admin)

| Kebutuhan | Pakai |
|---|---|
| Daftar + filter + pagination | `usePagination()` + `DataTable` + `TablePagination` di dalam `<Card class="gap-0 overflow-hidden py-0">` |
| Pencarian / filter pilihan | `SearchInput`, `FilterToggle`, `NativeSelect` |
| Form di dialog | `Modal` (shadcn `Dialog`) + `FormField` (shadcn `Field`) + `DialogFooter` |
| Konfirmasi aktif/nonaktif | `ConfirmModal` (shadcn `AlertDialog`) |
| Menu samping | `AppSidebar` (shadcn `Sidebar`, dibangun dari `router/routes.ts` + `meta.roles`) |
| Grafik | `ChartCard` + komponen di `components/charts` (warna dari token `--chart-1..5`) |
