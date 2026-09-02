# -*- coding: utf-8 -*-
"""Paper 10 LaTeX body, v3 (sol P72_p10_r4 + r5 edits, panel p10v2 fixes). All numbers from the manifest M. Held-out quantities are scores (bar s); sigma is reserved for laws."""
import json


def f(x, d=3):
    return ("%%.%df" % d) % x


def pct(x, d=1):
    return ("%%.%df" % d) % (100 * x)


def _loop_tex(s):
    s = s.replace("/maj", "").replace("/min", "m").replace(":", "")
    return r"$" + s.replace(">", r"\rightarrow ") + r"$"


def render(M):
    S, SUP, INV, INVU, DEC, R4, ALPH, MODE = M["S"], M["SUP"], M["INV"], M["INVU"], M["DEC"], M.get("R4", {}), M.get("ALPH", {}), M.get("MODE")
    b, w = INV["bach"]["alpha"], INV["wjazzd"]["alpha"]
    AL = ("0.1", "0.5", "1")
    def boot(d, a):
        g = d[a].get("group_bootstrap")
        return ("%s & %s--%s" % (f(g["Delta_inv_p05"]), pct(g["share_p05"]), pct(g["share_p95"]))) if g else "-- & --"
    def inv_rows(c, d):
        return "\n".join(r"%s & %s & %s & %s & %s & %s & %s & %s & %s \\" % (c, a, f(d[a]["sigma_C"]), f(d[a]["sigma_D"]), f(d[a]["Delta_inv"]), pct(d[a]["residual_share"]), f(d[a]["group_mean"]), f(d[a]["group_LCB95"]), boot(d, a)) for a in AL)
    unc = "\n".join(r"%s (uncollapsed) & 0.5 & %s & %s & %s & %s & %s & %s & -- & -- \\" % (c, f(INVU[k]["alpha"]["0.5"]["sigma_C"]), f(INVU[k]["alpha"]["0.5"]["sigma_D"]), f(INVU[k]["alpha"]["0.5"]["Delta_inv"]), pct(INVU[k]["alpha"]["0.5"]["residual_share"]), f(INVU[k]["alpha"]["0.5"]["group_mean"]), f(INVU[k]["alpha"]["0.5"]["group_LCB95"])) for c, k in (("Bach", "bach"), ("WJazzD", "wjazzd")))
    def sup_rows(k):
        rows = []
        for a in AL:
            for r in (0, 1, 2, 5):
                x = SUP[k]["results"]["alpha=%s|r=%d" % (a, r)]; rows.append(r"%s & %s & %s & %s & %s & %s & %s \\" % (a, ("all" if r == 0 else "r=%d" % r), pct(x["rho"]), f(x["retained_total"]), f(x["conditional"]), f(x["work_LCB95"]), x["zero_works"]))
        return "\n".join(rows)
    def edge_rows(k):
        return "\n".join(r"%s & %d & %d & %s \\" % (t["edge"].replace("/maj", " (major)").replace("/min", " (minor)").replace(":", " "), t["count"], t["reverse"], f(t["contribution_bits"])) for t in DEC[k]["top_edges"][:8])
    # cycles: two panels
    cyc = ""
    if R4:
        rows = []
        for k, c in (("bach", "Bach"), ("wjazzd", "WJazzD")):
            for t in R4[k]["circulation"]["top"][:5]:
                loop = t["loop"]; first = loop.split(">")[0]
                rows.append(r"%s & %s & %s & %s & %s & %s \\" % (c, _loop_tex(loop + ">" + first), f(t["j_C"], 5), f(t["A_C"], 2), f(t["term_bits"], 4), pct(t["share"])))
        cyc_rows = "\n".join(rows)
        nl = []
        for k, c in (("bach", "Bach"), ("wjazzd", "WJazzD")):
            for lab, v in R4[k]["named_loops"].items():
                closed = lab.split(">")[0] == lab.split(">")[-1]
                nl.append(r"%s & %s & %s & %d:%d & %d & %s \\" % (c, _loop_tex(lab), "closed" if closed else "open path", v["forward"], v["reverse"], v["works_with_forward"], f(v["log2_ratio"])))
        nl_rows = "\n".join(nl)
        cb, cw = R4["bach"]["circulation"], R4["wjazzd"]["circulation"]
        cyc = r"""\begin{table}[t]\centering\small
\caption{Panel A. Named progressions as contiguous windows within works (collapsed events). $N^+:N^-$ = complete forward and exactly reversed occurrences; the smoothed window ratio is $\log_2\frac{N^++0.5}{N^-+0.5}$, not the edge-product affinity $A_C$. An open path is not a cycle and has no affinity.}\label{tab:loops}
\begin{tabular}{lllrrr}\toprule corpus & progression & status & $N^+:N^-$ & works with forward & window ratio (bits) \\ \midrule
%(nl_rows)s
\bottomrule\end{tabular}\end{table}
\begin{table}[t]\centering\small
\caption{Panel B. Spanning-forest circulation terms of the stationary first-order fit ($\alpha=0.5$; maximum symmetric-traffic forest; return state printed). $\sigma=\sum_C j_C A_C$ closes with error %(ceb)s (Bach, $\sigma=%(sb)s$, %(ncb)s cycles) and %(cew)s (WJazzD, $\sigma=%(sw)s$, %(ncw)s cycles). Top-5 shares %(t5b)s and %(t5w)s, top-10 shares %(t10b)s and %(t10w)s. Terms, ranks and shares are basis dependent; only the total is invariant. Stationary $\sigma$ is a model quantity and is not comparable with the held-out scores of Table~\ref{tab:sup}.}\label{tab:cyc}
\begin{tabular}{llrrrr}\toprule corpus & fundamental cycle & $j_C$ & $A_C$ (bits) & $j_C A_C$ & share (\%%) \\ \midrule
%(cyc_rows)s
\bottomrule\end{tabular}\end{table}
""" % dict(sb=f(cb["sigma_stationary_bits"]), sw=f(cw["sigma_stationary_bits"]), ncb="{:,}".format(cb["n_cycles"]), ncw="{:,}".format(cw["n_cycles"]), ceb="%.1e" % cb["closure_err"], cew="%.1e" % cw["closure_err"],
           t5b=pct(cb["top5_share"]) + r"\%", t5w=pct(cw["top5_share"]) + r"\%", t10b=pct(cb["top10_share"]) + r"\%", t10w=pct(cw["top10_share"]) + r"\%", cyc_rows=cyc_rows, nl_rows=nl_rows)
    # vocabulary standardisation (restricted shared support)
    vs = M.get("VS"); vs_txt = ""
    if vs:
        vs_txt = (r"At $\alpha=0.5$, standardising to the %d inversion-closed chord-family strata shared by both corpora changes the inversion shares from %s\%% and %s\%% to %s\%% and %s\%%, reducing the gap from $%s$ to $%s$ ($E=%s$). This restricted shared-support standardisation therefore does not remove most of the observed contrast, but it excludes the %d jazz-only strata (two of which hold 48\%% of WJazzD events) and does not establish a vocabulary-independent corpus effect."
                  % (len(vs["shared_strata"]), pct(vs["R_bach"]), pct(vs["R_jazz"]), pct(vs["Rstar_bach"]), pct(vs["Rstar_jazz"]), f(vs["D_obs"]), f(vs["D_std"]), f(vs["E"], 2), len(vs["jazz_only"])))
    # alphabet matching
    alph_tbl = ""; alph_txt = ""; gap_lo = gap_hi = None
    if ALPH:
        rows = []; gaps = []; rb = []; rw = []; ew = []; shb = []; shw = []
        for a in AL:
            if a not in ALPH:
                continue
            for c, cn in (("bach", "Bach"), ("wjazzd", "WJazzD")):
                for k in sorted(ALPH[a][c]["k"], key=int):
                    r = ALPH[a][c]["k"][k]
                    rows.append(r"%s & %s & %s & %d & %d & %d & %s & %d & %s & %s & %s \\" % (cn, a, k, r["states_used"], r["fixed_fibers"], r["paired_fibers"], pct(r["retained_test_mass"]), r["groups_no_event"], f(r["Delta_inv"]), pct(r["share"]), f(r["group_LCB95"])))
                    (rb if c == "bach" else rw).append(r["retained_test_mass"]); (shb if c == "bach" else shw).append(r["share"])
                    if c == "wjazzd":
                        ew.append(r["groups_no_event"])
            for k in ALPH[a]["bach"]["k"]:
                gaps.append(100 * (ALPH[a]["bach"]["k"][k]["share"] - ALPH[a]["wjazzd"]["k"][k]["share"]))
        gap_lo, gap_hi = min(gaps), max(gaps)
        alph_tbl = r"""\begin{table}[t]\centering\scriptsize
\caption{Alphabet matching. In each training fold the state alphabet is restricted to the highest-mass complete inversion fibers up to target size $k$ (a fiber is never split; test counts are not used); edges with an endpoint outside the alphabet are dropped from training and test. Achieved size, fixed (self-inverse) and paired fibers, retained test-event mass, groups with no retained event, event-weighted residual $\bar\delta_{\mathrm{inv}}$ and its share of $\bar s_{C_{12}}$. The final column is the equal-group mean residual minus $1.645$ standard errors, in bits, giving a one-sided 95\%% lower bound; it is neither event-weighted nor a lower bound on the share.}\label{tab:alph}
\begin{tabular}{llrrrrrrrrr}\toprule corpus & $\alpha$ & target $k$ & achieved & fixed & paired & retained mass (\%%) & empty groups & $\bar\delta_{\mathrm{inv}}$ & share (\%%) & group LB \\ \midrule
%s
\bottomrule\end{tabular}\end{table}
""" % "\n".join(rows)
        alph_txt = (r"Across the %d $\alpha$-by-$k$ settings, retained-event shares are %s to %s\%% in Bach and %s to %s\%% in WJazzD, yielding positive gaps of %s to %s percentage points. Achieved alphabet sizes differ at every target, and retained mass ranges from %s to %s\%% in Bach and %s to %s\%% in WJazzD, with %d to %d empty WJazzD groups. This control shows that the gap does not disappear under these fold-local retained-event restrictions; it does not establish alphabet independence."
                    % (len(gaps), pct(min(shb)), pct(max(shb)), pct(min(shw)), pct(max(shw)), "%.1f" % gap_lo, "%.1f" % gap_hi, pct(min(rb)), pct(max(rb)), pct(min(rw)), pct(max(rw)), min(ew), max(ew)))
    # mode composition
    mode_tbl = ""; mode_txt = ""; MD = {}
    if MODE:
        rows = []
        og = []; cg = []; mg = []; bmin = []; bmaj = []; wstr = []
        for a in AL:
            C = MODE["alpha"][a]["corpora"]
            for c, cn in (("bach", "Bach"), ("wjazzd", "WJazzD")):
                r = C[c]
                for lab, x in (("major only", r["by_mode"]["major"]), ("minor only", r["by_mode"]["minor"]), ("observed mixture", r["observed"])):
                    rows.append(r"%s & %s & %s & %d & %s & %s & %s & %s & %s \\" % (cn, a, lab, x["events"], pct(x.get("kappa_support_share", 0)), f(x["sigma_C"]), f(x["Delta_inv"]), pct(x["share"]), f(x["group_LCB95"])))
                cw_ = r["common_weighted"]
                rows.append(r"%s & %s & common-mode weights & -- & -- & %s & %s & %s & -- \\" % (cn, a, f(cw_["sigma_C"]), f(cw_["Delta_inv"]), pct(cw_["share"])))
            og.append(100 * (C["bach"]["observed"]["share"] - C["wjazzd"]["observed"]["share"])); cg.append(100 * (C["bach"]["common_weighted"]["share"] - C["wjazzd"]["common_weighted"]["share"]))
            mg.append(100 * (C["bach"]["by_mode"]["major"]["share"] - C["wjazzd"]["by_mode"]["major"]["share"])); bmin.append(C["bach"]["by_mode"]["minor"]["share"]); bmaj.append(C["bach"]["by_mode"]["major"]["share"])
            wstr += [C["wjazzd"]["by_mode"]["major"]["share"], C["wjazzd"]["by_mode"]["minor"]["share"]]
        m5 = MODE["alpha"]["0.5"]; bm, wm = m5["corpora"]["bach"], m5["corpora"]["wjazzd"]
        MD = dict(og=(min(og), max(og)), cg=(min(cg), max(cg)), mg=(min(mg), max(mg)), bmin=(min(bmin), max(bmin)), bmaj=(min(bmaj), max(bmaj)), wstr=(min(wstr), max(wstr)), wmaj=m5["common_weights"]["major"], wmin=m5["common_weights"]["minor"])
        mode_tbl = r"""\begin{table}[t]\centering\scriptsize
\caption{Mode composition. Training uses all events; held-out events are split by the annotated mode of the source chord. $\kappa$-support = share of held-out edges whose inverted edge has positive training count under the mode-fixed action. Common-mode weights are fixed at %s\%% major and %s\%% minor for every $\alpha$. The final column is the equal-group mean residual minus $1.645$ standard errors, in bits, giving a one-sided 95\%% lower bound; it is not a lower bound on the share.}\label{tab:mode}
\begin{tabular}{lllrrrrrr}\toprule corpus & $\alpha$ & held-out events & $n$ & $\kappa$-support (\%%) & $\bar s_{C_{12}}$ & $\bar\delta_{\mathrm{inv}}$ & share (\%%) & group LB \\ \midrule
%s
\bottomrule\end{tabular}\end{table}
""" % (pct(MD["wmaj"], 2), pct(MD["wmin"], 2), "\n".join(rows))
        mode_txt = (r"Across $\alpha$, common-mode weighting reduces observed gaps of %.2f to %.2f percentage points to %.2f to %.2f points, while major-only gaps are $%.2f$ to $%.2f$ points. This is attenuation under a fixed representation, not evidence that mode mixture causally accounts for a specified fraction of a corpus effect. The $\kappa$-support column identifies a necessary estimator-specific support gate under the mode-fixed action: support is %s\%% in Bach major and %s\%% in Bach minor (%s\%% and %s\%% in WJazzD). It does not by itself explain residual magnitude, because contributions among supported events also differ (at $\alpha=0.5$ the mean residual per supported event is %s bits in Bach major, %s in Bach minor, %s in WJazzD major and %s in WJazzD minor)."
                    % (MD["og"][0], MD["og"][1], MD["cg"][0], MD["cg"][1], MD["mg"][0], MD["mg"][1], pct(bm["by_mode"]["major"]["kappa_support_share"]), pct(bm["by_mode"]["minor"]["kappa_support_share"]), pct(wm["by_mode"]["major"]["kappa_support_share"]), pct(wm["by_mode"]["minor"]["kappa_support_share"]),
                       f(bm["by_mode"]["major"]["Delta_inv"] / bm["by_mode"]["major"]["kappa_support_share"]), f(bm["by_mode"]["minor"]["Delta_inv"] / bm["by_mode"]["minor"]["kappa_support_share"]), f(wm["by_mode"]["major"]["Delta_inv"] / wm["by_mode"]["major"]["kappa_support_share"]), f(wm["by_mode"]["minor"]["Delta_inv"] / wm["by_mode"]["minor"]["kappa_support_share"])))
    ratio = [w[a]["sigma_D"] / b[a]["sigma_D"] for a in AL]
    bb_ = [b[a]["group_bootstrap"] for a in AL if b[a].get("group_bootstrap")]; wb_ = [w[a]["group_bootstrap"] for a in AL if w[a].get("group_bootstrap")]
    boot_txt = ""
    if bb_ and wb_:
        boot_txt = (r"A cluster bootstrap that resamples chorales or compositions with replacement (2{,}000 draws, held-out scores fixed, no refit) gives 5th percentiles of the event-weighted residual of %s to %s bits in Bach and %s to %s bits in WJazzD, and 90\%% percentile bands for the share of %s to %s\%% and %s to %s\%% respectively (Table~\ref{tab:inv}); the two share bands do not overlap at any $\alpha$."
                    % (f(min(x["Delta_inv_p05"] for x in bb_)), f(max(x["Delta_inv_p05"] for x in bb_)), f(min(x["Delta_inv_p05"] for x in wb_)), f(max(x["Delta_inv_p05"] for x in wb_)),
                       pct(min(x["share_p05"] for x in bb_)), pct(max(x["share_p95"] for x in bb_)), pct(min(x["share_p05"] for x in wb_)), pct(max(x["share_p95"] for x in wb_))))
    d = dict(nb=S["bach"]["works"], eb=INV["bach"]["alpha"]["0.5"]["N"], sb=S["bach"]["states"], nw=S["wjazzd"]["works"], ew=INV["wjazzd"]["alpha"]["0.5"]["N"], sw=S["wjazzd"]["states"], gw=INV["wjazzd"]["groups"],
             bb=f(min(SUP["bach"]["results"]["alpha=%s|r=1" % a]["retained_total"] for a in AL)), bb2=f(max(SUP["bach"]["results"]["alpha=%s|r=1" % a]["conditional"] for a in AL)),
             bw=f(min(SUP["wjazzd"]["results"]["alpha=%s|r=1" % a]["retained_total"] for a in AL)), bw2=f(max(SUP["wjazzd"]["results"]["alpha=%s|r=1" % a]["conditional"] for a in AL)),
             ib1=f(min(b[a]["Delta_inv"] for a in b)), ib2=f(max(b[a]["Delta_inv"] for a in b)), iw1=f(min(w[a]["Delta_inv"] for a in w)), iw2=f(max(w[a]["Delta_inv"] for a in w)),
             sh_b="%s to %s" % (pct(min(b[a]["residual_share"] for a in b)), pct(max(b[a]["residual_share"] for a in b))), sh_w="%s to %s" % (pct(min(w[a]["residual_share"] for a in w)), pct(max(w[a]["residual_share"] for a in w))),
             lb1=f(min(b[a]["group_LCB95"] for a in b)), lb2=f(max(b[a]["group_LCB95"] for a in b)), lw1=f(min(w[a]["group_LCB95"] for a in w)), lw2=f(max(w[a]["group_LCB95"] for a in w)),
             mmin=f(min(min(b[a]["group_LCB95"] for a in b), min(w[a]["group_LCB95"] for a in w))), invb=inv_rows("Bach", b), invw=inv_rows("WJazzD", w), unc=unc, supb=sup_rows("bach"), supw=sup_rows("wjazzd"),
             ub=pct(INVU["bach"]["alpha"]["0.5"]["residual_share"]), uw=pct(INVU["wjazzd"]["alpha"]["0.5"]["residual_share"]), rlo="%.1f" % min(ratio), rhi="%.1f" % max(ratio),
             epb=pct(S["bach"]["no_merge"]["endpoint_share"]), epw=pct(S["wjazzd"]["no_merge"]["endpoint_share"] or 0), edgb=edge_rows("bach"), edgw=edge_rows("wjazzd"), cyc=cyc, vs_txt=vs_txt, alph_tbl=alph_tbl, alph_txt=alph_txt, mode_tbl=mode_tbl, mode_txt=mode_txt, boot_txt=boot_txt,
             vsE=pct(vs["E"], 1) if vs else "--", gap_lo=("%.1f" % gap_lo) if gap_lo is not None else "--", gap_hi=("%.1f" % gap_hi) if gap_hi is not None else "--",
             cg_lo=("%.1f" % MD["cg"][0]) if MD else "--", cg_hi=("%.1f" % MD["cg"][1]) if MD else "--", bmin_lo=pct(MD["bmin"][0]) if MD else "--", bmin_hi=pct(MD["bmin"][1]) if MD else "--", bmaj=pct(MD["bmaj"][1]) if MD else "--", wstr_lo=pct(MD["wstr"][0]) if MD else "--", wstr_hi=pct(MD["wstr"][1]) if MD else "--",
             ceb=(("%.0e" % _ce) if (_ce := max(R4["bach"]["circulation"]["closure_err"], R4["wjazzd"]["circulation"]["closure_err"])) > 0 else "$0.0$") if R4 else "--")
    return r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}\usepackage{amsmath,amssymb,amsthm,booktabs,graphicx}\usepackage[hidelinks]{hyperref}
