"""Seed data demo untuk Sistem Toko Koperasi.

Jalankan dari folder backend:

    python -m scripts.seed                       # isi data demo
    python -m scripts.seed --reset               # hapus data demo lama dulu (minta konfirmasi)
    python -m scripts.seed --reset --yes --days 70 --per-day 12

Yang dibuat:
- User: 1 OWNER, 1 LOGISTIK, 1 ADMIN, 2 KASIR (dibuat hanya jika belum ada)
- 5 kategori, 25 produk (dengan barcode EAN-13 contoh), 3 supplier, 10 anggota
- Riwayat 10 minggu: restock awal, restock mingguan (Senin), dan ±900 penjualan.

Penjualan TIDAK sepenuhnya acak: pola sengaja ditanam supaya AI engine punya sesuatu untuk
ditemukan, dan hasilnya bisa dicek ke daftar pola di bawah (lihat ASSOCIATIONS & PROFILE):
- Pasangan yang sering dibeli bersama (mi instan + telur, kopi + gula, roti + susu,
  buku + pulpen + pensil, pasta gigi + sikat gigi, keripik + teh botol).
- Pola mingguan: Sabtu–Minggu lebih ramai; ATK laku di hari sekolah, jajanan di akhir pekan.
- Tren: kopi sachet & jus jeruk naik, biskuit cokelat turun.
- Restock mingguan kadang kurang untuk produk yang laris → sesekali stok habis.

Jalan di server dengan MongoDB jarak jauh butuh beberapa menit (tiap penjualan memakai
transaction). Kecilkan --per-day kalau hanya ingin cepat.

Semua transaksi dibuat lewat fungsi service yang sama dengan API (checkout dan restock),
bukan insert langsung. Dengan begitu stok, HPP, stock movement, dan audit log tetap konsisten.

Memakai .env yang sama dengan server (MONGODB_URI, MONGODB_DB). Untuk demo:
    MONGODB_DB=koperasi_demo python -m scripts.seed --reset
"""

from __future__ import annotations

import argparse
import asyncio
import random
import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Agar "python scripts/seed.py" juga bisa menemukan paket app.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import get_settings  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.db import mongo  # noqa: E402
from app.db.indexes import ensure_indexes  # noqa: E402
from app.schemas.restock import RestockCreate  # noqa: E402
from app.schemas.sale import SaleCreate  # noqa: E402
from app.services import restock_service, sale_service  # noqa: E402
from app.utils.time import WIB, utcnow  # noqa: E402

DEMO_PASSWORD = "koperasi123"  # sama dengan scripts/create_initial_users.py
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
    (
        "SUP-001",
        "CV Sumber Makmur",
        "Andi",
        "081200000001",
        "andi@sumbermakmur.example",
        "Jl. Soekarno Hatta 10, Bandung",
    ),
    (
        "SUP-002",
        "UD Berkah Jaya",
        "Ratna",
        "081200000002",
        "ratna@berkahjaya.example",
        "Jl. Cihampelas 25, Bandung",
    ),
    (
        "SUP-003",
        "PT Mitra Pangan",
        "Dedi",
        "081200000003",
        "dedi@mitrapangan.example",
        "Jl. Asia Afrika 8, Bandung",
    ),
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
    ("OWNER", "Oscar Owner", "owner"),
    ("LOGISTIK", "Rudi Logistik", "logistik"),
    ("ADMIN", "Ani Admin", "admin"),
    ("KASIR", "Siti Kasir", "kasir1"),
    ("KASIR", "Andi Kasir", "kasir2"),
]
REQUIRED_PER_ROLE = {"OWNER": 1, "LOGISTIK": 1, "ADMIN": 1, "KASIR": 2}


@dataclass
class Actor:
    """Pengganti CurrentUser untuk skrip. Service hanya memakai id, name, dan role."""

    id: str
    name: str
    role: str


def demo_barcode(index: int) -> str:
    """EAN-13 contoh dengan prefix Indonesia (899) dan checksum valid, mis. 8990000000017.
    Bisa dicetak / ditampilkan di layar untuk mencoba fitur scan."""
    body = f"899{index:09d}"
    total = sum(int(d) * (3 if i % 2 else 1) for i, d in enumerate(body))
    return body + str((10 - total % 10) % 10)


# ---------------------------------------------------------------------------
# Persiapan data master
# ---------------------------------------------------------------------------


