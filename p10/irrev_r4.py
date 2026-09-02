# -*- coding: utf-8 -*-
"""Paper 10 round 4 (sol P72_p10_r3): (A) Schnakenberg circulation basis on the fitted stationary Markov chain with closure sigma = sum_C j_C A_C;
(B) named-loop contiguous path counts within works; (C) vocabulary-standardisation of the inversion share (inversion-closed chord families, common weights).
  python -X utf8 irrev_r4.py --source bach|wjazzd
"""
from __future__ import annotations
import argparse, collections, hashlib, json, math
import numpy as np
from pathlib import Path
import irrev_bach as IB
from irrev_inversion import kappa, hfib
H = Path(__file__).resolve().parent
NAMES = {(0, 4, 7): "maj", (0, 3, 7): "min", (0, 3, 6): "dim", (0, 4, 8): "aug", (0, 4, 7, 10): "7", (0, 4, 7, 11): "maj7", (0, 3, 7, 10): "m7", (0, 3, 6, 10): "m7b5", (0, 3, 6, 9): "dim7", (0, 4, 7, 9): "6", (0, 3, 7, 9): "m6", (0, 5, 7, 10): "sus", (0, 4, 8, 10): "7alt"}
DEG = {0: "I", 1: "bII", 2: "II", 3: "bIII", 4: "III", 5: "IV", 6: "#IV", 7: "V", 8: "bVI", 9: "VI", 10: "bVII", 11: "VII"}
FAMILY = {"maj": "triad", "min": "triad", "dim": "dim-aug", "aug": "dim-aug", "7": "dom7-hdim", "m7b5": "dom7-hdim", "maj7": "maj7-m6", "m6": "maj7-m6", "m7": "m7-6", "6": "m7-6", "dim7": "dim7", "sus": "sus", "7alt": "other"}


def parse(state):
    mask, mode = state
    if mask == "UNK":
        return None, None, mode
    pcs = [p for p in range(12) if mask >> p & 1]
    for r in pcs:
        rel = tuple(sorted((p - r) % 12 for p in pcs))
        if rel in NAMES:
            return r, NAMES[rel], mode
    return None, "other", mode


def name(state):
    r, q, mode = parse(state)
    return "%s:%s/%s" % (DEG[r], q, mode[:3]) if r is not None else "?/%s" % mode[:3]


def stationary(states, E):
    idx = {s: i for i, s in enumerate(states)}; n = len(states); T = np.full((n, n), 0.5)
    for (i, j), c in E.items():
        T[idx[i], idx[j]] += c
    T = T / T.sum(1, keepdims=True)
    w, v = np.linalg.eig(T.T); k = int(np.argmin(np.abs(w - 1))); pi = np.real(v[:, k]); pi = pi / pi.sum()
    return idx, T, pi


def circulation(source, works):
    E = collections.Counter(e for seq in works.values() for e in IB.edges(seq))
    states = sorted({s for e in E for s in e}, key=repr)
    idx, T, pi = stationary(states, E); n = len(states)
    F = pi[:, None] * T; J = F - F.T; A = np.log2(F / F.T)
    sigma = float(np.sum(F * A))                     # = sum_ij F_ij log2 F_ij/F_ji  (bits, stationary Markov fit)
    # maximum symmetric-traffic spanning forest (Kruskal on weight F_ij + F_ji, undirected), fundamental cycles from non-tree edges
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    und = sorted(((F[i, j] + F[j, i], i, j) for i in range(n) for j in range(i + 1, n)), key=lambda t: (-t[0], states[t[1]].__repr__(), states[t[2]].__repr__()))
    tree = set(); adj = collections.defaultdict(list)
    for w, i, j in und:
        if find(i) != find(j):
            parent[find(i)] = find(j); tree.add((i, j)); adj[i].append(j); adj[j].append(i)
    def path(a, b):
        prev = {a: None}; q = [a]
        while q:
            x = q.pop(0)
            if x == b:
                break
            for y in adj[x]:
                if y not in prev:
                    prev[y] = x; q.append(y)
        p = [b]
        while p[-1] != a:
            p.append(prev[p[-1]])
        return p[::-1]
    cyc = []
    for i in range(n):
        for j in range(n):
            if i < j and (i, j) not in tree and (j, i) not in tree and (F[i, j] + F[j, i]) > 0:
                # fundamental cycle: chord i->j then tree path j->...->i ; circulation coefficient = net current on the chord edge J_ij
                p = path(j, i); loop = [(i, j)] + list(zip(p, p[1:]))
                Ac = float(sum(A[a, b] for a, b in loop)); jc = float(J[i, j])
                cyc.append(dict(chord=(states[i], states[j]), loop=[name(states[a]) for a, b in loop] + [name(states[loop[-1][1]])], j_C=jc, A_C=Ac, term=jc * Ac))
    total = sum(c["term"] for c in cyc)
    # exact algebra: sigma = sum_ij F_ij A_ij = (1/2) sum_ij J_ij A_ij; with tree currents determined by chord currents, sum_C j_C A_C reproduces sigma when
    # every undirected pair is either a tree edge or a chord (holds for connected support). Report closure.
    cyc.sort(key=lambda c: -abs(c["term"]))
    return dict(states=n, sigma_stationary_bits=round(sigma, 6), sum_jA=round(total, 6), closure_err=round(abs(sigma - total), 9), n_cycles=len(cyc),
                top10_share=round(sum(c["term"] for c in cyc[:10]) / sigma, 4) if sigma else None, top5_share=round(sum(c["term"] for c in cyc[:5]) / sigma, 4) if sigma else None,
                top=[dict(loop=">".join(c["loop"]), j_C=round(c["j_C"], 6), A_C=round(c["A_C"], 3), term_bits=round(c["term"], 5), share=round(c["term"] / sigma, 4)) for c in cyc[:12]])


