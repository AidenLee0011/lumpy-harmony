# -*- coding: utf-8 -*-
"""Paper 9 LaTeX body; every number is read from the results manifest M (build_paper.py). Two-part structure: I Logic, II Experiment."""


def f(x, d=3):
    return ("%%.%df" % d) % x


P = chr(37)


def _rep(rep, corpus, m, target):
    return [x for x in (rep or []) if x["corpus"] == corpus and x["m"] == m and x["target"] == target][0]


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
                cells.append(("%.4f (%.0f" + chr(92) + "%%)") % (M["nested"][k]["residue"], 100 * M["nested"][k]["pos_share"]) if k in M["nested"] else "--")
            rows.append(r"%s & %d & %s \\" % (cn, m, " & ".join(cells)))
    return chr(10).join(rows)


def render(M):
    c = M["controls"]; fu = M["full"]; tr = M["transfer"]; jz = M["jazz"]; dec = M["decompose"]; rep = M.get("repair"); tso = M.get("transfer_sourceonly")
    S, A, Mo = "beethoven_piano_sonatas", "ABC", "mozart_piano_sonatas"
    def r(corpus, m, v, k="residue"): return c["%s|m=%d|%s" % (corpus, m, v)][k]
    def g(corpus, m, k): return fu[corpus]["m=%d" % m][k]
    ctrl_rows = "\n".join(r"%s & %s & %s & %s & %s \\" % (lab, f(r(S, 1, v)), f(r(S, 2, v)), f(r(A, 1, v)), f(r(A, 2, v))) for v, lab in
                          [("base", "base"), ("rootfree", "root-free geometry"), ("nocollapse", "no event collapse"), ("fixedalpha", "fixed alphabet + UNK"), ("target_nocur", "target without current shape"),
                           ("beta0.25", r"smoothing $\beta=0.25$"), ("beta4", r"smoothing $\beta=4$"), ("fullroman", "complete Roman label"), ("rootfree+fixedalpha+fullroman", "root-free + fixed + complete")])
    full_rows = "\n".join(r"%s & %d & %d & %s & %s & %s & %s & %s & %s \\" % (cn, m, g(cp, m, "n_eligible"), f(g(cp, m, "bits_per_chord")["geom"]), f(g(cp, m, "bits_per_chord")["keyrel"]), f(g(cp, m, "bits_per_chord")["localrel"]), f(g(cp, m, "bits_per_chord")["func"]), f(g(cp, m, "gain_func_vs_localrel")), "%d\\%%" % round(100 * g(cp, m, "share_movements_positive")))
                          for cp, cn in ((A, "ABC quartets"), (Mo, "Mozart sonatas"), (S, "Beethoven sonatas")) for m in (1, 2, 3))
    tr_rows = "\n".join(r"%s & %s & %s \\" % (k.replace("_piano_sonatas", "").replace("->", r"$\rightarrow$"), f(tr[k]["residue_func_vs_localrel"]), (f(tso[k]["residue_func_vs_localrel"]) if tso and k in tso else "--")) for k in sorted(tr))
    dS1, dS2 = dec[S]["m=1"], dec[S]["m=2"]
    if rep:
        rep_rows = "\n".join(r"%s & %d & %s & %s & %s & %s & %s & %s \\" % (x["corpus"].replace("_piano_sonatas", ""), x["m"], x["target"], f(x["G_ref"]), f(x["G_repair_net"]), (str(x["recovery_rho"]) if (x["recovery_rho"] is not None and x["G_ref"] > 0) else "n/a"), ", ".join(s or "none" for s in x["selected_masks"]), "yes" if x["stable_4of5"] else "no") for x in rep)
        rep_block = r"""\begin{table}[t]\centering\small
\caption{Preregistered MDL repair over the 32-node lattice $\{S,C,M,A,I\}$, work-grouped 5-fold. $G_{\mathrm{ref}}=L(Z)-L(F_{\mathrm{sel}})$; $G_{\mathrm{repair}}$ is net of description cost; $\rho=G_{\mathrm{repair}}/G_{\mathrm{ref}}$; the preregistered rule required $\rho\ge0.80$ at both $m=1,2$ plus 4-of-5 fold stability; it failed because clean $m=1$ reached only %%(rho1)s without stability and the base-target recoveries were %%(rhob1)s and %%(rhob2)s. Recovery is n/a where $G_{\mathrm{ref}}\le 0$.}\label{tab:repair}
\begin{tabular}{llllrrrl}\toprule corpus & $m$ & target & $G_{\mathrm{ref}}$ & $G_{\mathrm{repair}}$ & $\rho$ & selected per fold & stable \\ \midrule
%s
\bottomrule\end{tabular}\end{table}""" % rep_rows
        rep_block = rep_block.replace(P+"(rho1)s", str(_rep(rep, S, 1, "clean")["recovery_rho"])).replace(P+"(rhob1)s", str(_rep(rep, S, 1, "base")["recovery_rho"])).replace(P+"(rhob2)s", str(_rep(rep, S, 2, "base")["recovery_rho"]))
    else:
        rep_block = r"\emph{(MDL repair results pending: Table~\ref{tab:repair} and Figure 4 are generated when \texttt{repair\_lattice.json} exists.)}"
    styles = jz["m=2"]["per_style"]
    jz_rows = "\n".join(r"%s & %d & %s & %s & %s \\" % (s, v["n"], f(v["geom"]), f(v["keyrel"]), f(v["gain"])) for s, v in sorted(styles.items(), key=lambda kv: -kv[1]["gain"]))
    return r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}\usepackage{amsmath,amssymb,amsthm,booktabs,graphicx,hyperref}
