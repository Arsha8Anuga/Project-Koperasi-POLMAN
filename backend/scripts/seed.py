"""Seed data demo untuk Sistem Toko Koperasi.

Jalankan dari folder backend:

    python -m scripts.seed              # isi data demo
    python -m scripts.seed --reset      # hapus data demo lama dulu (minta konfirmasi)
    python -m scripts.seed --reset --yes --sales 80

Yang dibuat:
- User: 1 OWNER, 1 LOGISTIK, 1 ADMIN, 2 KASIR (dibuat hanya jika belum ada)
- 5 kategori, 25 produk, 3 supplier, 10 anggota
- Restock awal semua produk, restock susulan tiap minggu, dan sekitar 60 penjualan acak
  yang tersebar di 6 minggu terakhir.

Semua transaksi dibuat lewat fungsi service yang sama dengan API (checkout dan restock),
bukan insert langsung. Dengan begitu stok, HPP, stock movement, dan audit log tetap konsisten.

Kebutuhan: file .env berisi MONGODB_URI dan MONGODB_DB, serta modul BE-1 dan BE-2 sudah ada
(app.services.audit dan app.services.restock_service).
"""

from __future__ import annotations

import argparse
import asyncio
import os
import random
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Agar "python scripts/seed.py" juga bisa menemukan paket app.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import bcrypt  # noqa: E402
from pymongo import AsyncMongoClient  # noqa: E402

from app.schemas.restock import RestockCreate  # noqa: E402  (milik BE-2)
from app.schemas.sale import SaleCreate  # noqa: E402
from app.services import restock_service, sale_service  # noqa: E402
from app.utils.datetime_utils import WIB, utcnow  # noqa: E402

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv tidak wajib
    pass

DEMO_PASSWORD = "Demo12345"
SIMULATION_DAYS = 42  # 6 minggu
RANDOM_SEED = 2026  # hasil selalu sama setiap dijalankan

# ---------------------------------------------------------------------------
# Data master demo
# ---------------------------------------------------------------------------

CATEGORIES = [
    ("ATK", "Alat tulis kantor"),
    ("Makanan", "Makanan ringan dan roti"),
    ("Minuman", "Minuman kemasan"),
    ("Kebersihan", "Perlengkapan kebersihan"),
    ("Kebutuhan Harian", "Kebutuhan rumah tangga sehari-hari"),
]

# (sku, nama, kategori, satuan, harga jual, harga beli dasar, stok minimum)
PRODUCTS = [
    ("ATK-001", "Buku Tulis 38 Lembar", "ATK", "pcs", 4000, 3100, 20),
    ("ATK-002", "Pulpen Hitam", "ATK", "pcs", 2500, 1800, 20),
    ("ATK-003", "Pensil 2B", "ATK", "pcs", 2000, 1400, 20),
    ("ATK-004", "Penghapus", "ATK", "pcs", 1500, 1000, 15),
    ("ATK-005", "Penggaris 30 cm", "ATK", "pcs", 3500, 2500, 10),
    ("MKN-001", "Roti Tawar", "Makanan", "bungkus", 15000, 12000, 10),
    ("MKN-002", "Biskuit Cokelat", "Makanan", "bungkus", 8000, 6300, 15),
    ("MKN-003", "Keripik Singkong", "Makanan", "bungkus", 7000, 5200, 15),
    ("MKN-004", "Mi Instan Goreng", "Makanan", "bungkus", 3500, 2800, 30),
    ("MKN-005", "Wafer Vanila", "Makanan", "bungkus", 2500, 1900, 20),
    ("MNM-001", "Air Mineral 600 ml", "Minuman", "botol", 3500, 2500, 30),
    ("MNM-002", "Teh Botol", "Minuman", "botol", 5000, 3800, 20),
    ("MNM-003", "Kopi Sachet", "Minuman", "sachet", 2000, 1500, 30),
    ("MNM-004", "Susu Kotak Cokelat", "Minuman", "kotak", 6000, 4700, 15),
    ("MNM-005", "Jus Jeruk Kemasan", "Minuman", "botol", 7500, 5800, 10),
    ("KBR-001", "Sabun Cuci Tangan", "Kebersihan", "botol", 12000, 9000, 10),
    ("KBR-002", "Tisu Wajah", "Kebersihan", "bungkus", 9000, 6800, 10),
    ("KBR-003", "Sabun Mandi Batang", "Kebersihan", "pcs", 4000, 3000, 15),
    ("KBR-004", "Pasta Gigi", "Kebersihan", "pcs", 11000, 8500, 10),
    ("KBR-005", "Sikat Gigi", "Kebersihan", "pcs", 6000, 4400, 10),
    ("KHR-001", "Gula Pasir 1 kg", "Kebutuhan Harian", "kg", 17000, 14500, 10),
    ("KHR-002", "Minyak Goreng 1 liter", "Kebutuhan Harian", "liter", 19000, 16500, 10),
    ("KHR-003", "Beras 5 kg", "Kebutuhan Harian", "karung", 68000, 62000, 5),
    ("KHR-004", "Telur Ayam 1 kg", "Kebutuhan Harian", "kg", 30000, 26500, 8),
    ("KHR-005", "Garam Halus", "Kebutuhan Harian", "bungkus", 3000, 2200, 15),
]

