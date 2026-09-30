"""Association rules dengan algoritma Apriori (numpy).

Input: daftar transaksi, tiap transaksi = himpunan productId.
Output: aturan "A (dan B) → C" dengan support, confidence, lift.

    support(X)       = jumlah transaksi yang memuat X / jumlah transaksi
    confidence(A→C)  = support(A ∪ C) / support(A)      "dari yang beli A, berapa % juga beli C"
    lift(A→C)        = confidence(A→C) / support(C)      > 1 : lebih sering bersama daripada kebetulan

Apriori: itemset hanya bisa sering muncul kalau semua subset-nya juga sering muncul,
jadi kandidat ukuran k dibangun dari itemset sering ukuran k-1 lalu dipangkas.
Pasangan (k=2) dihitung sekaligus lewat perkalian matriks T^T·T supaya tetap cepat
walau produknya ratusan.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

import numpy as np


@dataclass(frozen=True)
class Rule:
    antecedent: tuple[str, ...]
    consequent: str
    support: float
    confidence: float
    lift: float
    count: int


@dataclass(frozen=True)
class AprioriResult:
    rules: list[Rule]
    transactions: int
    items: int
    frequent_itemsets: int


def apriori(
    baskets: list[set[str]],
    min_support: float,
    min_confidence: float,
    min_lift: float,
    max_len: int = 3,
    max_rules: int = 300,
) -> AprioriResult:
    baskets = [b for b in baskets if b]
    n = len(baskets)
    if n == 0:
        return AprioriResult([], 0, 0, 0)

    items = sorted({i for b in baskets for i in b})
    index = {item: k for k, item in enumerate(items)}
    matrix = np.zeros((n, len(items)), dtype=np.uint8)
    for row, basket in enumerate(baskets):
        matrix[row, [index[i] for i in basket]] = 1

    min_count = max(2, int(np.ceil(min_support * n)))  # minimal 2 transaksi agar tidak "kebetulan satu kali"
    counts: dict[tuple[int, ...], int] = {}

    # k = 1
    single = matrix.sum(axis=0)
    frequent = [(k,) for k in range(len(items)) if single[k] >= min_count]
    for (k,) in frequent:
        counts[(k,)] = int(single[k])

    # k = 2: semua pasangan sekaligus
    if max_len >= 2 and len(frequent) >= 2:
        keep = [k for (k,) in frequent]
        sub = matrix[:, keep].astype(np.int32)
        pair = sub.T @ sub
        level = []
        for a in range(len(keep)):
            for b in range(a + 1, len(keep)):
                c = int(pair[a, b])
                if c >= min_count:
                    itemset = (keep[a], keep[b])
                    counts[itemset] = c
                    level.append(itemset)
        frequent = level
    else:
        frequent = []

    # k >= 3: gabung itemset yang prefix-nya sama, pangkas yang subset-nya tidak sering
    size = 3
    while size <= max_len and len(frequent) >= 2:
        current = set(frequent)
        candidates = set()
        for x, y in combinations(sorted(frequent), 2):
            if x[:-1] == y[:-1]:
                cand = tuple(sorted(set(x) | set(y)))
                if all(sub in current for sub in combinations(cand, size - 1)):
                    candidates.add(cand)
        level = []
        for cand in sorted(candidates):
            c = int(np.all(matrix[:, list(cand)], axis=1).sum())
            if c >= min_count:
                counts[cand] = c
                level.append(cand)
        frequent = level
        size += 1

    rules: list[Rule] = []
    for itemset, count in counts.items():
        if len(itemset) < 2:
            continue
        support = count / n
        for consequent in itemset:
            antecedent = tuple(k for k in itemset if k != consequent)
            confidence = count / counts[antecedent]
            lift = confidence / (counts[(consequent,)] / n)
            if confidence >= min_confidence and lift >= min_lift:
                rules.append(
                    Rule(
                        antecedent=tuple(items[k] for k in antecedent),
                        consequent=items[consequent],
                        support=round(support, 4),
                        confidence=round(confidence, 4),
                        lift=round(lift, 3),
                        count=count,
                    )
                )

    rules.sort(key=lambda r: (r.confidence * r.lift, r.count), reverse=True)
    return AprioriResult(rules=rules[:max_rules], transactions=n, items=len(items), frequent_itemsets=len(counts))
