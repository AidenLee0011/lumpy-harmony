# -*- coding: utf-8 -*-
"""Paper 9 manuscript build: figures from data/*.json + LaTeX (article class; venue template swap later) + tectonic + PII gate.
Numbers come only from the JSON results (no hand-typed values).  python -X utf8 build_paper.py [--no-compile]
"""
from __future__ import annotations
import json, os, subprocess, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
H = Path(__file__).resolve().parent; D = H / "data"; OUT = H / "paper"; FIG = OUT / "figs"
OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
J = lambda n: json.loads((D / n).read_text(encoding="utf-8"))
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False})

ctrl = J("controls_r3.json"); full = J("pilot_residue_full_backoff.json"); tr = J("transfer.json"); jz = J("jazz_contrast.json"); dec = J("residue_decompose.json")
rep = J("repair_lattice.json") if (D / "repair_lattice.json").exists() else None
nested = J("controls_r3_nested.json") if (D / "controls_r3_nested.json").exists() else {}
tso = J("transfer_sourceonly.json") if (D / "transfer_sourceonly.json").exists() else None

M = {"corpora": {c: full[c]["movements"] for c in full}, "full": {c: {m: {k: full[c][m][k] for k in ("n_eligible", "bits_per_chord", "gain_func_vs_keyrel", "gain_func_vs_localrel", "share_movements_positive")} for m in full[c] if m.startswith("m=")} for c in full},
     "controls": ctrl, "transfer": tr, "jazz": {k: v for k, v in jz.items()}, "decompose": {c: {m: dec[c][m]["residue_by_feature"] | {"full": dec[c][m]["residue_full_func"]} for m in dec[c] if m.startswith("m=")} for c in dec},
     "repair": [r["summary"] | {"corpus": r["corpus"], "m": r["m"], "target": r["target"]} for r in rep] if rep else None, "transfer_sourceonly": tso, "nested": nested, "lowo": J("lowo_headline.json") if (D / "lowo_headline.json").exists() else None, "lowo_nested": J("lowo_nested.json") if (D / "lowo_nested.json").exists() else None}
(OUT / "results_manifest.json").write_text(json.dumps(M, ensure_ascii=False, indent=1), encoding="utf-8")

VAR = ["base", "rootfree", "nocollapse", "fixedalpha", "target_nocur", "beta0.25", "beta4", "fullroman", "rootfree+fixedalpha+fullroman"]
LAB = {"base": "base", "rootfree": "root-free geometry", "nocollapse": "no event collapse", "fixedalpha": "fixed alphabet + UNK", "target_nocur": "target without current shape",
       "beta0.25": "smoothing beta 0.25", "beta4": "smoothing beta 4", "fullroman": "complete Roman label", "rootfree+fixedalpha+fullroman": "root-free + fixed + complete"}


def fig1():
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 3.0), sharey=True)
    for ax, corpus, title in zip(axs, ("beethoven_piano_sonatas", "ABC"), ("Beethoven piano sonatas", "Annotated Beethoven Corpus (quartets)")):
        y = list(range(len(VAR)))[::-1]
        for yi, v in zip(y, VAR):
            for m, mk in ((1, "o"), (2, "s")):
                r = ctrl["%s|m=%d|%s" % (corpus, m, v)]["residue"]; ax.plot(r, yi + (0.12 if m == 1 else -0.12), mk, color="black", mfc=("black" if m == 1 else "white"), ms=5)
        ax.axvline(0, color="grey", lw=0.8); ax.axvline(0.05, color="grey", lw=0.8, ls="--"); ax.set_yticks(y); ax.set_yticklabels([LAB[v] for v in VAR]); ax.set_title(title, fontsize=8)
        ax.set_xlabel("residue = L(local key content) - L(selective Roman), bits/chord\nfilled = m 1, open = m 2; dashed = 0.05")
    fig.savefig(FIG / "fig1_controls.pdf", bbox_inches="tight"); plt.close(fig)


def fig2():
    fig, ax = plt.subplots(figsize=(6.6, 2.4)); x = range(len(VAR)); w = 0.2
    for i, (corpus, col) in enumerate((("beethoven_piano_sonatas", "0.25"), ("ABC", "0.75"))):
        for j, m in enumerate((1, 2)):
            vals = [100 * ctrl["%s|m=%d|%s" % (corpus, m, v)]["pos_share"] for v in VAR]
            ax.bar([xi + (i * 2 + j - 1.5) * w for xi in x], vals, w, color=col, edgecolor="black", hatch=("" if m == 1 else "//"), label="%s m=%d" % ("sonatas" if i == 0 else "ABC", m))
    ax.axhline(70, color="grey", ls="--", lw=0.8); ax.set_xticks(list(x)); ax.set_xticklabels([LAB[v].replace(" ", "\n") for v in VAR], fontsize=6); ax.set_ylabel("% movements with positive residue"); ax.legend(frameon=False, fontsize=6, ncol=4)
    fig.savefig(FIG / "fig2_prevalence.pdf", bbox_inches="tight"); plt.close(fig)


