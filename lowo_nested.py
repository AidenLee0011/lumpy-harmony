# -*- coding: utf-8 -*-
"""Paper 9: leave-one-WORK-out primary nested analysis (panel v3 fix): residue L(Z) - L(F_nested) with works held out, base and clean targets, m=1,2.
  python -X utf8 lowo_nested.py
"""
import collections, json, re, statistics, sys
from pathlib import Path
H = Path(__file__).resolve().parent; D = H / "data"
sys.path.insert(0, str(H))
import controls_r3 as C
import repair_lattice as R

CORP = ["beethoven_piano_sonatas", "ABC", "mozart_piano_sonatas"]


def work_of(corpus, stem):
    return re.split(r"[-_]", stem)[0] if corpus != "ABC" else (re.sub(r"_?\d+$", "", stem.rsplit("_", 1)[0]) if "_" in stem else stem[:6])


def run(corpus, m, target):
    movs = C.load(corpus, True)
    tf = C.trans_rootfree if target == "clean" else C.trans_root
    rows = {stem: C.build_rows(mv, m, tf, "nested", target == "clean") for stem, mv in movs}
    groups = collections.defaultdict(list)
    for stem in rows:
        groups[work_of(corpus, stem)].append(stem)
    tot = collections.Counter(); N = 0; per = []
    for w, members in groups.items():
        train = [r for s2 in rows if work_of(corpus, s2) != w for r in rows[s2]]
        alpha = {y for _, y in train}
        L = collections.Counter(); n = 0
        for s in members:
            test = rows[s]
            for key in ("geom", "localrel", "func"):
                L[key] += C.code(train, test, key, 1.0, target == "clean")
            n += len(test)
        for key in L:
            tot[key] += L[key]
        N += n; per.append((L["localrel"] - L["func"]) / max(n, 1))
    return dict(corpus=corpus, m=m, target=target, works=len(groups), N=N, bits={k: round(v / N, 4) for k, v in tot.items()}, residue_nested=round((tot["localrel"] - tot["func"]) / N, 4),
                works_positive=round(sum(1 for x in per if x > 0) / len(per), 3), work_mean=round(statistics.mean(per), 4), work_sd=round(statistics.stdev(per), 4))


if __name__ == "__main__":
    out = []
    for c in CORP:
        for m in (1, 2):
            for t in ("base", "clean"):
                r = run(c, m, t); out.append(r); print(c, "m=%d" % m, t, "nested residue", r["residue_nested"], "works+", r["works_positive"], "works", r["works"], flush=True)
    (D / "lowo_nested.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
