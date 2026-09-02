# -*- coding: utf-8 -*-
"""Paper 10: what drives the irreversibility. Deterministic, zero LLM.
 (i) per-edge contributions to plug-in sigma, ranked, with readable key-relative chord names (root degree + quality)
 (ii) sigma restricted to edges with both directions present (coverage bias control)
 (iii) path irreversibility at depth 2: edges over state PAIRS (i,j)->(j,k) vs reversed (k,j)->(j,i)
 (iv) dihedral control: identify masks under inversion (pc -> -pc) as well as transposition
 (v) cycle affinities for the most frequent 3-cycles: A(i->j->k->i) = log2[c_ij c_jk c_ki / (c_ji c_kj c_ik)]
  python -X utf8 irrev_decompose.py --source bach|wjazzd
"""
from __future__ import annotations
import argparse, collections, itertools, json, math
from pathlib import Path
import irrev_bach as IB
H = Path(__file__).resolve().parent
NAMES = {(0, 4, 7): "maj", (0, 3, 7): "min", (0, 3, 6): "dim", (0, 4, 8): "aug", (0, 4, 7, 10): "7", (0, 4, 7, 11): "maj7", (0, 3, 7, 10): "m7", (0, 3, 6, 10): "m7b5", (0, 3, 6, 9): "dim7", (0, 4, 7, 9): "6", (0, 3, 7, 9): "m6", (0, 5, 7, 10): "sus", (0, 4, 8, 10): "7alt"}
DEG = {0: "I", 1: "bII", 2: "II", 3: "bIII", 4: "III", 5: "IV", 6: "#IV", 7: "V", 8: "bVI", 9: "VI", 10: "bVII", 11: "VII"}


def name(state):
    mask, mode = state
    if mask == "UNK":
        return "UNK"
    pcs = [p for p in range(12) if mask >> p & 1]
    for r in pcs:
        rel = tuple(sorted((p - r) % 12 for p in pcs))
        if rel in NAMES:
            return "%s:%s/%s" % (DEG[r], NAMES[rel], mode[:3])
    return "%s/%s" % ("".join(str(p) for p in pcs), mode[:3])


def run(source):
    works = IB.load(source)
    E = collections.Counter(e for seq in works.values() for e in IB.edges(seq)); N = sum(E.values())
    contrib = {e: (c / N) * math.log2((c + 0.5) / (E[(e[1], e[0])] + 0.5)) for e, c in E.items()}
    top = sorted(contrib.items(), key=lambda kv: -kv[1])[:20]
    both = {e: c for e, c in E.items() if E[(e[1], e[0])] > 0}; Nb = sum(both.values())
    sigma_both = sum((c / Nb) * math.log2(c / E[(e[1], e[0])]) for e, c in both.items())
    # depth-2 path irreversibility
    P2 = collections.Counter()
    for seq in works.values():
        for a, b, c in zip(seq, seq[1:], seq[2:]):
            P2[(a, b, c)] += 1
    N2 = sum(P2.values()); sigma2 = sum((c / N2) * math.log2((c + 0.5) / (P2[(k, j, i)] + 0.5)) for (i, j, k), c in P2.items())
    # dihedral: canonicalise mask under inversion (pc -> -pc mod 12) keeping the smaller code
    def inv(mask):
        return sum(1 << ((-p) % 12) for p in range(12) if mask >> p & 1)
    def dih(s):
        return (min(s[0], inv(s[0])) if s[0] != "UNK" else s[0], s[1])
    Ed = collections.Counter((dih(i), dih(j)) for seq in works.values() for (i, j) in IB.edges(seq)); Nd = sum(Ed.values())
    sigma_dih = sum((c / Nd) * math.log2((c + 0.5) / (Ed[(j, i)] + 0.5)) for (i, j), c in Ed.items())
    # 3-cycle affinities among the 12 most frequent states
    freq = collections.Counter(s for seq in works.values() for s in seq); S = [s for s, _ in freq.most_common(12)]
    cyc = []
    for i, j, k in itertools.permutations(S, 3):
        f = E[(i, j)] * E[(j, k)] * E[(k, i)]; b = E[(j, i)] * E[(k, j)] * E[(i, k)]
        if f > 0 and b > 0 and i < j and i < k:
            cyc.append((math.log2(f / b), f, b, "%s>%s>%s" % (name(i), name(j), name(k))))
    cyc.sort(key=lambda x: -abs(x[0]))
    out = dict(source=source, sigma_plugin=round(sum(contrib.values()), 4), sigma_both_directions_present=round(sigma_both, 4), share_edges_both=round(Nb / N, 3),
               sigma_depth2=round(sigma2, 4), sigma_dihedral=round(sigma_dih, 4), n_states=len(freq),
               top_edges=[dict(edge="%s -> %s" % (name(e[0]), name(e[1])), count=c, reverse=E[(e[1], e[0])], contribution_bits=round(v, 4)) for (e, v), c in zip(top, [E[e] for e, _ in top])],
               top_cycles=[dict(cycle=n, affinity_bits=round(a, 2), forward=f, backward=b) for a, f, b, n in cyc[:12]])
    print(json.dumps(out, indent=1)); (H / ("irrev_decompose_%s.json" % source)).write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--source", default="bach"); a = ap.parse_args(); run(a.source)