def fig3():
    fig, ax = plt.subplots(figsize=(6.6, 2.6))
    feats = ["+relativeroot", "+spelled", "+applied_flag", "+numeral_case", "+changes", "+form", "+cadence", "+phraseend", "+figbass", "relabel3", "spelled3"]
    x = range(len(feats)); w = 0.38
    for j, (m, col) in enumerate((("m=1", "0.3"), ("m=2", "0.8"))):
        d = dec["beethoven_piano_sonatas"][m]["residue_by_feature"]; vals = [d.get(f, 0) for f in feats]
        ax.bar([xi + (j - 0.5) * w for xi in x], vals, w, color=col, edgecolor="black", label="sonatas " + m)
        ax.axhline(dec["beethoven_piano_sonatas"][m]["residue_full_func"], color=col, ls="--", lw=0.8)
    ax.axhline(0, color="black", lw=0.6); ax.set_xticks(list(x)); ax.set_xticklabels([f.replace("+", "") for f in feats], fontsize=6.5); ax.set_ylabel("residue recovered, bits/chord"); ax.legend(frameon=False, fontsize=7)
    ax.set_title("Which label content carries the sonata residue (dashed = selective Roman label)", fontsize=8)
    fig.savefig(FIG / "fig3_attribution.pdf", bbox_inches="tight"); plt.close(fig)


def fig4():
    if not rep:
        return
    fig, axs = plt.subplots(1, len(rep), figsize=(1.7 * len(rep), 2.6), squeeze=False)
    for ax, r in zip(axs[0], rep):
        s = r["summary"]; vals = [s["bits_per_chord"][k] for k in ("geom", "Z", "repair", "Fsel", "all5")]
        ax.bar(["geom", "Z", "repair", "F sel", "all 5"], vals, color=["0.9", "0.75", "0.4", "0.2", "0.6"], edgecolor="black")
        ax.set_title("%s\nm=%d %s  rho=%s" % (r["corpus"][:9], r["m"], r["target"], s["recovery_rho"]), fontsize=7); ax.tick_params(labelsize=6)
        ax.set_ylim(min(vals) - 0.3, max(vals) + 0.1)
    axs[0][0].set_ylabel("held-out bits/chord")
    fig.savefig(FIG / "fig4_repair.pdf", bbox_inches="tight"); plt.close(fig)


def fig5():
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.6), gridspec_kw={"width_ratios": [1.4, 1]})
    ax = axs[0]; keys = sorted(tr); y = list(range(len(keys)))[::-1]
    for yi, k in zip(y, keys):
        ax.plot(tr[k]["residue_func_vs_localrel"], yi, "o", color="black", ms=5)
        if tso and k in tso:
            ax.plot(tso[k]["residue_func_vs_localrel"], yi, "s", mfc="white", mec="black", ms=5)
    ax.axvline(0, color="grey", lw=0.8); ax.axvline(0.05, color="grey", ls="--", lw=0.8); ax.set_yticks(y); ax.set_yticklabels([k.replace("_piano_sonatas", "").replace("beethoven", "Beeth.").replace("mozart", "Moz.") for k in keys], fontsize=6.5)
    ax.set_xlabel("residue on target corpus (filled = adapted, open = source-only)")
    ax = axs[1]; styles = jz["m=2"]["per_style"]; names = sorted(styles, key=lambda s: -styles[s]["gain"])
    ax.barh(range(len(names))[::-1], [styles[s]["gain"] for s in names], color="0.6", edgecolor="black"); ax.set_yticks(list(range(len(names)))[::-1]); ax.set_yticklabels(names, fontsize=7)
    ax.axvline(0.5, color="grey", ls="--", lw=0.8); ax.set_xlabel("WJazzD: key-relative content gain over geometry, bits/chord (dashed = classical 0.5)")
    fig.savefig(FIG / "fig5_transfer_jazz.pdf", bbox_inches="tight"); plt.close(fig)


for f in (fig1, fig2, fig3, fig4, fig5):
    f()
sys.path.insert(0, str(H))
from paper_text import render  # noqa: E402
(OUT / "paper.tex").write_text(render(M), encoding="utf-8")
print("tex written")
if "--no-compile" not in sys.argv:
    tect = os.environ.get("TECTONIC", str(H.parents[1] / "paperops" / "bin" / "tectonic.exe"))
    r = subprocess.run([tect, "-X", "compile", "paper.tex"], cwd=str(OUT), capture_output=True, text=True); print("tectonic rc", r.returncode)
    if r.returncode:
        print(r.stderr[-1200:])
    pdf = OUT / "paper.pdf"
    if pdf.exists():
        sys.path.insert(0, str(H.parents[2]))
        from da_backend.paperops.iclr_review import dump_text
        txt = dump_text(pdf); import fitz  # noqa
        print("pages", fitz.open(str(pdf)).page_count, "chars", len(txt)); bad = [w for w in ("shlee", "cafe24", "@", "이성현", "win10") if w in txt]; print("PII gate:", "clean" if not bad else "FAIL %s" % bad)