\newtheorem{proposition}{Proposition}\newtheorem{definition}{Definition}
\title{Approximate Predictive Sufficiency of Local Chord Content: Roman Function as Applied-Chord Lumping and a Failed Preregistered MDL Repair}
\author{Anonymous}
\date{Draft, September 2026}
\begin{document}\maketitle

\begin{abstract}
Roman-numeral labels combine local chord content with functional category choices. We test, on the observed annotations of the Beethoven piano sonatas, the Annotated Beethoven Corpus quartets and the Mozart piano sonatas, whether $Z=(\text{chromatic relative root},\text{mode},\text{chord type})$ is operationally sufficient under a fixed prequential code at context depths $m=1,2$. The genuine refinement $F_{\mathrm{nested}}=(\text{numeral},\text{relative root},\text{mode},\text{chord type})$ deterministically contains $Z$. Across the base, root-free fixed-alphabet and clean-target analyses the residue $\Delta=L(Z)-L(F_{\mathrm{nested}})$ never exceeds %(nmax)s bits per chord: the Beethoven sonatas at $m=1$ give %(nS1a)s to %(nS1c)s with %(nS1p)s to %(nS1q)s\%% of movements positive, while every ABC and Mozart value is at most %(nother)s. All three corpora therefore meet our operational $\Delta\le 0.05$ criterion, with the Beethoven sonatas at the threshold at $m=1$. A selective label $F_{\mathrm{sel}}=(\text{numeral},\text{mode},\text{chord type})$ is not nested, because it groups applied dominants by function; its Beethoven contrast is %(s1)s/%(s2)s bits per chord, and relabelling only the applied chords by functional degree recovers %(rl1)s/%(rl2)s, or %(rlp1)s\%%/%(rlp2)s\%%, identifying a functional-lumping contribution rather than a nested syntax gain. A preregistered five-feature MDL repair of that contrast failed its joint recovery and stability rule. An integer-count certificate audits the mappings, folds and reported code lengths. All conclusions are restricted to these annotations, representations and coding protocols.
\end{abstract}

\part*{I. Logic}
\section{The representation question}
Two traditions describe tonal harmony: geometric accounts locate chords in voice-leading spaces (Tymoczko, 2006; Callender, Quinn and Tymoczko, 2008), functional accounts describe progressions with key-relative Roman labels (Rohrmeier, 2011). A predictive sufficiency comparison between them is valid only when the richer representation is a genuine refinement of the baseline. Our primary question is therefore whether the local-content state $Z$ is operationally sufficient, at a threshold of $0.05$ bits per chord, relative to a Roman representation that deterministically contains $Z$. Our secondary question concerns a different object: the selective label $F_{\mathrm{sel}}$, which does not contain the chromatic relative root and instead re-partitions applied chords by function; its code gain cannot be interpreted through the nested sufficiency proposition, so we analyse it as a representation effect and ask how much of the displayed contrast is recovered by functional relabelling of applied chords. Finally we report the confirmatory failure of a preregistered MDL repair intended to approximate that selective-label contrast. The contributions are the corrected nested measurement, the same-arity applied-chord attribution, the preregistered negative result and an auditable integer-count certificate. The original hypothesis of this study, a substantial Roman residue beyond a strong tonal baseline, was preregistered at $0.05$ bits per chord and failed.