\newtheorem{lemma}{Lemma}\newtheorem{definition}{Definition}
\title{Allocating Held-Out Time-Reversal Scores to Inversion Distinctions in Bach Chorales and the Weimar Jazz Database}
\author{Anonymous}\date{Draft v3, September 2026}
\begin{document}\maketitle
\begin{abstract}
We estimate forward-versus-reversed held-out log scores for transposition-quotiented harmonic transitions in %(nb)d Bach chorales (music21 corpus, %(eb)d chord changes, %(sb)d key-relative states) and %(nw)d Weimar Jazz Database solos grouped into %(gw)d compositions (%(ew)d chord changes, %(sw)d states). In the bilateral-support analysis at $r=1$, retained-total and conditional scores across $\alpha\in\{0.1,0.5,1\}$ range from %(bb)s to %(bb2)s bits per transition in Bach and from %(bw)s to %(bw2)s bits per transition in WJazzD. A standard KL chain-rule identity gives both a nonnegative population decomposition and an exact eventwise decomposition of held-out log scores under an inversion quotient. For the inversion allocation, the event-weighted residual is %(ib1)s to %(ib2)s bits in Bach, or %(sh_b)s\%% of the event-weighted score; lower endpoints of two-sided 95\%% normal intervals for the equal-chorale mean are %(lb1)s to %(lb2)s bits. In WJazzD the corresponding values are %(iw1)s to %(iw2)s bits, %(sh_w)s\%%, and %(lw1)s to %(lw2)s bits for the equal-composition interval lower endpoints, all below the pre-specified 0.10-bit criterion. Three exploratory controls qualify the share contrast: at $\alpha=0.5$, a three-stratum shared-support standardisation reduces the gap by %(vsE)s\%%; across all $\alpha$, fold-local complete-fiber alphabet restrictions leave a %(gap_lo)s to %(gap_hi)s percentage-point gap among retained events; and common-mode weighting leaves %(cg_lo)s to %(cg_hi)s points, while major-only estimates reverse the ordering. At $\alpha=0.5$, stationary circulation reconstructions close to machine precision (reported error %(ceb)s); named-window counts show that one reported high-affinity cycle has one observed occurrence. This applies irreversibility diagnostics to harmonic transition laws, whereas Gonz\'alez-Espinoza, Mart\'inez-Mekler and Lacasa (2020) studied melodic visibility statistics; no theorem novelty is claimed.
\end{abstract}