def named_loops(source, works):
    loops = {"bach": [("i>iv>V>i", [("I", "min", "minor"), ("IV", "min", "minor"), ("V", "maj", "minor"), ("I", "min", "minor")]), ("I>IV>V>I", [("I", "maj", "major"), ("IV", "maj", "major"), ("V", "maj", "major"), ("I", "maj", "major")]), ("I>ii>V>I", [("I", "maj", "major"), ("II", "min", "major"), ("V", "maj", "major"), ("I", "maj", "major")])],
             "wjazzd": [("Imaj7>ii7>V7>Imaj7", [("I", "maj7", "major"), ("II", "m7", "major"), ("V", "7", "major"), ("I", "maj7", "major")]), ("Imaj7>II7>V7>Imaj7", [("I", "maj7", "major"), ("II", "7", "major"), ("V", "7", "major"), ("I", "maj7", "major")]), ("Imaj7>vi7>ii7>V7", [("I", "maj7", "major"), ("VI", "m7", "major"), ("II", "m7", "major"), ("V", "7", "major")])]}[source]
    def key(s):
        r, q, mode = parse(s); return (DEG.get(r), q, mode)
    out = {}
    for lab, pat in loops:
        fwd = bwd = 0; works_f = 0
        for seq in works.values():
            ks = [key(s) for s in seq]; f0 = 0
            for t in range(len(ks) - 3):
                w = tuple(ks[t:t + 4])
                if w == tuple(pat):
                    fwd += 1; f0 += 1
                if w == tuple(pat[::-1]):
                    bwd += 1
            works_f += 1 if f0 else 0
        out[lab] = dict(forward=fwd, reverse=bwd, works_with_forward=works_f, log2_ratio=round(math.log2((fwd + 0.5) / (bwd + 0.5)), 3))
    return out


def vocab_standardisation(source, works, alpha=0.5):
    """held-out per-event delta_inv and s_C by inversion-closed endpoint-family stratum (unordered), for common-weight standardisation across corpora"""
    grp = IB.groups(source, works); gids = sorted(set(grp.values()), key=lambda g: hashlib.sha256(g.encode()).hexdigest()); gfold = {g: i % 5 for i, g in enumerate(gids)}
    fold = {w: gfold[grp[w]] for w in works}; names = sorted(works)
    strat = collections.defaultdict(lambda: [0.0, 0.0, 0])
    for k in range(5):
        train = collections.Counter(e for w in names if fold[w] != k for e in IB.edges(works[w]))
        keys = set(train) | {(j, i) for (i, j) in train}; Z = sum(train[e] + alpha for e in keys)
        def pC(e): return (train[e] + alpha) / Z if e in keys else alpha / Z
        fib = collections.defaultdict(float)
        for e in keys:
            fib[hfib(e)] += pC(e)
        def pD(e):
            f = hfib(e); ke = (kappa(e[0]), kappa(e[1]))
            return fib[f] if f in fib else pC(e) + (pC(ke) if ke != e else 0.0)
        for w in names:
            if fold[w] != k:
                continue
            for (i, j) in IB.edges(works[w]):
                sc = math.log2(pC((i, j)) / pC((j, i))); sd = math.log2(pD((i, j)) / pD((j, i)))
                fa = FAMILY.get(parse(i)[1], "other"); fb = FAMILY.get(parse(j)[1], "other"); s = "|".join(sorted((fa, fb)))
                strat[s][0] += sc - sd; strat[s][1] += sc; strat[s][2] += 1
    N = sum(v[2] for v in strat.values())
    return {s: dict(p=round(v[2] / N, 4), mu_delta=round(v[0] / v[2], 4), mu_C=round(v[1] / v[2], 4), n=v[2]) for s, v in strat.items()}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--source", default="bach"); a = ap.parse_args()
    works = IB.load(a.source)
    out = dict(source=a.source, circulation=circulation(a.source, works), named_loops=named_loops(a.source, works), vocab_strata=vocab_standardisation(a.source, works))
    (H / ("irrev_r4_%s.json" % a.source)).write_text(json.dumps(out, indent=1), encoding="utf-8")
    c = out["circulation"]; print(a.source, "stationary sigma", c["sigma_stationary_bits"], "sum jA", c["sum_jA"], "closure", c["closure_err"], "cycles", c["n_cycles"], "top5 share", c["top5_share"], "top10", c["top10_share"])
    for t in c["top"][:6]: print("  ", t)
    print("  named loops", out["named_loops"])
    print("  strata", {k: (v["p"], v["mu_delta"], v["mu_C"]) for k, v in sorted(out["vocab_strata"].items(), key=lambda kv: -kv[1]["p"])[:8]})
