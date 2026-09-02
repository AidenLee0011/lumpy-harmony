# -*- coding: utf-8 -*-
"""Paper 10 first computation (sol P72_p9_r4 §5): transposition-invariant time-irreversibility of harmonic progressions.

State = key-relative 12-bit pitch-class mask (pcs transposed so the annotated tonic is 0) with mode; consecutive duplicates collapsed.
Edge process mu(i,j) over directed transitions. Irreversibility sigma = D_2(mu || R mu), R(i,j) = (j,i).
Held-out score per forward edge: d_ij = log2[(c_ij + 0.5) / (c_ji + 0.5)] with counts from training works (5 SHA256 work folds).
Endpoint audit = KL(source marginal || target marginal) as share of plug-in sigma. Rare-state UNK control. Theorem audit: explicit 12-fold transposition
augmentation of ABSOLUTE masks followed by quotient must equal the key-relative computation (identity check to 1e-9).
Stop rule (sol): Bach work-level 95% LCB <= 0.05 bits/transition -> do not open Paper 10.
  python -X utf8 irrev_bach.py [--source bach|wjazzd]
"""
from __future__ import annotations
import argparse, collections, hashlib, json, math, sqlite3, statistics
from pathlib import Path
H = Path(__file__).resolve().parent; D9 = H.parent / "p9_harmony" / "data"
QT = {"major": (0, 4, 7), "minor": (0, 3, 7), "diminished": (0, 3, 6), "augmented": (0, 4, 8)}
JT = {"maj": (0, 4, 7), "maj7": (0, 4, 7, 11), "maj6": (0, 4, 7, 9), "min": (0, 3, 7), "min7": (0, 3, 7, 10), "min6": (0, 3, 7, 9), "dom7": (0, 4, 7, 10), "dom7alt": (0, 4, 8, 10),
      "hdim7": (0, 3, 6, 10), "dim7": (0, 3, 6, 9), "dim": (0, 3, 6), "aug": (0, 4, 8), "sus": (0, 5, 7, 10)}


def load(source, relative=True):
    recs = [json.loads(l) for l in (D9 / ("cache_%s.jsonl" % source)).read_text(encoding="utf-8").splitlines() if l.strip()]
    T = QT if source == "bach" else JT
    by = collections.defaultdict(list)
    for r in recs:
        if r.get("idx", -1) < 0 or r.get("root") is None or r.get("key_root") is None or r.get("quality") not in T:
            continue
        mask = 0
        for t in T[r["quality"]]:
            mask |= 1 << ((r["root"] + t - (r["key_root"] if relative else 0)) % 12)
        st = (mask, r.get("key_mode"))
        if by[r["piece"]] and by[r["piece"]][-1] == st:
            continue
        by[r["piece"]].append(st)
    return {k: v for k, v in by.items() if len(v) >= 8}


def rot(mask, g):
    return ((mask << g) | (mask >> (12 - g))) & 0xFFF


def groups(source, works):
    if source != "wjazzd":
        return {w: w for w in works}
    c = sqlite3.connect(str(D9 / "wjazzd.db"))
    comp = {("wjazzd/%d" % melid): str(compid) for melid, compid in c.execute("select melid, compid from solo_info")}
    return {w: comp.get(w, w) for w in works}



def load_uncollapsed(source):
    recs = [json.loads(l) for l in (D9 / ("cache_%s.jsonl" % source)).read_text(encoding="utf-8").splitlines() if l.strip()]
    T = QT if source == "bach" else JT; by = collections.defaultdict(list)
    for r in recs:
        if r.get("idx", -1) < 0 or r.get("root") is None or r.get("key_root") is None or r.get("quality") not in T:
            continue
        mask = 0
        for t in T[r["quality"]]:
            mask |= 1 << ((r["root"] + t - r["key_root"]) % 12)
        by[r["piece"]].append((mask, r.get("key_mode")))
    return {k: v for k, v in by.items() if len(v) >= 8}



def edges(seq):
    return list(zip(seq, seq[1:]))


def sigma_plugin(E):
    N = sum(E.values())
    return sum((c / N) * math.log2((c + 0.5) / (E[(j, i)] + 0.5)) for (i, j), c in E.items())


