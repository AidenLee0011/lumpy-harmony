# -*- coding: utf-8 -*-
"""Apply sol P72_p9_r5 §3 edits 1-8 to paper_text.py and wire the nested table into build_paper.py."""
import pathlib
H = pathlib.Path(__file__).resolve().parent
B = chr(92); P = chr(37)
# ---- build_paper: load nested controls into the manifest
b = (H / "build_paper.py").read_text(encoding="utf-8")
if "controls_r3_nested" not in b:
    b = b.replace('rep = J("repair_lattice.json") if (D / "repair_lattice.json").exists() else None',
                  'rep = J("repair_lattice.json") if (D / "repair_lattice.json").exists() else None\nnested = J("controls_r3_nested.json") if (D / "controls_r3_nested.json").exists() else {}')
    b = b.replace('"transfer_sourceonly": tso}', '"transfer_sourceonly": tso, "nested": nested}')
    (H / "build_paper.py").write_text(b, encoding="utf-8")
# ---- paper_text
s = (H / "paper_text.py").read_text(encoding="utf-8")
def rep(a, c):
    global s
    assert a in s, a[:80]
    s = s.replace(a, c, 1)
rep(B + "title{Roman-Numeral Information Beyond Local Chord Content: Predictive Sufficiency and a Failed Preregistered Repair}",
    B + "title{Approximate Predictive Sufficiency of Local Chord Content: Roman Function as Applied-Chord Lumping and a Failed Preregistered MDL Repair}")
# abstract
i = s.index(B + "begin{abstract}"); j = s.index(B + "end{abstract}")
abstract = B + "begin{abstract}" + chr(10) + (
 "Roman-numeral labels combine local chord content with functional category choices. We test, on the observed annotations of the Beethoven piano sonatas, the Annotated Beethoven Corpus quartets and the Mozart piano sonatas, whether $Z=(" + B + "text{chromatic relative root}," + B + "text{mode}," + B + "text{chord type})$ is operationally sufficient under a fixed prequential code at context depths $m=1,2$. "
 "The genuine refinement $F_{" + B + "mathrm{nested}}=(" + B + "text{numeral}," + B + "text{relative root}," + B + "text{mode}," + B + "text{chord type})$ deterministically contains $Z$. Across the base, root-free fixed-alphabet and clean-target analyses the residue $" + B + "Delta=L(Z)-L(F_{" + B + "mathrm{nested}})$ never exceeds %(nmax)s bits per chord: the Beethoven sonatas at $m=1$ give %(nS1a)s to %(nS1c)s with %(nS1p)s to %(nS1q)s" + B + "%% of movements positive, while every ABC and Mozart value is at most %(nother)s. All three corpora therefore meet our operational $" + B + "Delta" + B + "le 0.05$ criterion, with the Beethoven sonatas at the threshold at $m=1$. "
 "A selective label $F_{" + B + "mathrm{sel}}=(" + B + "text{numeral}," + B + "text{mode}," + B + "text{chord type})$ is not nested, because it groups applied dominants by function; its Beethoven contrast is %(s1)s/%(s2)s bits per chord, and relabelling only the applied chords by functional degree recovers %(rl1)s/%(rl2)s, or %(rlp1)s" + B + "%%/%(rlp2)s" + B + "%%, identifying a functional-lumping contribution rather than a nested syntax gain. A preregistered five-feature MDL repair of that contrast failed its joint recovery and stability rule. An integer-count certificate audits the mappings, folds and reported code lengths. All conclusions are restricted to these annotations, representations and coding protocols." + chr(10))