SUPPLIERS = [
    ("SUP-001", "CV Sumber Makmur", "Andi", "081200000001", "andi@sumbermakmur.example", "Jl. Soekarno Hatta 10, Bandung"),
    ("SUP-002", "UD Berkah Jaya", "Ratna", "081200000002", "ratna@berkahjaya.example", "Jl. Cihampelas 25, Bandung"),
    ("SUP-003", "PT Mitra Pangan", "Dedi", "081200000003", "dedi@mitrapangan.example", "Jl. Asia Afrika 8, Bandung"),
]

# Kategori dipasok oleh supplier tertentu.
SUPPLIER_BY_CATEGORY = {
    "ATK": "SUP-001",
    "Kebersihan": "SUP-001",
    "Makanan": "SUP-002",
    "Minuman": "SUP-002",
    "Kebutuhan Harian": "SUP-003",
}

MEMBERS = [
    ("KOP-001", "Budi Santoso", "081311110001"),
    ("KOP-002", "Siti Aminah", "081311110002"),
    ("KOP-003", "Agus Salim", "081311110003"),
    ("KOP-004", "Dewi Lestari", "081311110004"),
    ("KOP-005", "Rahmat Hidayat", "081311110005"),
    ("KOP-006", "Nining Kurnia", "081311110006"),
    ("KOP-007", "Yusuf Maulana", "081311110007"),
    ("KOP-008", "Lina Marlina", "081311110008"),
    ("KOP-009", "Eko Prasetyo", "081311110009"),
    ("KOP-010", "Tuti Handayani", "081311110010"),
]

CUSTOMER_NAMES = ["Budi", "Sari", "Wawan", "Rina", "Joko", "Mira", "Fajar", "Ani"]

# (role, nama, username), jumlah yang dibutuhkan per role
DEMO_USERS = [
    ("OWNER", "Owner Koperasi", "owner"),
    ("LOGISTIK", "Rudi Logistik", "logistik"),
    ("ADMIN", "Admin Koperasi", "admin"),
    ("KASIR", "Siti Kasir", "siti"),
    ("KASIR", "Andi Kasir", "andi"),
]
REQUIRED_PER_ROLE = {"OWNER": 1, "LOGISTIK": 1, "ADMIN": 1, "KASIR": 2}


@dataclass
class Actor:
    """Pengganti CurrentUser untuk skrip. Service hanya memakai id, name, dan role."""

    id: str
    name: str
    role: str


# ---------------------------------------------------------------------------
# Persiapan data master
# ---------------------------------------------------------------------------


