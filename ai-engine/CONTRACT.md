# Kontrak AI engine ↔ backend

Engine dan backend **tidak saling memanggil**. Mereka hanya berbagi database MongoDB yang sama
(`MONGODB_URI` + `MONGODB_DB` harus sama). Kalau engine mati, backend tetap jalan dengan hasil terakhir.

| Collection | Ditulis oleh | Dibaca oleh |
|---|---|---|
| `transactions`, `products`, `stock_movements` | backend | engine (read-only) |
| `insights` | engine | backend (`GET /insights/*`) |
| `ai_jobs` | backend (MANUAL), seed (SEED), engine (SCHEDULE + status) | engine, backend |
| `ai_engine_status` | engine | backend (`GET /insights/status`) |

Semua waktu disimpan UTC. Tanggal (`date`) berformat `YYYY-MM-DD` menurut WIB.

## `ai_jobs`

```jsonc
{
  "_id": ObjectId,
  "status": "PENDING" | "RUNNING" | "DONE" | "FAILED",
  "trigger": "MANUAL" | "SCHEDULE" | "SEED",
  "kinds": ["association_rules", "forecast"],
  "requestedBy": { "id": "...", "name": "Ani Admin", "role": "ADMIN" } | null,
  "requestedAt": ISODate, "startedAt": ISODate | null, "finishedAt": ISODate | null,
  "error": "TipeError: pesan" | null,
  "summary": { "association_rules": {stats}, "forecast": {stats} } | null
}
```

Aturan:
- Hanya boleh ada **satu** job PENDING/RUNNING. Backend menolak job baru dengan `409 JOB_IN_PROGRESS`.
- Engine mengambil job dengan `find_one_and_update({status: PENDING} → RUNNING)` (atomik, urut `requestedAt`).
- Job RUNNING lebih dari 30 menit dianggap engine mati → FAILED (dilakukan backend maupun engine).
- Engine membuat job SCHEDULE sendiri kalau hasil tertua di `insights` lebih tua dari `AI_INTERVAL_MINUTES`.

## `ai_engine_status`

```jsonc
{ "_id": "engine", "lastSeenAt": ISODate, "version": "1.0.0", "intervalMinutes": 15, "host": "container-id" }
```
Diperbarui tiap putaran (±10 detik). Backend menganggap engine **offline** kalau `lastSeenAt` > 3 menit lalu.

## `insights` — `_id: "association_rules"`

```jsonc
{
  "_id": "association_rules", "kind": "association_rules", "algorithm": "apriori",
  "generatedAt": ISODate, "jobId": ObjectId | null, "engineVersion": "1.0.0",
  "params": { "historyDays": 90, "minSupport": 0.01, "minConfidence": 0.2, "minLift": 1.1, "maxLen": 3, "maxRules": 300 },
  "stats": { "transactions": 1003, "items": 25, "frequentItemsets": 41, "rules": 27,
             "from": ISODate, "to": ISODate, "durationMs": 52 },
  "rules": [
    {
      "antecedent": [ { "productId": ObjectId, "sku": "MKN-004", "name": "Mi Instan Goreng" } ],
      "consequent": [ { "productId": ObjectId, "sku": "KHR-004", "name": "Telur Ayam 1 kg" } ],
      "support": 0.0857, "confidence": 0.5686, "lift": 3.9, "count": 86
    }
  ]
}
```
`params` ditulis dengan nama Python (snake_case) — hanya untuk ditampilkan, backend tidak memprosesnya.
`consequent` selalu satu produk. Diurutkan `confidence × lift` menurun.

## `insights` — `_id: "forecast"`

```jsonc
{
  "_id": "forecast", "kind": "forecast", "generatedAt": ISODate, "jobId": ..., "engineVersion": "1.0.0",
  "params": { "history_days": 84, "horizon_days": 14, "lead_time_days": 3, "review_days": 7,
              "service_level": 0.95, "backtest_days": 7, "history_output_days": 28 },
  "stats": { "products": 25, "models": {"holt_winters": 11, "moving_average": 9, "croston": 5},
             "avgWape": 0.9, "reorderNeeded": 3, "from": "2026-07-09", "to": "2026-09-30", "durationMs": 411 },
  "products": [
    {
      "productId": ObjectId, "sku": "MKN-004", "name": "Mi Instan Goreng", "unit": "bungkus",
      "stock": 46,                    // stok saat dihitung
      "avgDaily": 5.1,                // rata-rata prediksi per hari
      "model": "holt_winters" | "moving_average" | "croston",
      "modelParams": { "alpha": 0.2, "beta": 0.05, "gamma": 0.1, "phi": 0.9 },
      "wape": 0.4253,                 // galat backtest model terpilih (null = data kurang)
      "baselineWape": 0.5251,         // galat baseline "rata-rata 7 hari"
      "daysUntilStockout": 9.3,       // null = tidak diperkirakan habis
      "stockoutDate": "2026-10-09",   // hanya kalau di dalam horizon
      "suggestedQty": 13,             // saran jumlah restock sekarang (0 = belum perlu)
      "reorderNeeded": false,         // stok <= titik pesan ulang
      "reorderPoint": 21.3,           // permintaan selama lead time + stok pengaman
      "safetyStock": 6,
      "excludedStockoutDays": 0,      // hari stok habis yang tidak dipakai melatih model
      "history":  [ { "date": "2026-09-02", "qty": 4 } ],                              // 28 hari terakhir
      "forecast": [ { "date": "2026-10-01", "qty": 4.8, "lower": 1.9, "upper": 7.7 } ] // 14 hari ke depan
    }
  ]
}
```

Mengubah bentuk dokumen = ubah engine **dan** `backend/app/schemas/insight.py` dalam PR yang sama.