s = s[:i] + abstract + s[j:]
# section 1 framing
i = s.index(B + "section{The representation question}"); j = s.index(B + "section{States, targets and quotients}")
sec1 = B + "section{The representation question}" + chr(10) + (
 "Two traditions describe tonal harmony: geometric accounts locate chords in voice-leading spaces (Tymoczko, 2006; Callender, Quinn and Tymoczko, 2008), functional accounts describe progressions with key-relative Roman labels (Rohrmeier, 2011). "
 "A predictive sufficiency comparison between them is valid only when the richer representation is a genuine refinement of the baseline. Our primary question is therefore whether the local-content state $Z$ is operationally sufficient, at a threshold of $0.05$ bits per chord, relative to a Roman representation that deterministically contains $Z$. "
 "Our secondary question concerns a different object: the selective label $F_{" + B + "mathrm{sel}}$, which does not contain the chromatic relative root and instead re-partitions applied chords by function; its code gain cannot be interpreted through the nested sufficiency proposition, so we analyse it as a representation effect and ask how much of the displayed contrast is recovered by functional relabelling of applied chords. "
 "Finally we report the confirmatory failure of a preregistered MDL repair intended to approximate that selective-label contrast. The contributions are the corrected nested measurement, the same-arity applied-chord attribution, the preregistered negative result and an auditable integer-count certificate. The original hypothesis of this study, a substantial Roman residue beyond a strong tonal baseline, was preregistered at $0.05$ bits per chord and failed." + chr(10) + chr(10))
s = s[:i] + sec1 + s[j:]
# definition of F
i = s.index(B + "begin{definition}[contexts]"); j = s.index(B + "end{definition}") + len(B + "end{definition}")
defn = (B + "begin{definition}[contexts]" + chr(10) +
 "$G_t=O_m(t)$ is the tuple of the previous $m$ transitions (geometry). $K_t$ adds the root scale degree in the " + B + "emph{global} key, chord type and global mode. Let $Z_t=(r_t," + B + "mu_t," + B + "tau_t)$ with $r_t$ the chromatic root degree relative to the local tonic, $" + B + "mu_t$ the local mode and $" + B + "tau_t$ the chord type. The genuine refinement is $F_{" + B + "mathrm{nested},t}=(" + B + "nu_t," + B + "rho_t," + B + "mu_t," + B + "tau_t)$ with $" + B + "nu_t$ the numeral and $" + B + "rho_t$ the relative root; the projection $h(" + B + "nu," + B + "rho," + B + "mu," + B + "tau)=(r," + B + "mu," + B + "tau)$ recovers $Z_t$, so the sufficiency proposition applies. Separately, $F_{" + B + "mathrm{sel},t}=(" + B + "nu_t," + B + "mu_t," + B + "tau_t)$: no function recovers $Z_t$ from it (an applied $V/V$ has numeral $V$ but relative root degree $2$), so $F_{" + B + "mathrm{sel}}$ is a non-nested re-partition of $Z$ and $L(Z)-L(F_{" + B + "mathrm{sel}})$ is reported only as a coding contrast. The target $Y_t$ is the next transition; the " + B + "emph{no-current-shape} target keeps only the root shift and the displacement cost." + chr(10) + B + "end{definition}")
s = s[:i] + defn + s[j:]
rep("$Z$ is a deterministic function of the label content, $Z=h(F)$, so $F$ refines $Z$.", "$Z=h(F_{" + B + "mathrm{nested}})$ holds on every observed label combination (machine-checked; zero counterexamples); it does not hold for $F_{" + B + "mathrm{sel}}$.")
# headline table: insert nested Table 1 before the full-corpora table
anchor = B + "begin{table}[t]" + B + "centering" + B + "small" + chr(10) + B + "caption{Full corpora, root-anchored geometry"
nested_tbl = (B + "begin{table}[t]" + B + "centering" + B + "small" + chr(10) + B + "caption{Corrected nested comparison. Each entry is $" + B + "Delta=L(Z)-L(F_{" + B + "mathrm{nested}})$ in bits per chord, followed by the share of movements with positive residue. The maximum observed nested residue is %(nmax)s; all rows meet the operational $" + B + "Delta" + B + "le0.05$ criterion. Small negative finite-code contrasts do not contradict the oracle inequality.}" + B + "label{tab:nested}" + chr(10) +
 B + "begin{tabular}{llrrr}" + B + "toprule corpus & $m$ & base nested & root-free + fixed alphabet & clean target " + B + B + " " + B + "midrule" + chr(10) + "%(nested_rows)s" + chr(10) + B + "bottomrule" + B + "end{tabular}" + B + "end{table}" + chr(10) + chr(10))
