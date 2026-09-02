# -*- coding: utf-8 -*-
"""Paper 10 manuscript build: figures from irrev_*.json + LaTeX (two-part structure, sol P72_p10_r3 §3) + tectonic + PII gate. Numbers only from JSON.
  python -X utf8 build_paper.py [--no-compile]
"""
from __future__ import annotations
import json, os, subprocess, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
H = Path(__file__).resolve().parent; OUT = H / "paper"; FIG = OUT / "figs"; OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
J = lambda n: json.loads((H / n).read_text(encoding="utf-8"))
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False})
S = {"bach": J("irrev_bach.json"), "wjazzd": J("irrev_wjazzd.json")}
SUP = {"bach": J("irrev_support_bach.json"), "wjazzd": J("irrev_support_wjazzd.json")}
SUPU = {c: J("irrev_support_%s_uncollapsed.json" % c) for c in ("bach", "wjazzd") if (H / ("irrev_support_%s_uncollapsed.json" % c)).exists()}
INV = {"bach": J("irrev_inversion_bach.json"), "wjazzd": J("irrev_inversion_wjazzd.json")}
INVU = {c: J("irrev_inversion_%s_uncollapsed.json" % c) for c in ("bach", "wjazzd")}
DEC = {"bach": J("irrev_decompose_bach.json"), "wjazzd": J("irrev_decompose_wjazzd.json")}
R4 = {c: J("irrev_r4_%s.json" % c) for c in ("bach", "wjazzd") if (H / ("irrev_r4_%s.json" % c)).exists()}
VS = J("irrev_vocab_std.json") if (H / "irrev_vocab_std.json").exists() else None
ALPH = {a: {c: J("irrev_alphabet_%s_a%s.json" % (c, a)) for c in ("bach", "wjazzd")} for a in ("0.1", "0.5", "1") if (H / ("irrev_alphabet_bach_a%s.json" % a)).exists()}
MODE = J("irrev_mode.json") if (H / "irrev_mode.json").exists() else None
M = dict(S=S, SUP=SUP, SUPU=SUPU, INV=INV, INVU=INVU, DEC=DEC, R4=R4, VS=VS, ALPH=ALPH, MODE=MODE)
(OUT / "results_manifest.json").write_text(json.dumps(M, indent=1), encoding="utf-8")
LAB = {"bach": "Bach chorales", "wjazzd": "WJazzD"}


def fig_decomp():
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.6))
    for ax, c in zip(axs, ("bach", "wjazzd")):
        al = ["0.1", "0.5", "1"]; sC = [INV[c]["alpha"][a]["sigma_C"] for a in al]; sD = [INV[c]["alpha"][a]["sigma_D"] for a in al]; dI = [INV[c]["alpha"][a]["Delta_inv"] for a in al]
        x = range(3); ax.bar(x, sD, 0.6, color="0.7", edgecolor="black", label=r"$\sigma_{D_{12}}$ (inversion-invariant)"); ax.bar(x, dI, 0.6, bottom=sD, color="0.25", edgecolor="black", label=r"$\Delta_{\mathrm{inv}}$ (inversion-resolving)")
        for i in x: ax.text(i, sC[i] + 0.02, "%.3f" % sC[i], ha="center", fontsize=7)
        ax.set_xticks(list(x)); ax.set_xticklabels([r"$\alpha$=%s" % a for a in al]); ax.set_title(LAB[c], fontsize=8); ax.set_ylabel("held-out bits per transition")
    axs[0].legend(frameon=False, fontsize=6.5); fig.savefig(FIG / "fig3_decomposition.pdf", bbox_inches="tight"); plt.close(fig)


def fig_lcb():
    fig, ax = plt.subplots(figsize=(6.6, 2.4)); y = 0
    for c in ("bach", "wjazzd"):
        for a in ("0.1", "0.5", "1"):
            r = INV[c]["alpha"][a]; ax.errorbar(r["group_mean"], y, xerr=[[r["group_mean"] - r["group_LCB95"]], [0]], fmt="o", color="black", capsize=2); ax.text(-0.05, y, "%s a=%s" % (LAB[c][:5], a), ha="right", va="center", fontsize=7); y += 1
        for a in ("0.5",):
            r = INVU[c]["alpha"][a]; ax.errorbar(r["group_mean"], y, xerr=[[r["group_mean"] - r["group_LCB95"]], [0]], fmt="s", mfc="white", color="black", capsize=2); ax.text(-0.05, y, "%s a=%s uncollapsed" % (LAB[c][:5], a), ha="right", va="center", fontsize=7); y += 1
    ax.axvline(0.10, color="grey", ls="--", lw=0.8); ax.axvline(0, color="grey", lw=0.6); ax.set_yticks([]); ax.set_xlabel(r"group-level $\Delta_{\mathrm{inv}}$ mean with 95% interval lower endpoint (bits per transition); dashed = pre-specified 0.10")
    fig.savefig(FIG / "fig4_lcb.pdf", bbox_inches="tight"); plt.close(fig)


