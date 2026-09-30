# Dokumentasi Sistem Toko Koperasi POLMAN

Dokumentasi ini menjelaskan Sistem Toko Koperasi POLMAN secara menyeluruh: tujuan, arsitektur, hak akses, fitur, model data, antarmuka pemrograman (API), mesin analisis (AI engine), pemindaian barcode, cara menjalankan untuk pengembangan, cara deployment, serta aspek keamanan dan pengujian.

Dokumentasi tersedia dalam dua bentuk dengan isi yang sama:

| Bentuk | Lokasi | Kegunaan |
|---|---|---|
| Markdown per bab | folder `docs/` | Dibaca langsung di repositori, mudah diperbarui per bagian |
| HTML tunggal | `docs/dokumentasi-toko-koperasi.html` | Dibuka di peramban tanpa server, dilengkapi daftar isi dan mode gelap |

## Daftar isi

| No. | Bab | Isi pokok |
|---|---|---|
| 1 | [Gambaran Umum](01-gambaran-umum.md) | Latar belakang, tujuan, ruang lingkup, istilah |
| 2 | [Arsitektur Sistem](02-arsitektur.md) | Komponen, teknologi, alur data, struktur repositori |
| 3 | [Peran dan Hak Akses](03-peran-dan-hak-akses.md) | Lima peran, aplikasi yang dapat dibuka, matriks hak akses |
| 4 | [Fitur Aplikasi](04-fitur-aplikasi.md) | Fitur aplikasi kasir dan panel admin per peran |
| 5 | [Model Data](05-model-data.md) | Koleksi MongoDB, field penting, indeks, aturan bisnis |
| 6 | [Referensi API](06-referensi-api.md) | Format respons, autentikasi, daftar endpoint, kode galat |
| 7 | [AI Engine](07-ai-engine.md) | Association rules, forecasting, saran restock, kontrak data |
| 8 | [Pemindaian Barcode](08-pemindaian-barcode.md) | Scanner USB, input manual, kamera, format yang didukung |
| 9 | [Instalasi dan Pengembangan](09-instalasi-dan-pengembangan.md) | Menjalankan tiap komponen secara lokal, data demo, konvensi kode |
| 10 | [Deployment](10-deployment.md) | Docker Compose, Portainer, domain dan HTTPS, variabel lingkungan |
| 11 | [Keamanan dan Pengujian](11-keamanan-dan-pengujian.md) | Mekanisme keamanan, audit trail, pengujian otomatis |

## Konvensi penulisan

Nama field, endpoint, perintah, dan nama berkas ditulis dengan huruf monospace, misalnya `sellingPrice` atau `GET /api/v1/products`. Nilai yang harus diganti sesuai lingkungan masing-masing ditulis di antara tanda kurung sudut, misalnya `<domain>`. Seluruh waktu yang tersimpan di basis data menggunakan UTC, sedangkan tanggal yang ditampilkan dan dipakai sebagai filter menggunakan zona waktu WIB (Asia/Jakarta).

HTML tunggal dibangun ulang dari berkas Markdown dengan perintah `python docs/build_html.py` (membutuhkan Pandoc), sehingga perubahan cukup dilakukan pada berkas Markdown.
