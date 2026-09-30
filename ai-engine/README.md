# AI engine — Toko Koperasi

Worker Python terpisah dari backend. Membaca transaksi dari MongoDB, menjalankan dua analisis,
menulis hasilnya ke collection `insights`. Backend dan frontend hanya **membaca** hasil itu
(kontrak lengkap: [CONTRACT.md](CONTRACT.md)).

| Analisis | Algoritma | Dipakai di |
|---|---|---|
| Produk yang sering dibeli bersama | **Apriori** (association rules: support, confidence, lift) | Kasir: saran di keranjang · Owner: tabel pasangan produk |
| Prediksi penjualan & saran restock | **Holt-Winters** (musiman mingguan, tren teredam) + fallback Croston / rata-rata bergerak, dipilih lewat **backtest WAPE** | Logistik & Owner: halaman Stok, form restock |

Semua algoritma ditulis sendiri di atas **numpy** (lihat `engine/association.py`, `engine/forecast.py`),
tanpa pandas/scikit-learn/statsmodels: image kecil, jalan di CPU lama (tanpa AVX2), dan tiap
rumus bisa ditunjukkan saat presentasi. Dengan ±1.000 transaksi & 25 produk, satu putaran < 1 detik.

## Menjalankan

```bash
cd ai-engine
pip install -r requirements-dev.txt
export MONGODB_URI="mongodb://..." MONGODB_DB=koperasi_dev   # SAMA dengan backend
python -m engine --once     # hitung sekali sekarang, lalu keluar
python -m engine            # worker: cek antrean tiap 10 detik, hitung ulang tiap 15 menit
pytest && ruff check .
```

| Env | Bawaan | Arti |
|---|---|---|
| `AI_INTERVAL_MINUTES` | 15 | Jadwal hitung ulang otomatis |
| `AI_POLL_SECONDS` | 10 | Seberapa sering antrean `ai_jobs` dicek (tombol "Hitung ulang" admin) |
| `AI_MIN_SUPPORT` / `AI_MIN_CONFIDENCE` / `AI_MIN_LIFT` | 0.01 / 0.2 / 1.1 | Ambang association rules |
| `AI_ASSOC_HISTORY_DAYS` | 90 | Transaksi yang dianalisis |
| `AI_LEAD_TIME_DAYS` | 3 | Waktu tunggu barang dari supplier |
| `AI_REVIEW_DAYS` | 7 | Jarak antar restock rutin |
| `AI_SERVICE_LEVEL` | 0.95 | Target peluang tidak kehabisan stok (menentukan stok pengaman) |

## Cara kerja singkat

**Association rules.** Tiap transaksi diubah jadi himpunan produk. Apriori mencari kombinasi
produk yang muncul di ≥ `minSupport` transaksi, lalu membentuk aturan `A → C`:
`confidence = P(C | A)`, `lift = confidence / P(C)`. Lift > 1 berarti lebih sering dibeli bersama
daripada kebetulan.

**Forecasting.** Penjualan harian 12 minggu terakhir per produk. Hari saat stok habis dikeluarkan
dari data latih (penjualannya 0 karena barang tidak ada, bukan karena tidak laku). Holt-Winters
dilatih dengan grid search α/β/γ, lalu diuji pada 7 hari terakhir yang disembunyikan; kalau tidak
lebih baik dari "rata-rata 7 hari", baseline itulah yang dipakai. Dari prediksi 14 hari dihitung:
perkiraan hari stok habis, stok pengaman `z·σ·√leadTime`, dan saran restock
`permintaan(leadTime + review) + stok pengaman − stok`.

**Batasan jujur.** Data demo adalah simulasi dengan pola yang sengaja ditanam (lihat
`backend/scripts/seed.py`); engine terbukti menemukan pola itu kembali. Penjualan harian per produk
kecil (1–5 unit), sehingga WAPE harian wajar tinggi (±0,4–0,9) — lebih bermakna dibaca sebagai
kecenderungan mingguan daripada angka per hari.