def confirm_reset(db_name: str) -> None:
    """Dijalankan SEBELUM event loop (input() memblokir)."""
    answer = input(
        f"Semua data toko di database '{db_name}' akan dihapus "
        "(produk, kategori, supplier, anggota, transaksi, stock movement, audit log). "
        "User tidak dihapus. Ketik 'ya' untuk lanjut: "
    )
    if answer.strip().lower() != "ya":
        print("Dibatalkan.")
        raise SystemExit(1)


async def reset_data(db) -> None:
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
    password_hash = hash_password(DEMO_PASSWORD)
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

    for index, (sku, name, category, unit, price, _cost, minimum) in enumerate(PRODUCTS, 1):
        if await db.products.find_one({"sku": sku}) is None:
            await db.products.insert_one(
                {
                    "sku": sku,
                    "barcode": demo_barcode(index),
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
    members = await db.members.find({"memberNumber": {"$in": [m[0] for m in MEMBERS]}}).to_list(length=None)
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
    return datetime(day.year, day.month, day.day, hour, minute, tzinfo=WIB).astimezone(UTC)


# ---------------------------------------------------------------------------
# Pola penjualan yang ditanam (dicari ulang oleh AI engine)
# ---------------------------------------------------------------------------

# sku: (bobot popularitas, tren per minggu, faktor akhir pekan, qty maks per transaksi)
PROFILE: dict[str, tuple[float, float, float, int]] = {
    "ATK-001": (5, 0.0, 0.5, 3),
    "ATK-002": (4, 0.0, 0.5, 3),
    "ATK-003": (2, 0.0, 0.5, 2),
    "ATK-004": (1.5, 0.0, 0.5, 2),
    "ATK-005": (1, 0.0, 0.5, 1),
    "MKN-001": (4, 0.0, 1.3, 1),
    "MKN-002": (3, -0.06, 1.4, 2),  # tren turun
    "MKN-003": (3, 0.0, 1.6, 2),
    "MKN-004": (9, 0.0, 1.2, 3),  # paling laris
    "MKN-005": (3, 0.0, 1.4, 3),
    "MNM-001": (8, 0.0, 1.3, 2),
    "MNM-002": (4, 0.0, 1.5, 2),
    "MNM-003": (6, 0.05, 1.0, 4),  # tren naik
    "MNM-004": (3, 0.0, 1.3, 2),
    "MNM-005": (1.5, 0.08, 1.4, 1),  # tren naik
    "KBR-001": (1, 0.0, 1.0, 1),
    "KBR-002": (1.5, 0.0, 1.0, 1),
    "KBR-003": (2, 0.0, 1.0, 2),
    "KBR-004": (2, 0.0, 1.0, 1),
    "KBR-005": (1, 0.0, 1.0, 1),
    "KHR-001": (2.5, 0.0, 1.2, 1),
    "KHR-002": (2.5, 0.0, 1.2, 1),
    "KHR-003": (1, 0.0, 1.3, 1),
    "KHR-004": (3, 0.0, 1.2, 1),
    "KHR-005": (1, 0.0, 1.0, 1),
}

# produk utama → (produk pendamping, peluang ikut dibeli)
ASSOCIATIONS: dict[str, list[tuple[str, float]]] = {
    "MKN-004": [("KHR-004", 0.55), ("MNM-001", 0.25)],  # mi instan + telur (+ air)
    "MNM-003": [("KHR-001", 0.45)],  # kopi + gula
    "MKN-001": [("MNM-004", 0.5)],  # roti + susu
    "ATK-001": [("ATK-002", 0.6), ("ATK-003", 0.35)],  # buku + pulpen (+ pensil)
    "ATK-003": [("ATK-004", 0.5)],  # pensil + penghapus
    "KBR-004": [("KBR-005", 0.55)],  # pasta gigi + sikat gigi
    "MKN-003": [("MNM-002", 0.5)],  # keripik + teh botol
}

# Senin..Minggu: banyaknya transaksi relatif
WEEKDAY_TRAFFIC = [1.0, 0.95, 1.0, 1.05, 1.15, 1.5, 1.35]
# jam buka 07–20 WIB, ramai pagi, siang, dan sore
HOUR_WEIGHTS = {7: 3, 8: 2, 9: 1, 10: 1, 11: 2, 12: 3, 13: 2, 14: 1, 15: 2, 16: 3, 17: 3, 18: 2, 19: 1, 20: 1}


def anchor_weights(day_index: int, weekend: bool) -> dict[str, float]:
    weeks = day_index / 7
    weights = {}
    for sku, (weight, trend, weekend_factor, _q) in PROFILE.items():
        w = weight * max(0.2, 1 + trend * weeks) * (weekend_factor if weekend else 1)
        weights[sku] = w
    return weights


def build_basket(rng: random.Random, weights: dict[str, float]) -> dict[str, int]:
    """Isi keranjang: 1–2 produk utama (sesuai popularitas) + pendampingnya + kadang produk acak."""
    skus = list(weights)
    basket: dict[str, int] = {}
    for anchor in rng.choices(skus, weights=[weights[s] for s in skus], k=1 if rng.random() < 0.7 else 2):
        basket[anchor] = rng.randint(1, PROFILE[anchor][3])
        for companion, chance in ASSOCIATIONS.get(anchor, []):
            if rng.random() < chance:
                basket[companion] = basket.get(companion, 0) + rng.randint(1, PROFILE[companion][3])
    if rng.random() < 0.15:
        extra = rng.choice(skus)
        basket[extra] = basket.get(extra, 0) + 1
    return basket


def build_timeline(rng: random.Random, days: int, per_day: float) -> list[tuple[datetime, str]]:
    """Kejadian berurutan waktu: restock awal, restock tiap Senin 07.00, dan penjualan harian."""
    now = utcnow()
    first_day = (now.astimezone(WIB) - timedelta(days=days - 1)).date()
    events: list[tuple[datetime, str]] = [(wib_datetime(first_day, 6, 30), "restock-initial")]

    for offset in range(days):
        day = first_day + timedelta(days=offset)
        if offset > 0 and day.weekday() == 0:
            moment = wib_datetime(day, 7, 0)
            if moment < now:
                events.append((moment, "restock-topup"))

        growth = 1 + 0.01 * (offset / 7)  # toko pelan-pelan makin ramai
        count = round(per_day * WEEKDAY_TRAFFIC[day.weekday()] * growth * rng.uniform(0.8, 1.2))
        hours = list(HOUR_WEIGHTS)
        for _ in range(count):
            hour = rng.choices(hours, weights=list(HOUR_WEIGHTS.values()))[0]
            moment = wib_datetime(day, hour, rng.randint(0, 59))
            if moment >= now - timedelta(minutes=5):
                continue
            events.append((moment, f"sale:{offset}"))

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


class SalesMemory:
    """Penjualan 7 hari terakhir per SKU, dipakai 'logistik simulasi' untuk menentukan jumlah restock."""

    def __init__(self) -> None:
        self.events: list[tuple[datetime, str, int]] = []

    def add(self, when: datetime, sku: str, qty: int) -> None:
        self.events.append((when, sku, qty))

    def last_week(self, now: datetime) -> dict[str, int]:
        since = now - timedelta(days=7)
        self.events = [e for e in self.events if e[0] >= since]
        totals: dict[str, int] = {}
        for _when, sku, qty in self.events:
            totals[sku] = totals.get(sku, 0) + qty
        return totals


def round_up(value: float, step: int) -> int:
    return max(step, int(-(-value // step) * step))


async def run_restock(
    db,
    rng,
    logistik: Actor,
    suppliers: dict,
    when: datetime,
    initial: bool,
    memory: SalesMemory,
    per_day: float,
) -> int:
    """Restock per supplier.

    Awal: stok ±2 minggu sesuai popularitas. Mingguan: produk yang stoknya tidak cukup untuk
    seminggu dipesan 0,85–1,35 × penjualan minggu lalu — kadang kurang, sehingga produk laris
    sesekali habis sebelum Senin berikutnya (dibutuhkan untuk menguji forecasting).
    """
    stock_by_sku = await current_stock(db, [row[0] for row in PRODUCTS])
    last_week = memory.last_week(when)
    total_weight = sum(p[0] for p in PROFILE.values())
    created = 0

    for supplier_code, supplier in suppliers.items():
        items = []
        for sku, *_rest in PRODUCTS:
            if SUPPLIER_BY_CATEGORY[CATEGORY_BY_SKU[sku]] != supplier_code:
                continue
            product = stock_by_sku[sku]
            stock = int(product["stock"])
            if initial:
                expected_week = PROFILE[sku][0] / total_weight * per_day * 7 * 1.6 * (PROFILE[sku][3] + 1) / 2
                quantity = round_up(expected_week * rng.uniform(1.6, 2.2) + int(product["minimumStock"]), 10)
            else:
                sold = last_week.get(sku, 0)
                if stock >= max(sold, int(product["minimumStock"]) * 2):
                    continue
                quantity = round_up(
                    max(sold * rng.uniform(0.85, 1.35) - stock, int(product["minimumStock"])), 10
                )
            items.append(
                {
                    "productId": str(product["_id"]),
                    "quantity": min(quantity, 10000),
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
    db, rng, cashiers: list[Actor], members: list[dict], when: datetime, day_index: int, memory: SalesMemory
) -> bool:
    """Satu penjualan berpola. False bila semua isi keranjang sedang habis."""
    weekend = when.astimezone(WIB).weekday() >= 5
    basket = build_basket(rng, anchor_weights(day_index, weekend))
    stock_by_sku = await current_stock(db, list(basket))

    items = []
    total = 0
    for sku, wanted in basket.items():
        product = stock_by_sku.get(sku)
        if not product or not product.get("isActive") or int(product["stock"]) <= 0:
            continue  # stok habis: pembeli hanya membeli yang ada
        quantity = min(wanted, int(product["stock"]))
        items.append({"productId": str(product["_id"]), "quantity": quantity})
        total += quantity * int(product["sellingPrice"])
    if not items:
        return False

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
        {"items": items, "customerName": customer_name, "memberId": member_id, "payment": payment}
    )
    await sale_service.checkout(db, rng.choice(cashiers), body, at=when)
    sku_by_id = {str(p["_id"]): sku for sku, p in stock_by_sku.items()}
    for item in items:
        memory.add(when, sku_by_id[item["productId"]], item["quantity"])
    return True


async def main(args: argparse.Namespace) -> None:
    settings = get_settings()  # membaca .env yang sama dengan server
    await mongo.connect(settings.mongodb_uri, settings.mongodb_db)
    db = mongo.get_database()
    try:
        await ensure_indexes(db)
        if args.reset:
            await reset_data(db)
        elif await db.transactions.count_documents({}) > 0:
            raise SystemExit(
                "Database sudah berisi transaksi. Jalankan dengan --reset agar data tidak dobel."
            )

        users = await ensure_users(db)
        suppliers, _products, members = await ensure_master_data(db)
        logistik = users["LOGISTIK"][0]
        cashiers = users["KASIR"]

        rng = random.Random(RANDOM_SEED)
        timeline = build_timeline(rng, args.days, args.per_day)
        planned = sum(1 for _w, kind in timeline if kind.startswith("sale"))
        print(f"Mensimulasikan {args.days} hari: ±{planned} penjualan (butuh beberapa menit)...")

        memory = SalesMemory()
        restocks = 0
        sales = 0
        skipped = 0
        for when, kind in timeline:
            if kind == "restock-initial":
                restocks += await run_restock(db, rng, logistik, suppliers, when, True, memory, args.per_day)
            elif kind == "restock-topup":
                restocks += await run_restock(db, rng, logistik, suppliers, when, False, memory, args.per_day)
            else:
                day_index = int(kind.split(":", 1)[1])
                if await run_sale(db, rng, cashiers, members, when, day_index, memory):
                    sales += 1
                    if sales % 100 == 0:
                        print(f"  ... {sales} penjualan")
                else:
                    skipped += 1

        print("Seed selesai.")
        print(f"  Transaksi restock : {restocks}")
        print(f"  Transaksi penjualan: {sales} (dilewati karena semua barang habis: {skipped})")
        print("Akun demo (password sama untuk semua akun buatan seed):")
        print(f"  password: {DEMO_PASSWORD}")
        for role, actors in users.items():
            print(f"  {role}: " + ", ".join(a.name for a in actors))
    finally:
        await mongo.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed data demo Sistem Toko Koperasi")
    parser.add_argument("--reset", action="store_true", help="hapus data toko lama sebelum seed")
    parser.add_argument("--yes", action="store_true", help="lewati pertanyaan konfirmasi reset")
    parser.add_argument(
        "--days", type=int, default=70, help="panjang riwayat dalam hari (bawaan 70 = 10 minggu)"
    )
    parser.add_argument(
        "--per-day", type=float, default=12, help="rata-rata penjualan per hari kerja (bawaan 12)"
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    if arguments.reset and not arguments.yes:
        confirm_reset(get_settings().mongodb_db)
    asyncio.run(main(arguments))