\part*{I. Logic}
\section{Prior musical irreversibility and claim boundary}
Time irreversibility of music has been quantified before: Gonz\'alez-Espinoza, Mart\'inez-Mekler and Lacasa (2020) applied horizontal-visibility-graph statistics to scalar melodic note streams across 8{,}856 pieces. We quantify a different object, the reversal asymmetry of transposition-quotiented harmonic transition laws, and decompose it through inversion-sensitive, directed-edge and closed-cycle analyses. The quotient identity we use is a corollary of the KL chain rule and of exact coarse-graining results (Esposito, 2012; Teza and Stella, 2020); it is stated as a lemma because it fixes the estimand and prevents an incorrect quotient implementation, not as a contribution.

\section{Harmonic edge laws, reversal and bilateral-support estimands}
\begin{definition}A chord event is a key-relative 12-bit pitch-class mask with mode (the annotated tonic at pitch class 0); consecutive identical masks are collapsed to chord changes (an uncollapsed control is reported). A directed edge is a pair $(i,j)$ of consecutive states; $R(i,j)=(j,i)$ is reversal. For an edge law $\mu$, $\sigma(\mu)=D_{\mathrm{KL},2}(\mu\Vert R_*\mu)$ in bits.\end{definition}
Held-out scoring: for work-grouped folds, each held-out edge receives $d_{ij}=\log_2\frac{c_{ij}+\alpha}{c_{ji}+\alpha}$ from training counts; the event mean $\bar s$ is a predictive log score, not $\sigma$ of a law. Bilateral support restricts to edges with $c_{ij},c_{ji}\ge r$ in training; the retained-total estimand assigns excluded edges zero, the conditional estimand averages over retained edges only.