async def confirm_reset(db, assume_yes: bool) -> None:
    if not assume_yes:
        answer = input(
            f"Semua data toko di database '{db.name}' akan dihapus "
            "(produk, kategori, supplier, anggota, transaksi, stock movement, audit log). "
            "User tidak dihapus. Ketik 'ya' untuk lanjut: "
        )
        if answer.strip().lower() != "ya":
            print("Dibatalkan.")
            raise SystemExit(1)
    for name in (
        "transactions",
        "stock_movements",
        "counters",
        "audit_logs",
        "products",
        "categories",
        "suppliers",
        "members",
    ):
        await db[name].delete_many({})
    print("Data lama dihapus.")


async def ensure_users(db) -> dict[str, list[Actor]]:
    """Pastikan tiap role punya cukup user. User yang sudah ada dipakai ulang."""
    now = utcnow()
    password_hash = bcrypt.hashpw(DEMO_PASSWORD.encode(), bcrypt.gensalt(rounds=12)).decode()
    result: dict[str, list[Actor]] = {}

    for role, needed in REQUIRED_PER_ROLE.items():
        cursor = db.users.find({"role": role, "isActive": True}).sort("_id", 1)
        existing = await cursor.to_list(length=None)
        actors = [Actor(str(u["_id"]), u["name"], role) for u in existing]
        candidates = [d for d in DEMO_USERS if d[0] == role]
        for _, name, username in candidates:
            if len(actors) >= needed:
                break
            if await db.users.find_one({"username": username}):
                continue
            inserted = await db.users.insert_one(
                {
                    "name": name,
                    "username": username,
                    "passwordHash": password_hash,
                    "role": role,
                    "isActive": True,
                    "createdAt": now,
                    "updatedAt": now,
                }
            )
            actors.append(Actor(str(inserted.inserted_id), name, role))
            print(f"User dibuat: {username} ({role}), password {DEMO_PASSWORD}")
        result[role] = actors
    return result


async def ensure_master_data(db) -> tuple[dict, list[dict], list[dict]]:
    """Buat kategori, produk, supplier, dan anggota bila belum ada.

    Mengembalikan (peta supplierCode ke supplier, daftar produk, daftar anggota).
    """
    now = utcnow()

    category_ids: dict[str, object] = {}
    for name, description in CATEGORIES:
        doc = await db.categories.find_one({"name": name})
        if doc is None:
            inserted = await db.categories.insert_one(
                {"name": name, "description": description, "isActive": True}
            )
            category_ids[name] = inserted.inserted_id
        else:
            category_ids[name] = doc["_id"]

    for sku, name, category, unit, price, _cost, minimum in PRODUCTS:
        if await db.products.find_one({"sku": sku}) is None:
            await db.products.insert_one(
                {
                    "sku": sku,
                    "name": name,
                    "categoryId": category_ids[category],
                    "unit": unit,
                    "sellingPrice": price,
                    "costPrice": 0,  # produk baru mulai dari nol (dokumen 04 bagian 7.6)
                    "lastPurchasePrice": 0,
                    "stock": 0,
                    "minimumStock": minimum,
                    "imageUrl": None,
                    "isActive": True,
                    "createdAt": now,
                    "updatedAt": now,
                }
            )

    suppliers: dict[str, dict] = {}
    for code, name, contact, phone, email, address in SUPPLIERS:
        doc = await db.suppliers.find_one({"supplierCode": code})
        if doc is None:
            doc = {
                "supplierCode": code,
                "name": name,
                "contactPerson": contact,
                "phone": phone,
                "email": email,
                "address": address,
                "notes": None,
                "isActive": True,
                "createdAt": now,
                "updatedAt": now,
            }
            inserted = await db.suppliers.insert_one(doc)
            doc["_id"] = inserted.inserted_id
        suppliers[code] = doc

    for number, name, phone in MEMBERS:
        if await db.members.find_one({"memberNumber": number}) is None:
            await db.members.insert_one(
                {
                    "memberNumber": number,
                    "name": name,
                    "phone": phone,
                    "joinedAt": "2026-01-10",
                    "isActive": True,
                    "createdAt": now,
                    "updatedAt": now,
                }
            )

    skus = [row[0] for row in PRODUCTS]
    products = await db.products.find({"sku": {"$in": skus}}).sort("sku", 1).to_list(length=None)
    members = await db.members.find(
        {"memberNumber": {"$in": [m[0] for m in MEMBERS]}}
    ).to_list(length=None)
    return suppliers, products, members