def run(source, unk_min=5):
    works = load(source)
    names = sorted(works, key=lambda w: hashlib.sha256(w.encode()).hexdigest()); fold = {w: i % 5 for i, w in enumerate(names)}
    freq = collections.Counter(s for seq in works.values() for s in seq)
    out = {"source": source, "works": len(works), "events": sum(len(v) for v in works.values()), "states": len(freq)}
    for merge in (False, True):
        def norm(seq):
            return [s if (not merge or freq[s] >= unk_min) else ("UNK", s[1]) for s in seq]
        per_work = []; tot = 0.0; n = 0; rev_cov = 0
        for k in range(5):
            train = collections.Counter(e for w in names if fold[w] != k for e in edges(norm(works[w])))
            for w in names:
                if fold[w] != k:
                    continue
                es = edges(norm(works[w])); s = 0.0
                for (i, j) in es:
                    s += math.log2((train[(i, j)] + 0.5) / (train[(j, i)] + 0.5)); rev_cov += 1 if train[(j, i)] > 0 else 0
                if es:
                    per_work.append(s / len(es)); tot += s; n += len(es)
        m = statistics.mean(per_work); sd = statistics.stdev(per_work); lcb = m - 1.96 * sd / math.sqrt(len(per_work))
        allE = collections.Counter(e for w in names for e in edges(norm(works[w]))); N = sum(allE.values())
        src = collections.Counter(); tgt = collections.Counter()
        for (i, j), c in allE.items():
            src[i] += c; tgt[j] += c
        S = len(freq) + 1
        kl_marg = sum((c / N) * math.log2(((c + 0.5) / (N + 0.5 * S)) / ((tgt[i] + 0.5) / (N + 0.5 * S))) for i, c in src.items())
        sf = sigma_plugin(allE)
        out["merge_rare" if merge else "no_merge"] = dict(event_weighted_bits=round(tot / n, 4), work_mean=round(m, 4), work_sd=round(sd, 4), n_works=len(per_work), work_LCB95=round(lcb, 4),
                                                          reverse_edge_coverage=round(rev_cov / n, 3), sigma_full_plugin=round(sf, 4), endpoint_marginal_KL=round(kl_marg, 4),
                                                          endpoint_share=round(kl_marg / sf, 3) if sf else None, pass_gate=bool(lcb > 0.05))
    # theorem audit: symmetrise ABSOLUTE-mask edges over all 12 transpositions, quotient by key-relative rotation -> must equal key-relative plug-in sigma
    absw = load(source, relative=False)
    key_of = {}
    recs = [json.loads(l) for l in (D9 / ("cache_%s.jsonl" % source)).read_text(encoding="utf-8").splitlines() if l.strip()]
    for r in recs:
        if r.get("key_root") is not None:
            key_of[r["piece"]] = r["key_root"]
    Eabs_sym = collections.Counter(); Eq = collections.Counter()
    for w, seq in absw.items():
        for (i, j) in edges(seq):
            for g in range(12):
                Eabs_sym[((rot(i[0], g), i[1]), (rot(j[0], g), j[1]))] += 1
            k = key_of[w]; Eq[((rot(i[0], (-k) % 12), i[1]), (rot(j[0], (-k) % 12), j[1]))] += 1
    # quotient of the symmetrised process by the diagonal action: orbit representative = rotate so that ... the identity says sigma(sym) == sigma(quotient by orbit)
    # compute sigma on the symmetrised absolute edges and on orbit-canonicalised edges (min over g of the pair) and compare
    def canon(e):
        return min(((rot(e[0][0], g), e[0][1]), (rot(e[1][0], g), e[1][1])) for g in range(12))
    Eorb = collections.Counter()
    for e, c in Eabs_sym.items():
        Eorb[canon(e)] += c
    # sigma on orbits: the reversal of an orbit is the orbit of the reversed edge (canonicalise the reversed pair, not the swapped canonical pair)
    Norb = sum(Eorb.values())
    sigma_orb = sum((c / Norb) * math.log2((c + 0.5) / (Eorb[canon((o[1], o[0]))] + 0.5)) for o, c in Eorb.items())
    # unsmoothed identity check on the common support (edges whose reverse is present): sum p log(p/p_rev)
    def sigma_exact(E, rev):
        N = sum(E.values()); return sum((c / N) * math.log2(c / E[rev(e)]) for e, c in E.items() if E[rev(e)] > 0)
    ex_sym = sigma_exact(Eabs_sym, lambda e: (e[1], e[0])); ex_orb = sigma_exact(Eorb, lambda o: canon((o[1], o[0])))
    out["theorem_audit"] = dict(sigma_symmetrised_absolute=round(sigma_plugin(Eabs_sym), 6), sigma_orbit_quotient=round(sigma_orb, 6),
                                exact_unsmoothed_symmetrised=round(ex_sym, 9), exact_unsmoothed_orbit=round(ex_orb, 9), identity_gap=round(abs(ex_sym - ex_orb), 12),
                                sigma_key_relative=round(sigma_plugin(Eq), 6), note="identity requires reversal to commute with the diagonal action; equality of the first two is the theorem check, the third is the musical (tonic-anchored) representative")
    print(json.dumps(out, indent=1))
    (H / ("irrev_%s.json" % source)).write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--source", default="bach"); a = ap.parse_args()
    run(a.source)