\paragraph{Smoothing and support convention.} In each fold the fitted support $E_f$ is the set of training edges together with their reversals. The fitted $C_{12}$ law is $\widehat P_f(e)=(c_f(e)+\alpha)/Z_f$ for $e\in E_f$ with $Z_f=\sum_{e\in E_f}(c_f(e)+\alpha)$, and $\alpha/Z_f$ for a held-out edge outside $E_f$. The $D_{12}$ law is obtained only by pushforward: $h_*\widehat P_f(z)=\sum_{e\in E_f,\,h(e)=z}\widehat P_f(e)$, and a held-out edge whose fiber meets $E_f$ nowhere receives $\widehat P_f(e)+\widehat P_f(\kappa e)$. Pseudocounts are therefore never added per fiber cell. The $\kappa$-support of a held-out edge $e$ is the indicator that $\kappa e\in E_f$ and $\kappa e\neq e$.

\paragraph{Folds and inference.} Groups (chorales in Bach, compositions in WJazzD) are sorted by the SHA-256 of their identifier and assigned round-robin to five folds, so performances of one composition never cross folds. Corpus scores weight held-out events equally. Group inference first averages the score within each group and then weights groups equally; the pre-specified interval is the group mean minus $1.96$ standard errors (the lower endpoint of a two-sided 95\%% normal interval, Table~\ref{tab:inv}); the exploratory controls report the group mean minus $1.645$ standard errors (a one-sided 95\%% lower bound, Tables~\ref{tab:alph} and \ref{tab:mode}). Because the weightings differ, a group bound need not lie below the event-weighted corpus score. A group with no retained held-out event under an alphabet restriction is excluded from the group mean and counted in the table.

