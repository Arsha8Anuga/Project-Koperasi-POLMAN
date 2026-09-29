# Backend Koperasi (FastAPI + MongoDB)

## Menjalankan

```bash
cd backend
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # isi MONGODB_URI, JWT_SECRET, TEST_MONGODB_DB
python -m scripts.create_initial_users                 # owner / logistik / admin / kasir1, password: koperasi123
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger ada di http://localhost:8000/docs. Untuk mencoba endpoint yang butuh login, panggil `POST /api/v1/auth/login`, salin `data.token`, lalu klik **Authorize**.

## Test & lint

```bash
pytest                 # memakai DB TEST_MONGODB_DB, yang DI-DROP setiap test. Beri nama sendiri, mis. koperasi_test_be2
ruff check . && ruff format --check .
```

## Aturan untuk BE-2 / BE-3 (wajib dibaca sebelum menulis router)

| Butuh | Pakai | Jangan |
|---|---|---|
| DB / client (transaction) | `Depends(get_db)`, `Depends(get_client)` dari `app.api.deps` | import `app.db.mongo` langsung |
| User login + cek role | `user: CurrentUser = Depends(require_roles(Role.LOGISTIK))` | cek role manual di service |
| Error bisnis | `raise AppError(409, "INSUFFICIENT_STOCK", "Stok tidak mencukupi", details)` | `HTTPException` |
| Response | `return ok(data, "pesan")` / `paginated(items, page, total)` + `response_model=ApiResponse[X]` | return dict mentah tanpa `response_model` |
| Pagination | `page: PageParams = Depends()` → `repositories.base.find_page(...)` | hitung skip sendiri |
| Filter tanggal | `created_at_filter(date_from, date_to)` dari `app.utils.time` | `datetime.now()` tanpa zona |
| Pencarian | `search_regex(term)` dari `app.utils.text` | text index / regex mentah dari user |
| Audit | `await audit.log(db, user, AuditAction.X, AuditModule.Y, ref_id, "deskripsi", session=session)` | tulis ke `audit_logs` langsung |
| Transaction | `await run_in_transaction(client, txn)` dari `app.db.transaction` | `start_session` manual |
| Schema | turunkan dari `CamelModel` / `DocModel` (`app.schemas.common`) | `alias=` manual per field |
| Dashboard | isi fungsi di `app/services/dashboard/logistik.py` (BE-2) / `owner.py` (BE-3) | ubah router dashboard |

Router baru didaftarkan di `app/api/v1/router.py`, di bagian masing-masing.
