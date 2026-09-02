# -*- coding: utf-8 -*-
"""Paper 9 / STANDARDS §30 rule 4: machine-check that the refinement F determines the baseline Z on every observed label combination.
Z = (chromatic local root degree, chord type, local mode); F_nested = (numeral, relativeroot, mode, chord type); F_sel = (numeral, mode, chord type).
Prints counterexamples (label combinations mapping to >1 Z value). Output data/nesting_check.json.
"""
import collections, json, sys
from pathlib import Path
import pandas as pd
H = Path(__file__).resolve().parent; D = H / "data"
sys.path.insert(0, str(H))
from corpora import _dcml_key, _roman_to_pc  # noqa: E402
from pilot_residue import fifths_to_pc  # noqa: E402

out = {}
for corpus in ("ABC", "mozart_piano_sonatas", "beethoven_piano_sonatas"):
    maps = {"F_nested": collections.defaultdict(set), "F_sel": collections.defaultdict(set)}
    n = 0
    for f in sorted((D / corpus / "harmonies").glob("*.tsv")):
        df = pd.read_csv(f, sep="\t", low_memory=False); gk, gmode = _dcml_key(df["globalkey"].iloc[0])
        for _, r in df.iterrows():
            numeral = r.get("numeral"); lk = r.get("localkey")
            if not isinstance(numeral, str) or not isinstance(lk, str) or gk is None or str(r.get("root")) in ("nan", ""):
                continue
            lk_pc = _roman_to_pc(lk, gk, gmode)
            if lk_pc is None:
                continue
            root = (lk_pc + fifths_to_pc(r.get("root"))) % 12; lmode = "m" if bool(r.get("localkey_is_minor")) else "M"
            Z = ((root - lk_pc) % 12, str(r.get("chord_type")), lmode)
            maps["F_nested"][(numeral, str(r.get("relativeroot")), lmode, str(r.get("chord_type")))].add(Z)
            maps["F_sel"][(numeral, lmode, str(r.get("chord_type")))].add(Z)
            n += 1
    res = {"events": n}
    for k, mp in maps.items():
        bad = {str(key): sorted(str(z) for z in zs) for key, zs in mp.items() if len(zs) > 1}
        res[k] = {"label_combinations": len(mp), "counterexamples": len(bad), "examples": dict(list(bad.items())[:5])}
    out[corpus] = res
    print(corpus, "events", n, "F_nested counterexamples", res["F_nested"]["counterexamples"], "/", res["F_nested"]["label_combinations"], "| F_sel counterexamples", res["F_sel"]["counterexamples"], "/", res["F_sel"]["label_combinations"])
(D / "nesting_check.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
