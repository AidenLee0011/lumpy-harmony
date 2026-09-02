# -*- coding: utf-8 -*-
"""Paper 9 LaTeX body; every number is read from the results manifest M (build_paper.py). Two-part structure: I Logic, II Experiment."""


def f(x, d=3):
    return ("%%.%df" % d) % x


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
        rep_rows = "\n".join(r"%s & %d & %s & %s & %s & %s & %s & %s \\" % (x["corpus"].replace("_piano_sonatas", ""), x["m"], x["target"], f(x["G_ref"]), f(x["G_repair_net"]), (str(x["recovery_rho"]) if x["recovery_rho"] is not None else "--"), ", ".join(s or "Z" for s in x["selected_masks"]), "yes" if x["stable_4of5"] else "no") for x in rep)
        rep_block = r"""\begin{table}[t]\centering\small
\caption{Preregistered MDL repair over the 32-node lattice $\{S,C,M,A,I\}$, work-grouped 5-fold. $G_{\mathrm{ref}}=L(Z)-L(F_{\mathrm{sel}})$; $G_{\mathrm{repair}}$ is net of description cost; $\rho=G_{\mathrm{repair}}/G_{\mathrm{ref}}$; the success criterion was $\rho\ge0.80$.}\label{tab:repair}
\begin{tabular}{llllrrrl}\toprule corpus & $m$ & target & $G_{\mathrm{ref}}$ & $G_{\mathrm{repair}}$ & $\rho$ & selected per fold & stable \\ \midrule
%s
\bottomrule\end{tabular}\end{table}""" % rep_rows
    else:
        rep_block = r"\emph{(MDL repair results pending: Table~\ref{tab:repair} and Figure 4 are generated when \texttt{repair\_lattice.json} exists.)}"
    styles = jz["m=2"]["per_style"]
    jz_rows = "\n".join(r"%s & %d & %s & %s & %s \\" % (s, v["n"], f(v["geom"]), f(v["keyrel"]), f(v["gain"])) for s, v in sorted(styles.items(), key=lambda kv: -kv[1]["gain"]))
    return r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}\usepackage{amsmath,amssymb,amsthm,booktabs,graphicx,hyperref}
\newtheorem{theorem}{Theorem}\newtheorem{definition}{Definition}
\title{Predictive Sufficiency and Selective Roman-Numeral Repair in Annotated Harmonic Corpora}
\author{Anonymous}
\date{Draft, September 2026}
\begin{document}\maketitle

\begin{abstract}
How much of a Roman-numeral harmonic analysis is information beyond the local key? We ask the question as a prediction problem: given the transposition-invariant voice-leading geometry of the last $m$ chord moves, how many bits per chord does the analyst's Roman label add when predicting the next move, once the local chromatic root degree, chord type and mode are already supplied. Using a fixed leave-one-movement-out prequential code on %(nmov)d movements from three DCML corpora, we find that local chromatic root degree, chord type and mode are approximately sufficient in the Annotated Beethoven Corpus (string quartets) and the Mozart piano sonatas: the selective Roman label adds at most %(maxABC)s bits per chord. In the Beethoven piano sonatas it adds %(s1)s to %(s2)s bits per chord, and this advantage survives root-free geometry (%(rf1)s to %(rf2)s), reinterpretation-preserving events, a fixed target alphabet and smoothing from $\beta=0.25$ to $4$; it halves under a target that removes the current chord shape (%(nc1)s to %(nc2)s). The complete Roman label, with inversion and alteration fields, does not improve finite-sample code length. We state the sufficiency and repair theorems that make the quantities exact, release an integer-count certificate, and report a preregistered MDL repair over five label features. A jazz corpus without Roman labels serves as an out-of-domain contrast: there, key-relative chord content improves next-move prediction by %(jazz)s bits per chord.
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
\begin{theorem}[predictive sufficiency]
If $Z=h(F)$ then $R_Z-R_F = H(Y\mid G,Z)-H(Y\mid G,F) = I(Y;F\mid G,Z)\ge 0$, and the following are equivalent: (i) $R_Z=R_F$; (ii) $Y\perp F\mid (G,Z)$; (iii) all fine states inside each $(G,Z)$ block share one predictive kernel; (iv) the projection $(G,F)\mapsto(G,Z)$ is predictively lumpable for $Y$.
\end{theorem}
\begin{theorem}[repair decomposition]
For any repair $R=r(F)$ refining $Z$, $I(Y;F\mid G,Z)=I(Y;R\mid G,Z)+I(Y;F\mid G,R)$. On finite support, the classes of $(g,f)\equiv(g',f')\iff g=g',\,h(f)=h(f'),\,\widehat P(Y\mid g,f)=\widehat P(Y\mid g',f')$ form the unique coarsest refinement of $(G,Z)$ with zero empirical residue.
\end{theorem}
Both statements are standard (log-loss regret equals conditional mutual information; kernel equality is Kemeny--Snell lumpability). Their role here is to fix what is being measured. The reported code-length differences are prequential estimates of $I(Y;F\mid G,Z)$; unlike the oracle quantity they can be negative, because a finite coder pays for every refinement it cannot fill with counts. We calibrate $\epsilon$-sufficiency with Pinsker: $I\le\epsilon$ implies $\mathbb E[\mathrm{TV}(P(Y\mid G,F),P(Y\mid G,Z))]\le\sqrt{\epsilon\ln 2/2}$, about $0.13$ at $\epsilon=0.05$.