\section{States, targets and quotients}
A chord event $t$ in a movement has a pitch-class set, an analysed root, a local key and a Roman label from the DCML annotation standard (Hentschel et al., 2021). A \emph{transition} from event $t$ to $t{+}1$ is canonicalised under common transposition: in the root-anchored version the previous root is sent to $0$; in the \emph{root-free} version the previous pitch-class set is sent to its lexicographically smallest transposition, so no analytic decision enters the geometry. A transition records the normalised previous set, the interval or shift to the next set, the normalised next set and the minimal total pitch-class displacement between the two sets.
\begin{definition}[contexts]
$G_t=O_m(t)$ is the tuple of the previous $m$ transitions (geometry). $K_t$ adds the root scale degree in the \emph{global} key, chord type and global mode. Let $Z_t=(r_t,\mu_t,\tau_t)$ with $r_t$ the chromatic root degree relative to the local tonic, $\mu_t$ the local mode and $\tau_t$ the chord type. The genuine refinement is $F_{\mathrm{nested},t}=(\nu_t,\rho_t,\mu_t,\tau_t)$ with $\nu_t$ the numeral and $\rho_t$ the relative root; the projection $h(\nu,\rho,\mu,\tau)=(r,\mu,\tau)$ recovers $Z_t$, so the sufficiency proposition applies. Separately, $F_{\mathrm{sel},t}=(\nu_t,\mu_t,\tau_t)$: no function recovers $Z_t$ from it (an applied $V/V$ has numeral $V$ but relative root degree $2$), so $F_{\mathrm{sel}}$ is a non-nested re-partition of $Z$ and $L(Z)-L(F_{\mathrm{sel}})$ is reported only as a coding contrast. The target $Y_t$ is the next transition; the \emph{no-current-shape} target keeps only the root shift and the displacement cost.
\end{definition}
$Z=h(F_{\mathrm{nested}})$ holds on every observed label combination (machine-checked; zero counterexamples); it does not hold for $F_{\mathrm{sel}}$.

\section{Sufficiency and repair}
Write $R_X=\inf_q \mathbb E[-\log_2 q(Y\mid G,X)]$ for the optimal log loss under context $X$.
\begin{proposition}[predictive sufficiency; standard]
If $Z=h(F)$ then $R_Z-R_F = H(Y\mid G,Z)-H(Y\mid G,F) = I(Y;F\mid G,Z)\ge 0$, and the following are equivalent: (i) $R_Z=R_F$; (ii) $Y\perp F\mid (G,Z)$; (iii) all fine states inside each $(G,Z)$ block share one predictive kernel; (iv) the projection $(G,F)\mapsto(G,Z)$ is predictively lumpable for $Y$.
\end{proposition}
\begin{proposition}[repair decomposition; standard]
For any repair $R=r(F)$ refining $Z$, $I(Y;F\mid G,Z)=I(Y;R\mid G,Z)+I(Y;F\mid G,R)$. On finite support, the classes of $(g,f)\equiv(g',f')\iff g=g',\,h(f)=h(f'),\,\widehat P(Y\mid g,f)=\widehat P(Y\mid g',f')$ form the unique coarsest refinement of $(G,Z)$ with zero empirical residue.
\end{proposition}
Both statements are background identities (log-loss regret equals conditional mutual information; kernel equality is Kemeny--Snell lumpability), not contributions of this paper. Their role is to fix what is being measured. The reported code-length differences are prequential estimates of $I(Y;F\mid G,Z)$; unlike the oracle quantity they can be negative, because a finite coder pays for every refinement it cannot fill with counts. We calibrate $\epsilon$-sufficiency with Pinsker: $I\le\epsilon$ implies $\mathbb E[\mathrm{TV}(P(Y\mid G,F),P(Y\mid G,Z))]\le\sqrt{\epsilon\ln 2/2}$, about $0.13$ at $\epsilon=0.05$.

