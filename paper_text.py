# -*- coding: utf-8 -*-
"""Paper 9 LaTeX body; every number is read from the results manifest M (build_paper.py). Two-part structure: I Logic, II Experiment."""


def f(x, d=3):
    return ("%%.%df" % d) % x


P = chr(37)


def _rep(rep, corpus, m, target):
    return [x for x in (rep or []) if x["corpus"] == corpus and x["m"] == m and x["target"] == target][0]


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
\title{Roman-Numeral Information Beyond Local Chord Content: Predictive Sufficiency and a Failed Preregistered Repair}
\author{Anonymous}
\date{Draft, September 2026}
\begin{document}\maketitle

\begin{abstract}
How much of a Roman-numeral harmonic analysis is information beyond the local key? We ask the question as a prediction problem: given the transposition-invariant voice-leading geometry of the last $m$ chord moves, how many bits per chord does the analyst's Roman label add when predicting the next move, once the local chromatic root degree, chord type and mode are already supplied. Using a fixed leave-one-movement-out prequential code on %(nmov)d movements from three DCML corpora, the maximum observed selective-label residue is %(maxABC)s bits per chord in the Annotated Beethoven Corpus (string quartets) and %(maxMoz)s in the Mozart piano sonatas, meeting our operational, finite-corpus criterion of at most $0.05$ bits per chord. In the Beethoven piano sonatas the selective label gains %(s1)s to %(s2)s bits per chord on the base target and %(nc1)s to %(nc2)s on a separate no-current-shape control; under the combined root-free, fixed-alphabet, no-current-shape held-out protocol the residue is %(cl1)s at $m=1$ and %(cl2)s at $m=2$. Functional relabelling of applied chords accounts for %(rlp1)s\%% and %(rlp2)s\%% of the base residue. The complete Roman label, with inversion and alteration fields, does not improve finite-sample code length. We use two standard log-loss identities to define the oracle quantities, report finite prequential code contrasts, provide an archival integer-count certificate, and document the failure of a preregistered five-feature MDL repair, which recovered %(rho1)s of the clean residue at $m=1$ with unstable feature selection and %(rhob1)s to %(rhob2)s of the base residue. A jazz corpus without Roman labels serves as an out-of-domain contrast: there, key-relative chord content improves next-move prediction by %(jazz)s bits per chord.
\end{abstract}

\part*{I. Logic}
\section{The representation question}
Two traditions describe tonal harmony. Geometric accounts (Tymoczko, 2006; Callender, Quinn and Tymoczko, 2008) locate chords in voice-leading spaces and explain progressions by efficient motion between them. Functional and syntactic accounts (Rohrmeier, 2011) describe progressions with key-relative labels, the Roman numerals of harmonic analysis. The two are usually contrasted by argument. We contrast them by a quantity: the conditional information that the Roman label carries about the next chord move, given the geometry and given a deliberately strong key-aware baseline. The original hypothesis of this study, that Roman function carries a substantial residue beyond a strong tonal baseline, was preregistered with a threshold of $0.05$ bits per chord; it failed in two of three corpora. The paper reports what survived.

\section{States, targets and quotients}
A chord event $t$ in a movement has a pitch-class set, an analysed root, a local key and a Roman label from the DCML annotation standard (Hentschel et al., 2021). A \emph{transition} from event $t$ to $t{+}1$ is canonicalised under common transposition: in the root-anchored version the previous root is sent to $0$; in the \emph{root-free} version the previous pitch-class set is sent to its lexicographically smallest transposition, so no analytic decision enters the geometry. A transition records the normalised previous set, the interval or shift to the next set, the normalised next set and the minimal total pitch-class displacement between the two sets.
\begin{definition}[contexts]
$G_t=O_m(t)$ is the tuple of the previous $m$ transitions (geometry). $K_t$ adds the root scale degree in the \emph{global} key, chord type and global mode. $Z_t$ adds the root scale degree in the \emph{local} key, chord type and local mode (no Roman syntax). $F_{\mathrm{sel},t}$ adds the selective Roman label (numeral, local mode, chord type). $F_{\mathrm{all},t}$ adds the complete label (relative root, inversion figures, alterations, form). The target $Y_t$ is the next transition; the \emph{no-current-shape} target keeps only the root shift and the displacement cost.
\end{definition}
$Z$ is a deterministic function of the label content, $Z=h(F)$, so $F$ refines $Z$.

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

\begin{figure}[t]\centering\includegraphics[width=\linewidth]{figs/fig1_controls.pdf}\caption{Control forest. Filled = $m{=}1$, open = $m{=}2$; dashed line = the preregistered $0.05$ bits/chord.}\end{figure}
\begin{figure}[t]\centering\includegraphics[width=\linewidth]{figs/fig2_prevalence.pdf}\caption{Share of movements with positive residue under each control.}\end{figure}