\section{Diagonal $C_{12}$ quotient}
Let $G=\mathbb Z_{12}$ act diagonally on edges, $T_g(i,j)=(gi,gj)$, and let reversal commute with the action. For the symmetrised law $\mu^G=\frac{1}{12}\sum_g (T_g)_*\mu$ and the orbit map $q$, $\sigma(\mu^G)=\sigma(q_*\mu)$ (KL chain rule for the statistic $q$; both symmetrised laws are uniform within each orbit, so the conditional term vanishes). Our key-relative representation is the tonic-anchored orbit representative; an exact unsmoothed check on the common support gives identity gap $0.0$ in Bach. Smoothed plug-ins differ because pseudocounts must be pushed forward, not added per cell.

\section{Exact $C_{12}\rightarrow D_{12}$ allocation}
\begin{lemma}[standard KL chain-rule corollary]Let $h$ be a quotient commuting with reversal, $P$ an edge law and $Q=R_*P$. Then
\[D_{\mathrm{KL}}(P\Vert Q)=D_{\mathrm{KL}}(h_*P\Vert h_*Q)+\sum_z (h_*P)(z)\,D_{\mathrm{KL}}\big(P(\cdot\mid z)\Vert Q(\cdot\mid z)\big).\]
The second population term is nonnegative. For a fold-fitted predictive pair $(\widehat P_f,\widehat Q_f)$ the corresponding held-out identity is eventwise,
\[\log_2\frac{\widehat P_f(x)}{\widehat Q_f(x)}=\log_2\frac{h_*\widehat P_f(hx)}{h_*\widehat Q_f(hx)}+\log_2\frac{\widehat P_f(x\mid hx)}{\widehat Q_f(x\mid hx)},\]
and its held-out residual is not guaranteed nonnegative by the theorem; positivity and its group bounds are empirical results.\end{lemma}
Here $\kappa$ is mode-conditioned pitch-class inversion ($p\mapsto -p$, mode fixed) and $h$ identifies an edge with its inversion. We write $\bar s_{C_{12}}=\bar s_{D_{12}}+\bar\delta_{\mathrm{inv}}$ for the held-out event means. Under the stated estimator and mode-fixed action, $\bar\delta_{\mathrm{inv}}$ is the held-out residual allocated to distinctions within $h$-fibers; an event contribution can be nonzero only if its inverted edge has positive training mass. The mode-fixed action is one valid $D_{12}$ action, not the unique music-theoretic one.

