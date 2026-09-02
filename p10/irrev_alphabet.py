# -*- coding: utf-8 -*-
"""Paper 10 check 2 (sol P72_p10_r3 §2): alphabet-size matching. Restrict states to the top-k C12 inversion orbits by training mass (never split an orbit),
k in {25, 50, 67}; edges with an endpoint outside the alphabet are dropped from training and test; recompute held-out Delta_inv share and group LCB (alpha 0.5).
  python -X utf8 irrev_alphabet.py --source wjazzd|bach
"""
import argparse, collections, hashlib, json, math, statistics
from pathlib import Path
import irrev_bach as IB
from irrev_inversion import kappa, hfib
H = Path(__file__).resolve().parent


def orbit(s):
    return min(s, kappa(s))


def run(source, alpha=0.5):
    works = IB.load(source); grp = IB.groups(source, works)
    gids = sorted(set(grp.values()), key=lambda g: hashlib.sha256(g.encode()).hexdigest()); gfold = {g: i % 5 for i, g in enumerate(gids)}; fold = {w: gfold[grp[w]] for w in works}
    names = sorted(works); out = {"source": source, "k": {}}
    for k in (25, 50, 67, 175):
        sC = sD = sI = 0.0; N = 0; per = collections.defaultdict(lambda: [0.0, 0]); states_used = set()
        for f in range(5):
            trainseq = [works[w] for w in names if fold[w] != f]
            mass = collections.Counter(orbit(s) for seq in trainseq for s in seq)
            keep_orbits = [o for o, _ in sorted(mass.items(), key=lambda kv: (-kv[1], repr(kv[0])))]
            alphabet = set()
            for o in keep_orbits:
                members = {o, kappa(o)}
                if len(alphabet | members) > k:
                    break
                alphabet |= members
            states_used |= alphabet
            train = collections.Counter(e for seq in trainseq for e in IB.edges(seq) if e[0] in alphabet and e[1] in alphabet)
            keys = set(train) | {(j, i) for (i, j) in train}; Z = sum(train[e] + alpha for e in keys)
            def pC(e): return (train[e] + alpha) / Z if e in keys else alpha / Z
            fib = collections.defaultdict(float)
            for e in keys:
                fib[hfib(e)] += pC(e)
            def pD(e):
                ff = hfib(e); ke = (kappa(e[0]), kappa(e[1]))
                return fib[ff] if ff in fib else pC(e) + (pC(ke) if ke != e else 0.0)
            for w in names:
                if fold[w] != f:
                    continue
                for (i, j) in IB.edges(works[w]):
                    if i not in alphabet or j not in alphabet:
                        continue
                    sc = math.log2(pC((i, j)) / pC((j, i))); sd = math.log2(pD((i, j)) / pD((j, i)))
                    sC += sc; sD += sd; sI += sc - sd; N += 1; per[grp[w]][0] += sc - sd; per[grp[w]][1] += 1
        gi = [v[0] / v[1] for v in per.values() if v[1]]
        m = statistics.mean(gi); sd_ = statistics.stdev(gi); lcb = m - 1.96 * sd_ / math.sqrt(len(gi))
        out["k"][k] = dict(target_k=k, states_used=len(states_used), events=N, sigma_C=round(sC / N, 4), sigma_D=round(sD / N, 4), Delta_inv=round(sI / N, 4), share=round((sI / N) / (sC / N), 4), groups=len(gi), group_LCB95=round(lcb, 4))
        print(source, "k", k, out["k"][k], flush=True)
    (H / ("irrev_alphabet_%s.json" % source)).write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--source", default="wjazzd"); a = ap.parse_args(); run(a.source)