rep(anchor, nested_tbl + anchor)
# same-arity paragraph
i = s.index(B + "section{What carries the residue}"); j = s.index(B + "begin{figure}[t]" + B + "centering" + B + "includegraphics[width=" + B + "linewidth]{figs/fig3_attribution.pdf}")
para = (B + "section{What the selective-label contrast is}" + chr(10) +
 "The tuple (numeral, chord type, mode), at the same arity as $Z$, reproduces the Beethoven selective contrasts of %(s1)s/%(s2)s bits per chord exactly (%(sp1)s and %(sp2)s). This tuple is not a refinement of $Z$: it groups applied dominants onto their functional numeral while retaining spelled alterations elsewhere. Relabelling only the applied chords by functional degree, again at the same arity, yields gains of %(rl1)s/%(rl2)s bits per chord, equal to %(rlp1)s" + B + "%%/%(rlp2)s" + B + "%% of the full selective contrast; the remaining %(rlrest1)s/%(rlrest2)s bits are not explained by this operation. Adding single complete-label fields on top of $Z$ recovers less (Figure~3): relative root %(rr1)s/%(rr2)s, applied flag %(af1)s, spelled degree alone %(spd1)s; inversion figures cost %(fb1)s/%(fb2)s. The supported positive finding is therefore that functional labelling gains predictive compression substantially through category lumping of applied chords, not that a nested Roman label supplies additional syntax." + chr(10))
s = s[:i] + para + s[j:]
# repair framing
i = s.index(B + "section{A failed preregistered MDL repair}"); j = s.index("Five feature blocks are parsed")
s = s[:i] + B + "section{A failed preregistered MDL repair}" + chr(10) + "The preregistered MDL experiment attempted to approximate the observed $F_{" + B + "mathrm{sel}}$ coding contrast with a five-feature lattice. Because $F_{" + B + "mathrm{sel}}$ is non-nested, this is a predictive reconstruction test for a particular label re-partition, not a repair of a conditional syntax residue. " + s[j:]
rep("This is a confirmatory negative result" if "This is a confirmatory negative result" in s else "Recovery is n/a where", "Recovery is n/a where")
# scope
i = s.index(B + "section{Scope and limitations}"); j = s.index(B + "end{document}")
scope = (B + "section{Scope and limitations}" + chr(10) + "Every claim in this study is descriptive of the observed annotations, fixed representations, folds, targets and prequential coder. The work-level non-nested Beethoven-versus-other margins are %(wm1)s/%(wm2)s bits per chord and the clean Beethoven residues %(wc1)s/%(wc2)s, but the 21-work betting processes against $H_0{:}" + B + "mathbb E[d]" + B + "le0.05$ attained only $E_{" + B + "max}=%(e1)s/%(e2)s$, far below the rejection threshold of 20. We therefore make no claim about composers, styles, unobserved works or any population; because the 70 ABC movements are also Beethoven movements, no contrast here can be attributed to composer. Learned-model robustness was not tested; coder dependence remains a limitation (plain KT without back-off inverts the ranking, and the selective contrast moves between %(b025)s and %(b4)s bits at $m=1$ as the smoothing mass varies from 0.25 to 4)." + chr(10) + chr(10))
s = s[:i] + scope + s[j:]
# remove the now-duplicated learned-model section
i = s.find(B + "section{Learned-model robustness}")
if i >= 0:
    j = s.index(B + "section{Scope and limitations}"); s = s[:i] + s[j:]