def fig_support():
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.4))
    for ax, c in zip(axs, ("bach", "wjazzd")):
        for a, mk in (("0.1", "o"), ("0.5", "s"), ("1", "^")):
            rs = [SUP[c]["results"]["alpha=%s|r=%d" % (a, r)] for r in (0, 1, 2, 5)]
            ax.plot([0, 1, 2, 5], [x["retained_total"] for x in rs], marker=mk, color="black", mfc="white", label=r"retained-total $\alpha$=%s" % a)
            ax.plot([0, 1, 2, 5], [x["conditional"] for x in rs], marker=mk, color="0.5", ls="--", label=r"conditional $\alpha$=%s" % a if a == "0.5" else None)
        ax.set_xticks([0, 1, 2, 5]); ax.set_xticklabels(["all", "r=1", "r=2", "r=5"]); ax.set_title(LAB[c], fontsize=8); ax.set_ylabel("bits per transition")
    axs[1].legend(frameon=False, fontsize=6); fig.savefig(FIG / "fig2_support.pdf", bbox_inches="tight"); plt.close(fig)


def fig_edges():
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.8))
    for ax, c in zip(axs, ("bach", "wjazzd")):
        top = DEC[c]["top_edges"][:10]; y = list(range(len(top)))[::-1]
        ax.barh(y, [t["contribution_bits"] for t in top], color="0.6", edgecolor="black"); ax.set_yticks(y); ax.set_yticklabels(["%s (%d:%d)" % (t["edge"].replace("/maj", "").replace("/min", "m"), t["count"], t["reverse"]) for t in top], fontsize=6)
        ax.set_title(LAB[c] + ": top directed edges (forward:reverse counts)", fontsize=8); ax.set_xlabel("plug-in contribution to sigma, bits")
    fig.savefig(FIG / "fig5_edges.pdf", bbox_inches="tight"); plt.close(fig)


def fig_cycles():
    if not R4:
        return
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.8))
    for ax, c in zip(axs, ("bach", "wjazzd")):
        top = R4[c]["circulation"]["top"][:8]; y = list(range(len(top)))[::-1]
        ax.barh(y, [t["term_bits"] for t in top], color="0.5", edgecolor="black"); ax.set_yticks(y); ax.set_yticklabels([t["loop"].replace("/maj", "").replace("/min", "m")[:48] for t in top], fontsize=5.5)
        ax.set_title("%s: fundamental-cycle terms $j_C A_C$ (top-5 share %.0f%%)" % (LAB[c], 100 * R4[c]["circulation"]["top5_share"]), fontsize=7.5); ax.set_xlabel("bits per transition (stationary fit)")
    fig.savefig(FIG / "fig6_cycles.pdf", bbox_inches="tight"); plt.close(fig)


def fig_controls():
    if not ALPH or not MODE:
        return
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.5))
    ax = axs[0]
    for c, mk in (("bach", "o"), ("wjazzd", "s")):
        for a, col in (("0.1", "0.3"), ("0.5", "0.55"), ("1", "0.8")):
            ks = sorted(int(k) for k in ALPH[a][c]["k"]); ax.plot(ks, [100 * ALPH[a][c]["k"][str(k)]["share"] for k in ks], marker=mk, color=col, mfc="white" if c == "wjazzd" else col, label="%s a=%s" % (LAB[c][:5], a))
    ax.set_xlabel("matched alphabet size k (complete inversion fibers)"); ax.set_ylabel(r"$\bar\delta_{\mathrm{inv}}$ share of score (%)"); ax.set_title("alphabet matching", fontsize=8); ax.legend(frameon=False, fontsize=5.5, ncol=2)
    ax = axs[1]; x = 0; lab = []
    for c in ("bach", "wjazzd"):
        r = MODE["alpha"]["0.5"]["corpora"][c]
        vals = [r["by_mode"]["major"]["share"], r["by_mode"]["minor"]["share"], r["observed"]["share"], r["common_weighted"]["share"]]
        ax.bar([x + i for i in range(4)], [100 * v for v in vals], color=["0.85", "0.4", "0.6", "0.2"], edgecolor="black"); lab += [("%s\n%s") % (LAB[c][:5], t) for t in ("major", "minor", "obs.", "common\nweights")]; x += 5
    ax.set_xticks([i for i in range(9) if i != 4]); ax.set_xticklabels(lab, rotation=0, fontsize=5.5); ax.set_ylabel("share (%)"); ax.set_title(r"mode composition ($\alpha=0.5$)", fontsize=8)
    fig.savefig(FIG / "fig7_controls.pdf", bbox_inches="tight"); plt.close(fig)


for f in (fig_decomp, fig_lcb, fig_support, fig_edges, fig_cycles, fig_controls):
    f()
sys.path.insert(0, str(H))
from paper_text import render  # noqa: E402
(OUT / "paper.tex").write_text(render(M), encoding="utf-8"); print("tex written")
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
