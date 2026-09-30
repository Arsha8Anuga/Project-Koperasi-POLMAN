import random

from engine.association import apriori


def make_baskets(n=1000, seed=1):
    """Pola ditanam: MI → TELUR (60%), BUKU → PULPEN (60%), BUKU+PULPEN → PENSIL (50%); sisanya acak."""
    rng = random.Random(seed)
    others = [f"X{i}" for i in range(15)]
    baskets = []
    for _ in range(n):
        b = set()
        r = rng.random()
        if r < 0.25:
            b.add("MI")
            if rng.random() < 0.6:
                b.add("TELUR")
        elif r < 0.4:
            b.add("BUKU")
            if rng.random() < 0.6:
                b.add("PULPEN")
                if rng.random() < 0.5:
                    b.add("PENSIL")
        b.add(rng.choice(others))
        if rng.random() < 0.1:
            b.add(rng.choice(["TELUR", "PULPEN", "PENSIL"]))  # derau: dibeli sendiri
        baskets.append(b)
    return baskets


def find(rules, ante, cons):
    return next((r for r in rules if set(r.antecedent) == set(ante) and r.consequent == cons), None)


def test_menemukan_pola_yang_ditanam():
    res = apriori(make_baskets(), min_support=0.01, min_confidence=0.2, min_lift=1.1, max_len=3)
    assert res.transactions == 1000

    mi_telur = find(res.rules, ["MI"], "TELUR")
    assert mi_telur is not None and 0.5 < mi_telur.confidence < 0.72 and mi_telur.lift > 2

    # aturan dua-item → satu item (k = 3)
    pensil = find(res.rules, ["BUKU", "PULPEN"], "PENSIL")
    assert pensil is not None and pensil.confidence > 0.4

    # pasangan barang acak tidak boleh lolos sebagai aturan kuat
    assert not any(r.consequent.startswith("X") and r.lift > 1.5 and r.confidence > 0.3 for r in res.rules)


def test_rumus_support_confidence_lift_manual():
    # 10 transaksi: A di 5, B di 4, A&B di 3
    baskets = [{"A", "B"}] * 3 + [{"A"}] * 2 + [{"B"}] + [{"C"}] * 4
    res = apriori(baskets, min_support=0.1, min_confidence=0.1, min_lift=0.0, max_len=2)
    r = find(res.rules, ["A"], "B")
    assert r.count == 3 and r.support == 0.3
    assert r.confidence == 0.6  # 3/5
    assert r.lift == 1.5  # 0.6 / (4/10)


def test_data_kosong_dan_filter():
    assert apriori([], 0.01, 0.2, 1.1).rules == []
    baskets = [{"A", "B"}] * 3 + [{"A"}] * 2 + [{"B"}] + [{"C"}] * 4
    assert apriori(baskets, 0.1, 0.9, 0.0, 2).rules == []  # confidence tertinggi 0.75 (B→A)
