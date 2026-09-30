"""AI engine Toko Koperasi: association rules (Apriori) & forecasting penjualan (Holt-Winters).

Berjalan terpisah dari backend. Membaca `transactions`, `products`, `stock_movements`,
menulis hasil ke `insights`, memproses antrean `ai_jobs`, dan mengirim denyut ke
`ai_engine_status`. Kontrak lengkap: CONTRACT.md.
"""

__version__ = "1.0.0"