\section{Detailed balance, cycle affinities and circulation}
For a stationary first-order chain with flow $F_{ij}=\pi_iP_{ij}$, $\sigma=\sum_{i<j}(F_{ij}-F_{ji})\log_2(F_{ij}/F_{ji})$, and $\sigma=0$ iff detailed balance iff every cycle affinity $A_C=\sum_{(i,j)\in C}\log_2(F_{ij}/F_{ji})$ vanishes (Kolmogorov, 1936). With a spanning forest, $\sigma=\sum_C j_C A_C$ over fundamental cycles; individual terms are basis dependent, the total is not. A loop's affinity is a force, not a contribution: it is reported together with its circulation and with contiguous window counts.

\part*{II. Experiment}
\section{Corpora, states, grouped folds and pre-specification}
Bach: %(nb)d chorales, %(eb)d collapsed chord changes, %(sb)d states; folds by chorale. WJazzD: %(nw)d solos in %(gw)d compositions, %(ew)d collapsed chord changes, %(sw)d states; folds by composition. Chord types are triads (Bach, music21 quality) and thirteen jazz symbol templates (WJazzD). State alphabets and annotation pipelines differ, so all cross-corpus differences reported below are descriptive and conditional on these representations. The conjunctive decision rule required the equal-group mean residual minus $1.96$ standard errors, the lower endpoint of a two-sided 95\%% normal interval, to exceed $0.10$ bits in both corpora at every $\alpha\in\{0.1,0.5,1\}$; it also required closure error below $10^{-12}$. The rule was fixed in the dated analysis plan of 2 September 2026 before the inversion allocation was computed; it was recorded in the project ledger, not deposited in a public registry, so we call it pre-specified rather than preregistered. The vocabulary, alphabet, mode, bootstrap and cycle analyses are exploratory.

