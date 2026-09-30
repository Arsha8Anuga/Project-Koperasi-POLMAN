from engine import config
from engine.config import Settings, load_env_files, uri_problem


def test_env_file_mengisi_yang_belum_di_set(tmp_path, monkeypatch):
    for key in ("MONGODB_URI", "MONGODB_DB", "AI_LEAD_TIME_DAYS", "JWT_SECRET"):
        monkeypatch.setenv(key, "x")  # dicatat monkeypatch → dipulihkan setelah test
        monkeypatch.delenv(key)
    monkeypatch.setenv("MONGODB_DB", "dari_env")
    env = tmp_path / ".env"
    env.write_text(
        '﻿# komentar\nMONGODB_URI="mongodb://u:p%2Bx@h:1/?authSource=admin"\n'
        "MONGODB_DB=dari_file\nJWT_SECRET=tidak-ikut\nexport AI_LEAD_TIME_DAYS=5\n",
        encoding="utf-8",
    )
    assert load_env_files((tmp_path / "tidak-ada", env)) == env
    s = Settings()
    assert s.mongodb_uri == "mongodb://u:p%2Bx@h:1/?authSource=admin"  # kutip dibuang
    assert s.mongodb_db == "dari_env"  # env yang sudah ada tidak ditimpa
    assert s.forecast.lead_time_days == 5
    assert "JWT_SECRET" not in config.os.environ  # hanya MONGODB_* dan AI_* yang diambil


def test_uri_problem():
    assert uri_problem("mongodb://localhost:27017") is None
    assert uri_problem("mongodb+srv://x.example.net") is None
    assert "teks contoh" in uri_problem("<isi sama persis>")
    msg = uri_problem("'mongo://user:rahasia@host")
    assert "rahasia" not in msg


def test_nilai_kosong_dan_berkutip_dari_environment(monkeypatch):
    monkeypatch.setenv("MONGODB_URI", "  'mongodb://localhost:27017'  ")
    monkeypatch.setenv("MONGODB_DB", "")
    s = Settings()
    assert s.mongodb_uri == "mongodb://localhost:27017"
    assert s.mongodb_db == "koperasi_dev"