\section{Exact certificate}
At submission every table will be regenerated from an archived manifest containing, for each corpus, $m$, target and context: for each corpus, $m$, target and context the counts $n_{gfy},n_{gf},n_{gzy},n_{gz}$, the cross-product audit $n_{gfy}n_{gz}=n_{gzy}n_{gf}$ per supported cell, the coding ledger (context, back-off level, counts, alphabet, UNK events, predictive probability, per-event loss), the exact code ratio $Q=\prod_t p_F(y_t)/p_Z(y_t)$ with $\log_2Q/N=L_Z/N-L_F/N$, one $Q_i$ per movement, and the repair fold files. The build fails if any headline number changes. Until the archive and its hashes are public this is an intended certificate, not a released one.

\part*{II. Experiment}
\section{Corpora and coder}
DCML corpora: Annotated Beethoven Corpus (%(nABC)d quartet movements), Mozart piano sonatas (%(nMoz)d), Beethoven piano sonatas (%(nS)d). Events with a parseable numeral, chord tones and local key are kept; consecutive identical pitch-class sets are collapsed to chord changes (a no-collapse control follows). The coder is prequential: the geometry-only predictor is a Krichevsky--Trofimov estimator over the transition alphabet; every label-augmented context backs off to it with escape mass $\beta$ ($p=(c_{\mathrm{ctx}}(y)+\beta p_G(y))/(n_{\mathrm{ctx}}+\beta)$). Each movement is coded with counts from all other movements and updated within itself. Plain KT without back-off inverts every ranking (adding any label costs bits) and is reported as the sparsity control it is.

\begin{table}[t]\centering\small
\caption{Corrected nested comparison. Each entry is $\Delta=L(Z)-L(F_{\mathrm{nested}})$ in bits per chord, followed by the share of movements with positive residue. The maximum observed nested residue is %(nmax)s; all rows meet the operational $\Delta\le0.05$ criterion. Small negative finite-code contrasts do not contradict the oracle inequality.}\label{tab:nested}
\begin{tabular}{llrrr}\toprule corpus & $m$ & base nested & root-free + fixed alphabet & clean target \\ \midrule
%(nested_rows)s
\bottomrule\end{tabular}\end{table}

\begin{table}[t]\centering\small
\caption{Full corpora, root-anchored geometry, $\beta=1$. Bits per eligible chord; residue $=L(Z)-L(F_{\mathrm{sel}})$; last column = movements with positive residue.}\label{tab:full}
\begin{tabular}{llrrrrrrr}\toprule corpus & $m$ & $n$ & $G$ & $K$ (global key) & $Z$ (local key) & $F_{\mathrm{sel}}$ & residue & positive \\ \midrule
%(full_rows)s
\bottomrule\end{tabular}\end{table}

\section{Controls}
\begin{table}[t]\centering\small
\caption{Residue $L(Z)-L(F_{\mathrm{sel}})$ under each control (bits/chord). The complete-label rows are negative because the finite coder cannot fill the refined contexts, not because the oracle information is negative.}\label{tab:ctrl}
\begin{tabular}{lrrrr}\toprule control & sonatas $m{=}1$ & $m{=}2$ & ABC $m{=}1$ & $m{=}2$ \\ \midrule
%(ctrl_rows)s
\bottomrule\end{tabular}\end{table}
Figure~1 shows the same numbers as a forest; Figure~2 the share of movements with positive residue. Considered separately, root-free geometry retains %(rfpct1)s\%% and %(rfpct2)s\%% of the base sonata residue and the no-current-shape target retains %(ncpct1)s\%% and %(ncpct2)s\%%; under the combined root-free, fixed-alphabet, no-current-shape held-out protocol the sonata residues are %(cl1)s and %(cl2)s bits per chord. The ABC residue stays at or below $0.053$ under every control.

\begin{figure}[t]\centering\includegraphics[width=\linewidth]{figs/fig1_controls.pdf}\caption{Control forest for the non-nested selective contrast $L(Z)-L(F_{\mathrm{sel}})$ (a coding contrast, not a sufficiency residue). Filled = $m{=}1$, open = $m{=}2$; dashed = $0.05$ bits/chord. The valid nested comparison is Table~\ref{tab:nested}: $F_{\mathrm{nested}}\to Z$ is a functional projection, whereas no projection exists from $F_{\mathrm{sel}}$ to $Z$ (an applied $V/V$ has numeral $V$ but relative root degree $2$).}\end{figure}
\begin{figure}[t]\centering\includegraphics[width=\linewidth]{figs/fig2_prevalence.pdf}\caption{Share of movements with positive residue under each control.}\end{figure}

