import numpy as np

from engine.forecast import (
    choose_and_forecast,
    croston,
    days_until_stockout,
    fill_censored,
    holt_winters,
    restock_advice,
    wape,
)

WEEK = np.array([5, 5, 5, 6, 7, 12, 10], dtype=float)  # Sabtu–Minggu ramai


def weekly_series(weeks=12, noise=0.8, trend=0.0, seed=0):
    rng = np.random.default_rng(seed)
    y = np.tile(WEEK, weeks) + trend * np.arange(7 * weeks)
    return np.clip(y + rng.normal(0, noise, len(y)), 0, None)


def test_holt_winters_menangkap_pola_mingguan():
    y = weekly_series()
    f, sigma, params = holt_winters(y, 14)
    assert len(f) == 14 and sigma < 2
    # hari ke-5 & ke-6 setelah data (posisi Sabtu/Minggu) jauh lebih tinggi dari hari biasa
    assert f[5] > f[1] + 3 and f[12] > f[8] + 3
    assert set(params) == {"alpha", "beta", "gamma", "phi"}


def test_model_mengalahkan_baseline_pada_data_musiman():
    y = weekly_series(noise=0.5)
    choice = choose_and_forecast(y, 14)
    assert choice.model == "holt_winters"
    assert choice.wape is not None and choice.baseline_wape is not None
    assert choice.wape < choice.baseline_wape


def test_permintaan_jarang_pakai_croston():
    y = np.zeros(84)
    y[::9] = 3  # laku tiap ~9 hari
    choice = choose_and_forecast(y, 14)
    assert choice.model == "croston"
    assert 0.2 < choice.forecast[0] < 0.5  # ± 3/9 per hari
    f, _ = croston(np.zeros(10), 5)
    assert f.sum() == 0


def test_hari_stok_habis_tidak_menurunkan_prediksi():
    y = weekly_series(noise=0.3)
    censored = y.copy()
    censored[-10:-6] = np.nan  # 4 hari barang kosong
    filled = fill_censored(censored)
    assert not np.isnan(filled).any() and abs(filled[-10] - y[-10]) < 2
    naive = y.copy()
    naive[-10:-6] = 0  # kalau hari kosong dianggap "tidak laku"
    assert choose_and_forecast(censored, 7).forecast.sum() > choose_and_forecast(naive, 7).forecast.sum()


def test_wape():
    assert wape(np.array([10, 10]), np.array([8, 12])) == 0.2
    assert wape(np.array([0, 0]), np.array([1, 1])) is None
    assert wape(np.array([10, np.nan]), np.array([5, 100])) == 0.5


def test_hari_sampai_stok_habis():
    f = np.array([5.0] * 14)
    assert days_until_stockout(12, f) == 2.4
    assert days_until_stockout(0, f) == 0.0
    assert days_until_stockout(100, f) == 20.0  # di luar horizon: diperkirakan dari rata-rata
    assert days_until_stockout(10, np.zeros(14)) is None


def test_saran_restock():
    f = np.array([5.0] * 14)
    advice = restock_advice(stock=10, forecast=f, sigma=2.0, lead_time=3, review=7, service_level=0.95)
    # stok pengaman = ceil(1.645 × 2 × √3) = 6 ; titik pesan = 15 + 6 ; saran = 50 + 6 − 10
    assert advice.safety_stock == 6 and advice.reorder_point == 21
    assert advice.suggested_qty == 46 and advice.reorder_needed is True
    assert restock_advice(200, f, 2.0, 3, 7, 0.95).suggested_qty == 0