\section{Support-controlled held-out irreversibility}
\begin{table}[t]\centering\small\caption{Held-out reversal asymmetry by bilateral support (bits per transition). rho = share of held-out events on edges observed in both directions in training; retained-total assigns excluded edges zero; LB = work- (Bach) or composition- (WJazzD) level 95\%% lower bound.}\label{tab:sup}
\begin{tabular}{lrrrrrr}\toprule $\alpha$ & support & $\rho$ (\%%) & retained-total & conditional & LB & works with no retained edge \\ \midrule
\multicolumn{7}{l}{\emph{Bach chorales}} \\
%(supb)s
\multicolumn{7}{l}{\emph{WJazzD}} \\
%(supw)s
\bottomrule\end{tabular}\end{table}
Endpoint (piece boundary) marginals contribute %(epb)s\%% (Bach) and %(epw)s\%% (WJazzD) of the plug-in $\sigma$; merging states with fewer than five occurrences changes nothing. Figure~\ref{fig:sup} shows the bilateral-support curves.
\begin{figure}[t]\centering\includegraphics[width=\linewidth]{figs/fig2_support.pdf}\caption{Bilateral-support control: retained-total (solid) and conditional (dashed) scores across support thresholds and smoothing.}\label{fig:sup}\end{figure}

\section{Inversion allocation and group inference}
\begin{table}[t]\centering\scriptsize\caption{Exact eventwise allocation of held-out reversal log scores (bits per transition). Per-event closure error $\le 9\times10^{-16}$. The barred scores, residual and share are event-weighted. The group mean is unweighted over chorales or compositions, and ``95\%% CI lower'' equals the group mean minus $1.96$ standard errors, the pre-specified lower endpoint of a two-sided 95\%% normal interval. The last two columns are from a cluster bootstrap over groups (2{,}000 draws, no refit): the 5th percentile of the event-weighted residual and the 5th to 95th percentile band of the share.}\label{tab:inv}
\begin{tabular}{llrrrrrrrr}\toprule corpus & $\alpha$ & $\bar s_{C_{12}}$ & $\bar s_{D_{12}}$ & $\bar\delta_{\mathrm{inv}}$ & share (\%%) & group mean & 95\%% CI lower & boot. $\bar\delta$ p05 & boot. share (\%%) \\ \midrule
%(invb)s
%(invw)s
%(unc)s
\bottomrule\end{tabular}\end{table}
The pre-specified conjunctive rule fails: the minimum interval lower endpoint is $%(mmin)s$ (WJazzD, $\alpha=1$). Bach exceeds the 0.10-bit interval-lower-endpoint criterion at every $\alpha$ for collapsed events; its collapsed-event share is %(sh_b)s\%%, and its uncollapsed share is %(ub)s\%% at the only tested value, $\alpha=0.5$. WJazzD's collapsed share is %(sh_w)s\%%, and its uncollapsed share is %(uw)s\%% at $\alpha=0.5$. The absolute residual ranges overlap (%(ib1)s to %(ib2)s versus %(iw1)s to %(iw2)s bits), while WJazzD's inversion-invariant score is %(rlo)s to %(rhi)s times Bach's; both the residual numerator and the score denominator determine the reported shares. %(boot_txt)s
\begin{figure}[t]\centering\includegraphics[width=\linewidth]{figs/fig3_decomposition.pdf}\caption{Exact allocation of held-out reversal scores into inversion-invariant and inversion-resolving parts.}\end{figure}
\begin{figure}[t]\centering\includegraphics[width=\linewidth]{figs/fig4_lcb.pdf}\caption{Group-level $\bar\delta_{\mathrm{inv}}$ with 95\%% interval lower endpoints; dashed = pre-specified 0.10 bits.}\end{figure}