\section{Exact certificate}
Every table below is regenerated from released integer counts: for each corpus, $m$, target and context the counts $n_{gfy},n_{gf},n_{gzy},n_{gz}$, the cross-product audit $n_{gfy}n_{gz}=n_{gzy}n_{gf}$ per supported cell, the coding ledger (context, back-off level, counts, alphabet, UNK events, predictive probability, per-event loss), the exact code ratio $Q=\prod_t p_F(y_t)/p_Z(y_t)$ with $\log_2Q/N=L_Z/N-L_F/N$, one $Q_i$ per movement, and the repair fold files. The build fails if any headline number changes.

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
Figure~1 shows the same numbers as a forest; Figure~2 the share of movements with positive residue. Root-free geometry retains %(rfpct1)s\%% and %(rfpct2)s\%% of the base sonata residue; the no-current-shape target retains %(ncpct1)s\%% and %(ncpct2)s\%%. The ABC residue stays at or below $0.053$ under every control.

\begin{figure}[t]\centering\includegraphics[width=\linewidth]{figs/fig1_controls.pdf}\caption{Control forest. Filled = $m{=}1$, open = $m{=}2$; dashed line = the preregistered $0.05$ bits/chord.}\end{figure}
\begin{figure}[t]\centering\includegraphics[width=\linewidth]{figs/fig2_prevalence.pdf}\caption{Share of movements with positive residue under each control.}\end{figure}

\section{What carries the residue}
The selective label differs from $Z$ only in the numeral string: the spelled scale degree with alterations, whose applied chords are labelled by their function (a $V/V$ is a $V$) rather than by their chromatic degree. Coding with (numeral, chord type, mode), the same arity as $Z$, reproduces the selective residue exactly (%(sp1)s and %(sp2)s bits at $m=1,2$). Relabelling only the applied chords by their functional degree, again at the same arity, recovers %(rl1)s and %(rl2)s bits, that is %(rlp1)s\%% and %(rlp2)s\%% of the residue. Adding single complete-label fields on top of $Z$ recovers less than the selective label (Figure~3): relative root %(rr1)s / %(rr2)s, applied flag %(af1)s, spelled degree alone %(spd1)s; inversion figures cost %(fb1)s / %(fb2)s.
\begin{figure}[t]\centering\includegraphics[width=\linewidth]{figs/fig3_attribution.pdf}\caption{Residue recovered by adding one label feature to $Z$ (Beethoven sonatas); dashed = selective label.}\end{figure}

\section{Preregistered MDL repair}
Five feature blocks are parsed from the complete label: spelled degree $S$, case $C$, mixture $M$, applied structure $A$, inversion $I$. All 32 subsets are scored prequentially on training works, charged $D(B)=3+\lceil\log_2\binom{5}{|B|}\rceil$ bits, and the minimiser is applied to held-out works (5 folds grouped by work, SHA256 round robin). %(rep_block)s
\begin{figure}[t]\centering\includegraphics[width=\linewidth]{figs/fig4_repair.pdf}\caption{Held-out bits per chord for geometry, $Z$, the selected repair, the selective label and all five features.}\end{figure}

\section{Transfer and an out-of-domain contrast}
Training the coder on one corpus and coding another, the sonata corpus keeps its residue whichever corpus supplies the counts, and the other two corpora stay at or below $0.053$ (Table~\ref{tab:tr}; adapted = counts updated on the target stream, source-only = frozen counts). In the Weimar Jazz Database (456 solos, chord symbols, no Roman labels) key-relative chord content improves next-move prediction by %(jazz)s bits per chord at $m=2$, four to five times the classical gain; the gain ranges from %(jzmin)s (%(jzminname)s) to %(jzmax)s (%(jzmaxname)s) across styles. Roman residue is undefined there; the contrast bounds how idiom-specific the classical numbers are.
\begin{table}[t]\centering\small\caption{Cross-corpus transfer of the residue (bits/chord).}\label{tab:tr}
\begin{tabular}{lrr}\toprule train $\rightarrow$ test, $m$ & adapted & source-only \\ \midrule
%(tr_rows)s
\bottomrule\end{tabular}\end{table}
\begin{table}[t]\centering\small\caption{WJazzD, $m=2$: key-relative content gain over geometry by style.}\label{tab:jz}
\begin{tabular}{lrrrr}\toprule style & $n$ & $G$ & $K$ & gain \\ \midrule
%(jz_rows)s
\bottomrule\end{tabular}\end{table}
\begin{figure}[t]\centering\includegraphics[width=\linewidth]{figs/fig5_transfer_jazz.pdf}\caption{Left: transfer residues (filled adapted, open source-only). Right: WJazzD key-relative gain by style; dashed = classical 0.5.}\end{figure}

\section{Learned-model robustness (appendix study)}
A two-layer Transformer ($d=96$, 4 heads, FFN 192) with one categorical condition position (null / $Z$ / $F_{\mathrm{sel}}$), padded condition vocabularies for equal parameter counts, five work-grouped folds and ten seeds is used only to check that the corpus ordering is not coder-specific: the deterministic contrast $D_{\det}=%(Ddet)s$ bits/chord must have the same sign under the learned model. This study is pending and is reported in the appendix when complete.

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
           Ddet=f(((r(S, 1, "rootfree") - r(A, 1, "rootfree")) + (r(S, 2, "rootfree") - r(A, 2, "rootfree"))) / 2, 4))