\section{What carries the residue}
The selective label differs from $Z$ only in the numeral string: the spelled scale degree with alterations, whose applied chords are labelled by their function (a $V/V$ is a $V$) rather than by their chromatic degree. Coding with (numeral, chord type, mode), the same arity as $Z$, reproduces the selective residue exactly (%(sp1)s and %(sp2)s bits at $m=1,2$). At the same arity, functional relabelling of applied chords yields code gains of %(rl1)s and %(rl2)s bits, equal to %(rlp1)s\%% and %(rlp2)s\%% of the displayed selective contrast; this does not by itself establish a causal syntactic effect or a feature interaction. Adding single complete-label fields on top of $Z$ recovers less than the selective label (Figure~3): relative root %(rr1)s / %(rr2)s, applied flag %(af1)s, spelled degree alone %(spd1)s; inversion figures cost %(fb1)s / %(fb2)s.
\begin{figure}[t]\centering\includegraphics[width=\linewidth]{figs/fig3_attribution.pdf}\caption{Residue recovered by adding one label feature to $Z$ (Beethoven sonatas); dashed = selective label.}\end{figure}

\section{A failed preregistered MDL repair}
Five feature blocks are parsed from the complete label: spelled degree $S$, case $C$, mixture $M$, applied structure $A$, inversion $I$. All 32 subsets are scored prequentially on training works, charged $D(B)=3+\lceil\log_2\binom{5}{|B|}\rceil$ bits, and the minimiser is applied to held-out works (5 folds grouped by work, SHA256 round robin). %(rep_block)s
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

\section{Learned-model robustness}
Learned-model robustness was not tested; coder dependence remains a limitation (plain KT without back-off inverts the ranking, and the sonata residue moves between %(b025)s and %(b4)s bits at $m=1$ as the smoothing mass varies from 0.25 to 4).

\section{Scope and limitations}
These are finite-corpus, parser-, annotation-, target- and coder-conditional results for the DCML ABC quartet corpus, Mozart corpus and Beethoven piano-sonata corpus; because the 70 ABC movements are also Beethoven movements, the contrast cannot be attributed to composer and may reflect repertory type, corpus construction, annotation practice or label sparsity. The e-process on movement-level gains against $H_0{:}\ \mathbb E[\text{residue}]\le0.05$ does not reject at a Hoeffding bound with range $0.5$; the residue is a deterministic finite-corpus statement, not a superpopulation claim. Nothing here shows that Roman function beats geometry in general; the paper shows what a strong key-aware baseline leaves for the label to explain, and where.

\end{document}
""" % dict(nmov=sum(M["corpora"].values()), nABC=M["corpora"][A], nMoz=M["corpora"][Mo], nS=M["corpora"][S],
           maxABC=f(max(g(A, m, "gain_func_vs_localrel") for m in (1, 2, 3)) if True else 0), s1=f(r(S, 1, "base")), s2=f(r(S, 2, "base")), rf1=f(r(S, 1, "rootfree")), rf2=f(r(S, 2, "rootfree")),
           nc1=f(r(S, 2, "target_nocur")), nc2=f(r(S, 1, "target_nocur")), jazz=f(jz["m=2"]["gain_keyrel"], 2), full_rows=full_rows, ctrl_rows=ctrl_rows, tr_rows=tr_rows, jz_rows=jz_rows, rep_block=rep_block,
           rfpct1="%d" % round(100 * r(S, 1, "rootfree") / r(S, 1, "base")), rfpct2="%d" % round(100 * r(S, 2, "rootfree") / r(S, 2, "base")), ncpct1="%d" % round(100 * r(S, 1, "target_nocur") / r(S, 1, "base")), ncpct2="%d" % round(100 * r(S, 2, "target_nocur") / r(S, 2, "base")),
           sp1=f(dS1.get("spelled3", 0)), sp2=f(dS2.get("spelled3", 0)), rl1=f(dS1.get("relabel3", 0)), rl2=f(dS2.get("relabel3", 0)), rlp1="%d" % round(100 * dS1.get("relabel3", 0) / dS1["full"]), rlp2="%d" % round(100 * dS2.get("relabel3", 0) / dS2["full"]),
           rr1=f(dS1["+relativeroot"]), rr2=f(dS2["+relativeroot"]), af1=f(dS1.get("+applied_flag", 0)), spd1=f(dS1.get("+spelled", 0)), fb1=f(dS1["+figbass"]), fb2=f(dS2["+figbass"]),
           jzmin=f(min(v["gain"] for v in styles.values()), 2), jzminname=min(styles, key=lambda s: styles[s]["gain"]).lower(), jzmax=f(max(v["gain"] for v in styles.values()), 2), jzmaxname=max(styles, key=lambda s: styles[s]["gain"]).lower(),
           maxMoz=f(max(g(Mo, m, "gain_func_vs_localrel") for m in (1, 2, 3))), cl1=f(_rep(rep, S, 1, "clean")["G_ref"], 4), cl2=f(_rep(rep, S, 2, "clean")["G_ref"], 4), rho1=str(_rep(rep, S, 1, "clean")["recovery_rho"]), rhob1=str(_rep(rep, S, 1, "base")["recovery_rho"]), rhob2=str(_rep(rep, S, 2, "base")["recovery_rho"]), b025=f(r(S, 1, "beta0.25")), b4=f(r(S, 1, "beta4")), Ddet=f(((r(S, 1, "rootfree") - r(A, 1, "rootfree")) + (r(S, 2, "rootfree") - r(A, 2, "rootfree"))) / 2, 4))
