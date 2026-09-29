from app.services.hpp import moving_average


def test_contoh_dokumen():
    assert moving_average(50, 3000, 100, 3200) == 3133


def test_stok_awal_nol():
    assert moving_average(0, 0, 100, 3200) == 3200


def test_stok_nol_tapi_cost_lama_ada():
    assert moving_average(0, 5000, 10, 3000) == 3000  # cost lama diabaikan


def test_pembulatan_half_up():
    assert moving_average(1, 1, 1, 2) == 2  # 1,5 → 2