# ---------------------------------------------------------------------------
# Simulasi transaksi
# ---------------------------------------------------------------------------

BASE_COST = {row[0]: row[5] for row in PRODUCTS}
CATEGORY_BY_SKU = {row[0]: row[2] for row in PRODUCTS}


def round_to(value: float, step: int) -> int:
    return int(round(value / step) * step)


def random_purchase_price(rng: random.Random, sku: str) -> int:
    """Harga beli sekitar harga dasar, bervariasi 4 persen agar HPP rata-rata berubah."""
    base = BASE_COST[sku]
    return max(50, round_to(base * rng.uniform(0.96, 1.04), 50))


def wib_datetime(day, hour: int, minute: int) -> datetime:
    return datetime(day.year, day.month, day.day, hour, minute, tzinfo=WIB).astimezone(timezone.utc)


def build_timeline(rng: random.Random, sales_count: int) -> list[tuple[datetime, str]]:
    """Buat daftar kejadian berurutan waktu: restock awal, restock mingguan, dan penjualan."""
    now = utcnow()
    first_day = (now.astimezone(WIB) - timedelta(days=SIMULATION_DAYS - 1)).date()

    events: list[tuple[datetime, str]] = [(wib_datetime(first_day, 7, 0), "restock-initial")]

    # Restock susulan setiap 7 hari pukul 07.30 WIB (hanya bila waktunya sudah lewat).
    week = 1
    while True:
        restock_day = first_day + timedelta(days=7 * week)
        moment = wib_datetime(restock_day, 7, 30)
        if moment >= now - timedelta(hours=1):
            break
        events.append((moment, "restock-topup"))
        week += 1

    made = 0
    while made < sales_count:
        day = first_day + timedelta(days=rng.randint(0, SIMULATION_DAYS - 1))
        moment = wib_datetime(day, rng.randint(8, 16), rng.randint(0, 59))
        if moment <= wib_datetime(first_day, 8, 0) or moment >= now - timedelta(minutes=5):
            continue
        events.append((moment, "sale"))
        made += 1

    events.sort(key=lambda event: event[0])
    return events


