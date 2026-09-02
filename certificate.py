# -*- coding: utf-8 -*-
"""Paper 9 integer-count certificate (sol P72_p9_r3 §3 / r5 §4): for each corpus and m, export the count tensors n_{g,f,y}, n_{g,f}, n_{g,z,y}, n_{g,z}
for Z and F_nested (base geometry, collapsed events), the nestedness table, the cross-product equality audit (n_gfy n_gz == n_gzy n_gf per supported cell),
the empirical oracle conditional mutual information I(Y;F|G,Z) computed from the counts, and SHA-256 hashes of the corpus TSV files and of this code.
Output: data/certificate/<corpus>_m<m>.json (tensors as lists of [g_id, f_id, y_id, count] with id tables) + certificate_summary.json.
  python -X utf8 certificate.py --m 1,2
"""
from __future__ import annotations
import argparse, collections, hashlib, json, math, sys
from pathlib import Path
H = Path(__file__).resolve().parent; D = H / "data"; OUT = D / "certificate"; OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(H))
import controls_r3 as C  # noqa: E402

CORP = ["ABC", "mozart_piano_sonatas", "beethoven_piano_sonatas"]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run(corpus, m):
    movs = C.load(corpus, True)
    rows = [r for _, mv in movs for r in C.build_rows(mv, m, C.trans_root, "nested", False)]
    gid, fid, zid, yid = {}, {}, {}, {}
    def idx(d, k):
        return d.setdefault(k, len(d))
    ngfy = collections.Counter(); ngf = collections.Counter(); ngzy = collections.Counter(); ngz = collections.Counter(); nest = collections.defaultdict(set)
    for ctx, y in rows:
        g = idx(gid, repr(ctx["geom"])); z = idx(zid, ctx["localrel"][1]); f = idx(fid, ctx["func"][1]); yy = idx(yid, repr(y))
        ngfy[(g, f, yy)] += 1; ngf[(g, f)] += 1; ngzy[(g, z, yy)] += 1; ngz[(g, z)] += 1; nest[f].add(z)
    N = len(rows)
    # nestedness: every F value maps to exactly one Z
    violations = {fk: sorted(zs) for fk, zs in nest.items() if len(zs) > 1}
    # cross-product audit and empirical CMI
    fz = {fk: next(iter(zs)) for fk, zs in nest.items() if len(zs) == 1}
    equal = 0; unequal = 0; cmi = 0.0
    for (g, f, y), c in ngfy.items():
        z = fz.get(f)
        if z is None:
            continue
        lhs = c * ngz[(g, z)]; rhs = ngzy[(g, z, y)] * ngf[(g, f)]
        equal += 1 if lhs == rhs else 0; unequal += 0 if lhs == rhs else 1
        cmi += (c / N) * math.log2((c / ngf[(g, f)]) / (ngzy[(g, z, y)] / ngz[(g, z)]))
    cert = dict(corpus=corpus, m=m, events=N, ids=dict(G=len(gid), F=len(fid), Z=len(zid), Y=len(yid)),
                nestedness=dict(F_values=len(nest), violations=len(violations), examples=dict(list(violations.items())[:5])),
                cross_product=dict(cells=equal + unequal, equal=equal, unequal=unequal), empirical_cmi_bits=round(cmi, 6),
                tensors=dict(n_gfy=[[g, f, y, c] for (g, f, y), c in sorted(ngfy.items())], n_gzy=[[g, z, y, c] for (g, z, y), c in sorted(ngzy.items())]),
                tables=dict(G=[k for k, _ in sorted(gid.items(), key=lambda kv: kv[1])], F=[k for k, _ in sorted(fid.items(), key=lambda kv: kv[1])], Z=[k for k, _ in sorted(zid.items(), key=lambda kv: kv[1])], Y=[k for k, _ in sorted(yid.items(), key=lambda kv: kv[1])]),
                provenance=dict(code_sha256={f.name: sha(f) for f in (H / "controls_r3.py", H / "corpora.py", H / "pilot_residue.py", H / "certificate.py")},
                                corpus_tsv_sha256={f.name: sha(f) for f in sorted((D / corpus / "harmonies").glob("*.tsv"))}))
    (OUT / ("%s_m%d.json" % (corpus, m))).write_text(json.dumps(cert), encoding="utf-8")
    summ = {k: cert[k] for k in ("corpus", "m", "events", "ids", "nestedness", "cross_product", "empirical_cmi_bits")}; summ["nestedness"] = {k: v for k, v in summ["nestedness"].items() if k != "examples"}
    print(summ, flush=True); return summ


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--m", default="1,2"); a = ap.parse_args()
    out = [run(c, m) for c in CORP for m in [int(x) for x in a.m.split(",")]]
    (D / "certificate_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