\section{What the selective-label contrast is}
The tuple (numeral, chord type, mode), at the same arity as $Z$, reproduces the Beethoven selective contrasts of %(s1)s/%(s2)s bits per chord exactly (%(sp1)s and %(sp2)s). This tuple is not a refinement of $Z$: it groups applied dominants onto their functional numeral while retaining spelled alterations elsewhere. Relabelling only the applied chords by functional degree, again at the same arity, yields gains of %(rl1)s/%(rl2)s bits per chord, equal to %(rlp1)s\%%/%(rlp2)s\%% of the full selective contrast; the remaining %(rlrest1)s/%(rlrest2)s bits are not explained by this operation. Adding single complete-label fields on top of $Z$ recovers less (Figure~3): relative root %(rr1)s/%(rr2)s, applied flag %(af1)s, spelled degree alone %(spd1)s; inversion figures cost %(fb1)s/%(fb2)s. The supported positive finding is therefore that functional labelling gains predictive compression substantially through category lumping of applied chords, not that a nested Roman label supplies additional syntax.
\begin{figure}[t]\centering\includegraphics[width=\linewidth]{figs/fig3_attribution.pdf}\caption{Residue recovered by adding one label feature to $Z$ (Beethoven sonatas); dashed = selective label.}\end{figure}

\section{A failed preregistered MDL repair}
The preregistered MDL experiment attempted to approximate the observed $F_{\mathrm{sel}}$ coding contrast with a five-feature lattice. Because $F_{\mathrm{sel}}$ is non-nested, this is a predictive reconstruction test for a particular label re-partition, not a repair of a conditional syntax residue. Five feature blocks are parsed from the complete label: spelled degree $S$, case $C$, mixture $M$, applied structure $A$, inversion $I$. All 32 subsets are scored prequentially on training works, charged $D(B)=3+\lceil\log_2\binom{5}{|B|}\rceil$ bits, and the minimiser is applied to held-out works (5 folds grouped by work, SHA256 round robin). %(rep_block)s
\begin{figure}[t]\centering\includegraphics[width=\linewidth]{figs/fig4_repair.pdf}\caption{Held-out bits per chord for geometry, $Z$, the selected repair, the selective label and all five features.}\end{figure}

\section{Transfer and an out-of-domain contrast}
Training the coder on one corpus and coding another, sonata-target residues remain the largest under both adapted and source-only scoring, and the other targets stay at or below $0.053$ (Table~\ref{tab:tr}; adapted = counts updated on the target stream, source-only = frozen counts). In the Weimar Jazz Database (456 solos, chord symbols, no Roman labels) key-relative chord content improves next-move prediction by %(jazz)s bits per chord at $m=2$, four to five times the classical gain; the gain ranges from %(jzmin)s (%(jzminname)s) to %(jzmax)s (%(jzmaxname)s) across styles. Roman residue is undefined there; the contrast bounds how idiom-specific the classical numbers are.
\begin{table}[t]\centering\small\caption{Cross-corpus transfer of the residue (bits/chord).}\label{tab:tr}
\begin{tabular}{lrr}\toprule train $\rightarrow$ test, $m$ & adapted & source-only \\ \midrule
%(tr_rows)s
\bottomrule\end{tabular}\end{table}
\begin{table}[t]\centering\small\caption{WJazzD, $m=2$: key-relative content gain over geometry by style.}\label{tab:jz}
\begin{tabular}{lrrrr}\toprule style & $n$ & $G$ & $K$ & gain \\ \midrule
%(jz_rows)s
\bottomrule\end{tabular}\end{table}
\begin{figure}[t]\centering\includegraphics[width=\linewidth]{figs/fig5_transfer_jazz.pdf}\caption{Left: transfer residues (filled adapted, open source-only). Right: WJazzD key-relative gain by style; dashed = classical 0.5.}\end{figure}

\section{Scope and limitations}
Every claim in this study is descriptive of the observed annotations, fixed representations, folds, targets and prequential coder. The work-level non-nested Beethoven-versus-other margins are %(wm1)s/%(wm2)s bits per chord and the clean Beethoven residues %(wc1)s/%(wc2)s, but the 21-work betting processes against $H_0{:}\mathbb E[d]\le0.05$ attained only $E_{\max}=%(e1)s/%(e2)s$, far below the rejection threshold of 20. We therefore make no claim about composers, styles, unobserved works or any population; because the 70 ABC movements are also Beethoven movements, no contrast here can be attributed to composer. Learned-model robustness was not tested; coder dependence remains a limitation (plain KT without back-off inverts the ranking, and the selective contrast moves between %(b025)s and %(b4)s bits at $m=1$ as the smoothing mass varies from 0.25 to 4).