def cash_given(rng: random.Random, total: int) -> int:
    """Uang yang diberikan pembeli: pas, atau dibulatkan ke atas."""
    options = {total}
    for step in (1000, 5000, 10000, 50000, 100000):
        options.add(((total + step - 1) // step) * step)
    return rng.choice(sorted(options))


async def current_stock(db, skus: list[str]) -> dict[str, dict]:
    docs = await db.products.find({"sku": {"$in": skus}}).to_list(length=None)
    return {d["sku"]: d for d in docs}


async def run_restock(
    db, rng, logistik: Actor, suppliers: dict, when: datetime, initial: bool
) -> int:
    """Buat restock per supplier. Awal: semua produk. Susulan: hanya produk yang menipis."""
    stock_by_sku = await current_stock(db, [row[0] for row in PRODUCTS])
    created = 0

    for supplier_code, supplier in suppliers.items():
        items = []
        for sku, *_rest in PRODUCTS:
            if SUPPLIER_BY_CATEGORY[CATEGORY_BY_SKU[sku]] != supplier_code:
                continue
            product = stock_by_sku[sku]
            if initial:
                quantity = rng.randint(80, 150)
            elif int(product["stock"]) <= int(product["minimumStock"]) * 3:
                quantity = rng.randint(40, 100)
            else:
                continue
            items.append(
                {
                    "productId": str(product["_id"]),
                    "quantity": quantity,
                    "purchasePrice": random_purchase_price(rng, sku),
                }
            )
        if not items:
            continue
        body = RestockCreate.model_validate(
            {
                "supplierId": str(supplier["_id"]),
                "items": items,
                "notes": "Restock awal (seed)" if initial else "Restock mingguan (seed)",
            }
        )
        await restock_service.create(db, logistik, body, at=when)
        created += 1
    return created


async def run_sale(
    db, rng, cashiers: list[Actor], members: list[dict], when: datetime
) -> bool:
    """Buat satu penjualan acak. Mengembalikan False bila tidak ada produk berstok."""
    stock_by_sku = await current_stock(db, [row[0] for row in PRODUCTS])
    available = [p for p in stock_by_sku.values() if p.get("isActive") and int(p["stock"]) > 0]
    if not available:
        return False

    chosen = rng.sample(available, k=min(len(available), rng.randint(1, 4)))
    items = []
    total = 0
    for product in chosen:
        quantity = rng.randint(1, min(5, int(product["stock"])))
        items.append({"productId": str(product["_id"]), "quantity": quantity})
        total += quantity * int(product["sellingPrice"])

    payment: dict = {"method": "CASH", "amountPaid": cash_given(rng, total)}
    if rng.random() < 0.3:
        payment = {"method": "QRIS"}

    member_id = None
    customer_name = None
    if members and rng.random() < 0.3:
        member_id = str(rng.choice(members)["_id"])
    elif rng.random() < 0.4:
        customer_name = rng.choice(CUSTOMER_NAMES)

    body = SaleCreate.model_validate(
        {
            "items": items,
            "customerName": customer_name,
            "memberId": member_id,
            "payment": payment,
        }
    )
    await sale_service.checkout(db, rng.choice(cashiers), body, at=when)
    return True


async def main(args: argparse.Namespace) -> None:
    uri = os.environ.get("MONGODB_URI")
    if not uri:
        raise SystemExit("MONGODB_URI belum diatur. Isi di file .env atau environment.")
    db_name = os.environ.get("MONGODB_DB", "koperasi_db")

    client = AsyncMongoClient(uri)
    db = client[db_name]
    try:
        if args.reset:
            await confirm_reset(db, args.yes)
        elif await db.transactions.count_documents({}) > 0:
            raise SystemExit(
                "Database sudah berisi transaksi. Jalankan dengan --reset agar data tidak dobel."
            )

        users = await ensure_users(db)
        suppliers, _products, members = await ensure_master_data(db)
        logistik = users["LOGISTIK"][0]
        cashiers = users["KASIR"]

        rng = random.Random(RANDOM_SEED)
        timeline = build_timeline(rng, args.sales)

        restocks = 0
        sales = 0
        for when, kind in timeline:
            if kind == "restock-initial":
                restocks += await run_restock(db, rng, logistik, suppliers, when, initial=True)
            elif kind == "restock-topup":
                restocks += await run_restock(db, rng, logistik, suppliers, when, initial=False)
            elif await run_sale(db, rng, cashiers, members, when):
                sales += 1

        print("Seed selesai.")
        print(f"  Transaksi restock : {restocks}")
        print(f"  Transaksi penjualan: {sales}")
        print("Akun demo (password sama untuk semua akun buatan seed):")
        print(f"  password: {DEMO_PASSWORD}")
        for role, actors in users.items():
            print(f"  {role}: " + ", ".join(a.name for a in actors))
    finally:
        await client.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed data demo Sistem Toko Koperasi")
    parser.add_argument("--reset", action="store_true", help="hapus data toko lama sebelum seed")
    parser.add_argument("--yes", action="store_true", help="lewati pertanyaan konfirmasi reset")
    parser.add_argument("--sales", type=int, default=60, help="jumlah penjualan acak (bawaan 60)")
    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(main(parse_args()))