# figure 1 caption -> representation diagram statement
rep("caption{Design, estimand and provenance. Run B differs from run A only by an eligibility rule that admits nine additional cells; on the 49 shared cells both rules select the same prefix (Section~" + B + "ref{sec:audit}).}" if False else "caption{Control forest. Filled = $m{=}1$, open = $m{=}2$; dashed line = the preregistered $0.05$ bits/chord.}",
    "caption{Control forest for the non-nested selective contrast $L(Z)-L(F_{" + B + "mathrm{sel}})$ (a coding contrast, not a sufficiency residue). Filled = $m{=}1$, open = $m{=}2$; dashed = $0.05$ bits/chord. The valid nested comparison is Table~" + B + "ref{tab:nested}: $F_{" + B + "mathrm{nested}}" + B + "to Z$ is a functional projection, whereas no projection exists from $F_{" + B + "mathrm{sel}}$ to $Z$ (an applied $V/V$ has numeral $V$ but relative root degree $2$).}")
# format keys
old_keys = 'maxMoz=f(max(g(Mo, m, "gain_func_vs_localrel") for m in (1, 2, 3))),'
new_keys = ('maxMoz=f(max(g(Mo, m, "gain_func_vs_localrel") for m in (1, 2, 3))), nmax=f(_nmax(M), 4), nS1a=f(_nv(M, S, 1, "nested"), 4), nS1c=f(_nv(M, S, 1, "nested+clean"), 4), '
            'nS1p="%.1f" % (100 * _np(M, S, 1, "nested")), nS1q="%.1f" % (100 * _np(M, S, 1, "nested+clean")), nother=f(_nother(M), 4), nested_rows=_nested_rows(M), '
            'rlrest1=f(dS1["full"] - dS1.get("relabel3", 0)), rlrest2=f(dS2["full"] - dS2.get("relabel3", 0)), '
            'wm1=f(M["lowo"]["gate"]["m=1"]["base_margin"], 4), wm2=f(M["lowo"]["gate"]["m=2"]["base_margin"], 4), wc1=f(M["lowo"]["gate"]["m=1"]["clean_sonata_residue"], 4), wc2=f(M["lowo"]["gate"]["m=2"]["clean_sonata_residue"], 4), '
            'e1=str(M["lowo"]["gate"]["m=1"]["betting_e_base_tau005"]["E_max"]), e2=str(M["lowo"]["gate"]["m=2"]["betting_e_base_tau005"]["E_max"]), ')
rep(old_keys, new_keys)
helpers = '''
def _nv(M, corpus, m, variant):
    return M["nested"]["%s|m=%d|%s" % (corpus, m, variant)]["residue"]


def _np(M, corpus, m, variant):
    return M["nested"]["%s|m=%d|%s" % (corpus, m, variant)]["pos_share"]


def _nmax(M):
    return max(v["residue"] for v in M["nested"].values())


def _nother(M):
    return max(v["residue"] for k, v in M["nested"].items() if not k.startswith("beethoven"))


def _nested_rows(M):
    rows = []
    for c, cn in (("beethoven_piano_sonatas", "Beethoven piano sonatas"), ("ABC", "ABC quartets"), ("mozart_piano_sonatas", "Mozart piano sonatas")):
        for m in (1, 2):
            cells = []
            for v in ("nested", "nested+rootfree+fixedalpha", "nested+clean"):
                k = "%s|m=%d|%s" % (c, m, v)
                cells.append("%.4f (%.0f%%)" % (M["nested"][k]["residue"], 100 * M["nested"][k]["pos_share"]) if k in M["nested"] else "--")
            rows.append(r"%s & %d & %s \\\\" % (cn, m, " & ".join(cells)))
    return chr(10).join(rows)


def render(M):'''
rep("def render(M):", helpers.lstrip(chr(10)))
(H / "paper_text.py").write_text(s, encoding="utf-8")
# build_paper: lowo into manifest
b = (H / "build_paper.py").read_text(encoding="utf-8")
if '"lowo"' not in b:
    b = b.replace('"transfer_sourceonly": tso, "nested": nested}', '"transfer_sourceonly": tso, "nested": nested, "lowo": J("lowo_headline.json") if (D / "lowo_headline.json").exists() else None}')
    (H / "build_paper.py").write_text(b, encoding="utf-8")
print("r5 edits applied")