\section{Controls on the share contrast: vocabulary, alphabet and mode}
%(vs_txt)s
%(alph_tbl)s
%(alph_txt)s
%(mode_tbl)s
%(mode_txt)s Taken together, the gap persists under the limited shared-stratum and retained-event alphabet controls, but it is strongly mode-dependent under the chosen action. Under this representation, within-fiber inversion distinctions account for %(bmin_lo)s to %(bmin_hi)s\%% of held-out reversal score in Bach minor, about %(bmaj)s\%% in Bach major, and %(wstr_lo)s to %(wstr_hi)s\%% across WJazzD mode strata; these are corpus-conditional descriptive results, not a genre effect.
\begin{figure}[t]\centering\includegraphics[width=\linewidth]{figs/fig7_controls.pdf}\caption{Left: inversion-resolving share under fold-local alphabet matching. Right: share by held-out mode, observed mixture and common-mode weighting ($\alpha=0.5$).}\end{figure}

\section{Directed edges, named windows and stationary cycle circulation}
\begin{table}[t]\centering\small\caption{Top directed edges by plug-in contribution to $\sigma$ (forward and reverse counts).}\label{tab:edges}
\begin{tabular}{lrrr}\toprule edge & forward & reverse & bits \\ \midrule
\multicolumn{4}{l}{\emph{Bach}} \\
%(edgb)s
\multicolumn{4}{l}{\emph{WJazzD}} \\
%(edgw)s
\bottomrule\end{tabular}\end{table}
%(cyc)s
\begin{figure}[t]\centering\includegraphics[width=\linewidth]{figs/fig5_edges.pdf}\caption{Top directed edges by contribution.}\end{figure}
\begin{figure}[t]\centering\includegraphics[width=\linewidth]{figs/fig6_cycles.pdf}\caption{Fundamental-cycle terms of the stationary fit.}\end{figure}
The exploratory secondary-dominant cycle $II^7\rightarrow V^7\rightarrow I^{maj7}$ has the largest edge-product affinity in WJazzD but is supported by one complete forward window in one composition, whereas the conventional $ii^7$ cycle occurs 54 times in 17 compositions and is never observed in reverse (Table~\ref{tab:loops}). In this spanning-forest basis Bach's stationary circulation is more concentrated than WJazzD's among the five largest terms (top-5 shares in Table~\ref{tab:cyc}); these percentages are basis dependent and do not mean that five named progressions explain those fractions of corpus-level asymmetry.

\section{Limitations and replication}
These results describe two annotated corpora under fixed event definitions, chord templates, key estimates (machine-estimated for Bach, annotated for WJazzD), smoothing rules, and a mode-conditioned inversion that leaves the binary mode covariate fixed. Because the quotient fibers and $\kappa$-support are induced by the selected action, another musically defensible inversion action may change both the support gate and the allocation; no action-sensitivity analysis is reported. The held-out quantities are predictive log scores, not physical entropy-production estimates. State alphabets and annotation pipelines differ across corpora and no genre effect is identified. The vocabulary standardisation covers only three shared strata and excludes 29 jazz-only strata. The stationary cycle analysis uses $\alpha=0.5$, which gives positive fitted flow to pseudocount-supported edges; individual fundamental cycles, ranks and shares depend on the spanning forest and smoothing choice. Named-window counts establish corpus occurrence, not functional or causal harmonic syntax. Code, derived counts, fold assignments and the JSON manifest from which every table regenerates are released in an anonymised repository supplied to the editor.

\section*{References}
\small
Esposito, M. (2012). Stochastic thermodynamics under coarse graining. Physical Review E 85, 041125.\\
Gonz\'alez-Espinoza, A., Mart\'inez-Mekler, G., Lacasa, L. (2020). Arrow of time across five centuries of classical music. Physical Review Research 2, 033166 (arXiv:2004.07307).\\
Kolmogorov, A. N. (1936). Zur Theorie der Markoffschen Ketten. Mathematische Annalen 112, 155--160.\\
Teza, G., Stella, A. L. (2020). Exact coarse graining preserves entropy production out of equilibrium. Physical Review Letters 125, 110601.
\end{document}
""" % d