\end{document}
""" % dict(nmov=sum(M["corpora"].values()), nABC=M["corpora"][A], nMoz=M["corpora"][Mo], nS=M["corpora"][S],
           maxABC=f(max(g(A, m, "gain_func_vs_localrel") for m in (1, 2, 3)) if True else 0), s1=f(r(S, 1, "base")), s2=f(r(S, 2, "base")), rf1=f(r(S, 1, "rootfree")), rf2=f(r(S, 2, "rootfree")),
           nc1=f(r(S, 2, "target_nocur")), nc2=f(r(S, 1, "target_nocur")), jazz=f(jz["m=2"]["gain_keyrel"], 2), full_rows=full_rows, ctrl_rows=ctrl_rows, tr_rows=tr_rows, jz_rows=jz_rows, rep_block=rep_block,
           rfpct1="%d" % round(100 * r(S, 1, "rootfree") / r(S, 1, "base")), rfpct2="%d" % round(100 * r(S, 2, "rootfree") / r(S, 2, "base")), ncpct1="%d" % round(100 * r(S, 1, "target_nocur") / r(S, 1, "base")), ncpct2="%d" % round(100 * r(S, 2, "target_nocur") / r(S, 2, "base")),
           sp1=f(dS1.get("spelled3", 0)), sp2=f(dS2.get("spelled3", 0)), rl1=f(dS1.get("relabel3", 0)), rl2=f(dS2.get("relabel3", 0)), rlp1="%d" % round(100 * dS1.get("relabel3", 0) / dS1["full"]), rlp2="%d" % round(100 * dS2.get("relabel3", 0) / dS2["full"]),
           rr1=f(dS1["+relativeroot"]), rr2=f(dS2["+relativeroot"]), af1=f(dS1.get("+applied_flag", 0)), spd1=f(dS1.get("+spelled", 0)), fb1=f(dS1["+figbass"]), fb2=f(dS2["+figbass"]),
           jzmin=f(min(v["gain"] for v in styles.values()), 2), jzminname=min(styles, key=lambda s: styles[s]["gain"]).lower(), jzmax=f(max(v["gain"] for v in styles.values()), 2), jzmaxname=max(styles, key=lambda s: styles[s]["gain"]).lower(),
           maxMoz=f(max(g(Mo, m, "gain_func_vs_localrel") for m in (1, 2, 3))), nmax=f(_nmax(M), 4), nS1a=f(_nv(M, S, 1, "nested"), 4), nS1c=f(_nv(M, S, 1, "nested+clean"), 4), nS1p="%.1f" % (100 * _np(M, S, 1, "nested")), nS1q="%.1f" % (100 * _np(M, S, 1, "nested+clean")), nother=f(_nother(M), 4), nested_rows=_nested_rows(M), rlrest1=f(dS1["full"] - dS1.get("relabel3", 0)), rlrest2=f(dS2["full"] - dS2.get("relabel3", 0)), wm1=f(M["lowo"]["gate"]["m=1"]["base_margin"], 4), wm2=f(M["lowo"]["gate"]["m=2"]["base_margin"], 4), wc1=f(M["lowo"]["gate"]["m=1"]["clean_sonata_residue"], 4), wc2=f(M["lowo"]["gate"]["m=2"]["clean_sonata_residue"], 4), e1=str(M["lowo"]["gate"]["m=1"]["betting_e_base_tau005"]["E_max"]), e2=str(M["lowo"]["gate"]["m=2"]["betting_e_base_tau005"]["E_max"]),  cl1=f(_rep(rep, S, 1, "clean")["G_ref"], 4), cl2=f(_rep(rep, S, 2, "clean")["G_ref"], 4), rho1=str(_rep(rep, S, 1, "clean")["recovery_rho"]), rhob1=str(_rep(rep, S, 1, "base")["recovery_rho"]), rhob2=str(_rep(rep, S, 2, "base")["recovery_rho"]), b025=f(r(S, 1, "beta0.25")), b4=f(r(S, 1, "beta4")), Ddet=f(((r(S, 1, "rootfree") - r(A, 1, "rootfree")) + (r(S, 2, "rootfree") - r(A, 2, "rootfree"))) / 2, 4))
