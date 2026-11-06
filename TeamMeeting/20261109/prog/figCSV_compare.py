# -*- coding: utf-8 -*-
"""
figCSV_compare.py : AgMIP 形式の各モデルの出力（CSV）と AIM-ALPHA を、卒論（中間報告）の4つの効果で比べる。
  Xia et al. の Excel は使わない。
  入力 : ../data/モデル間比較用model_output/{AIM,ENVISAGE,GCAM,GLOBIOM,IMPACT}.csv（PROD, CONS, XPRP）
         ../data/all_scenario_World.gdx（qs_load, qd_load, pp_load, cal_load, qdFood_load, pop_load, cty_reg_map）
  出力 : ../output/figCSV_<VAR>_world.png            VAR = PROD, CONS, XPRP（パネル：CRP と5作物）
         ../output/figCSV_<VAR>_<ITEM>_region.png     ITEM = CRP, WHT, RIC, CGR, OSD, SGC（パネル：AgMIP 17地域）
         ../data/csv_compare.csv（図の数値）、../data/kcal_factor.csv、../data/missing_cty.csv
  指標 :
    PROD（生産量）・CONS（国内利用）：カロリーベース [PJ]
        E [PJ] = Q [1000 t] × f [kcal/t] × 1000 × 4184 [J/kcal] × 1e-15
        f（作物ごと）= Σ cal_load / Σ qdFood_load × 1000（AIM-ALPHA、BaU_NoCC_woO3、2020 年、世界、
          cal_load と qdFood_load の両方に値がある国と品目の組）。全モデル・全地域で同じ f を使う。
        AIM-ALPHA は qs_load（PROD）、qd_load（CONS）を AgMIP の品目と地域に足してから換算する。
    XPRP（生産者価格）：価格指数の効果 [%] = (P_対象,2050 − P_参照,2050) ÷ P_Baseline,2020 × 100
        作物別・地域別の価格は各モデルの CSV の値をそのまま使う。CRP は、作物別の価格をその年の生産量（重量）で
        重み付けして平均する。AIM-ALPHA は国×品目の pp_load を、その年の qs_load で重み付けして平均する。
  効果（卒論の定義。オゾンは気候に含める）：
    (1) RCP26 − Baseline  (2) RCP26_MITI − RCP26  (3) RCP26_MITI − Baseline  (4) RCP70 − Baseline
"""
import os, io, time, textwrap
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GDX = os.path.join(ROOT, "data", "all_scenario_World.gdx")
MDIR = os.path.join(ROOT, "data", "モデル間比較用model_output")
DDIR = os.path.join(ROOT, "data")
FIGD = os.path.join(ROOT, "output")
os.makedirs(FIGD, exist_ok=True)

# ---------------------------------------------------------------- 定義
XIA = ["AIM", "ENVISAGE", "GCAM", "GLOBIOM", "IMPACT"]
MODELS = XIA + ["AIM-ALPHA"]
LABEL = {"AIM": "AIM-Hub"}
# シナリオ。オゾンは _W_CH4 なし（CH4 濃度をシナリオで変えていないもの）を使う。
# AIM-ALPHA の wO3 の外生収量へのオゾンの影響が、_W_CH4 なしのシナリオと一致したため（2026-11-06 に確認）。
SC = {"Baseline": "BAU_NoCC", "RCP26": "OZBAU_RCP26",
      "RCP26_MITI": "OZBAU_MITI_RCP26", "RCP70": "OZBAU"}
def scen(m, k):
    s = SC[k]
    if m == "GLOBIOM":
        return s.replace("_W_CH4", "")          # GLOBIOM には _W_CH4 が無い
    if m == "ENVISAGE":
        return s.replace("_W_CH4", "_w_CH4")    # ENVISAGE は小文字
    return s
SC_ALPHA = {"Baseline": "SSP2_BaU_CS_NoCC_woO3", "RCP26": "SSP2_BaU_CS_RCP26_wO3",
            "RCP26_MITI": "SSP2_500C_CS_RCP26_wO3", "RCP70": "SSP2_BaU_CS_RCP70_wO3"}
EFF = {"(1)": ("RCP26", "Baseline"), "(2)": ("RCP26_MITI", "RCP26"),
       "(3)": ("RCP26_MITI", "Baseline"), "(4)": ("RCP70", "Baseline")}
EFFS = list(EFF)
EFF_LINE = ("(1) Climate change (SSP2-2.6)   (2) Mitigation (SSP2-2.6)   "
            "(3) Combined effect (SSP2-2.6)   (4) Climate change (SSP2-7.0)")
REG17 = ["CAN", "USA", "BRA", "OSA", "FSU", "EUR", "MEN", "SSA", "CHN", "IND", "SEA", "OAS", "ANZ",
         "NAM", "OAM", "AME", "SAS"]
BASE13 = REG17[:13]
NO_GCAM_MEDIAN = ["EUR", "MEN", "AME"]
# GLOBIOM の CSV には、メタン濃度を固定したオゾンのシナリオが無い（OZBAU などは中身がメタン濃度を変えた方）。
# そのため、白抜きの記号で示し、中央値からは外す。
HOLLOW = ["GLOBIOM"]
ITEMS5 = ["WHT", "RIC", "CGR", "OSD", "SGC"]
NAME = {"CRP": "Crops (CRP)", "WHT": "Wheat", "RIC": "Rice", "CGR": "Coarse grains", "OSD": "Oilseeds", "SGC": "Sugar crops"}
# AgMIP の品目 → AIM-ALPHA の品目（define/AgMIP_c.map）
A2C = {"WHT": ["wht"], "RIC": ["rce"], "CGR": ["mze", "crl"], "OSD": ["ocr"], "SGC": ["sgr"],
       "VFN": ["str", "pls", "nut", "vgt", "frt"], "OCR": ["stm", "spc"]}
A2C["OCR_AIM"] = A2C["VFN"] + A2C["OCR"]     # AIM-Hub の OCR は VFN を含む
# CRP を作る品目（畜産・加工品・エネルギー作物・繊維作物・その他は入れない）
CRP_Q = {"AIM": ["WHT", "RIC", "CGR", "OSD", "SGC", "OCR"],
         "ENVISAGE": ["WHT", "RIC", "CGR", "OSD", "SGC", "VFN", "OCR"],
         "GCAM": ["WHT", "RIC", "CGR", "OSD", "SGC", "VFN", "OCR"],
         "GLOBIOM": ["WHT", "RIC", "CGR", "OSD", "SGC", "VFN", "OCR"],
         "IMPACT": ["WHT", "RIC", "CGR", "OSD", "SGC", "VFN", "OCR"]}
CRP_P = dict(CRP_Q, GCAM=["WHT", "RIC", "CGR", "OSD", "SGC", "OCR",
                          "VFN|FRU", "VFN|LEG", "VFN|NUT", "VFN|RTB", "VFN|VEG"])   # GCAM の VFN の価格は内訳のみ
BASEY = {m: 2020 for m in XIA}; BASEY["ENVISAGE"] = 2021      # ENVISAGE の CSV に 2020 年は無い
J = 4184.0

# ---------------------------------------------------------------- AIM-ALPHA の読み込み
import gamspy_base, gams.transfer as gt
gc = gt.Container(system_directory=gamspy_base.directory)
SYM = ["qs_load", "qd_load", "pp_load", "cal_load", "qdFood_load", "pop_load", "cty_reg_map"]
gc.read(GDX, symbols=SYM)
def rec(n, cols):
    d = gc[n].records.copy(); d.columns = cols
    for c in cols[:-1]:
        d[c] = d[c].astype(str)
    return d
qs = rec("qs_load", ["s", "c", "cty", "y", "v"]); qd = rec("qd_load", ["s", "c", "cty", "y", "v"])
pp = rec("pp_load", ["s", "c", "cty", "y", "v"]); cal = rec("cal_load", ["s", "c", "cty", "y", "v"])
qf = rec("qdFood_load", ["s", "c", "cty", "y", "v"]); pop = rec("pop_load", ["s", "cty", "y", "v"])
crm = gc["cty_reg_map"].records.iloc[:, :2].astype(str); crm.columns = ["cty", "reg"]
REGMEM = {r: set(crm[crm.reg == r].cty) for r in REG17}
REGMEM["WLD"] = set(crm[crm.reg == "World"].cty)
REGS = ["WLD"] + REG17

# カロリー換算係数 f [kcal/t]
fb = cal.merge(qf, on=["s", "c", "cty", "y"], suffixes=("_cal", "_q"))
fb = fb[(fb.s == SC_ALPHA["Baseline"]) & (fb.y == "2020")]
KF = {i: fb[fb.c.isin(cs)].v_cal.sum() / fb[fb.c.isin(cs)].v_q.sum() * 1000 for i, cs in A2C.items()}
pd.DataFrame({"agmip_item": list(KF), "alpha_items": ["+".join(A2C[i]) for i in KF],
              "kcal_per_t": list(KF.values())}).to_csv(os.path.join(DDIR, "kcal_factor.csv"), index=False, encoding="utf-8-sig")
def to_pj(q1000t, item):
    return q1000t * KF[item] * 1000 * J * 1e-15

rows = []   # Model, VAR, ITEM, Region, effect, value
# ---------------------------------------------------------------- 各モデル（CSV）
check = []
for m in XIA:
    d = pd.read_csv(os.path.join(MDIR, m + ".csv"), low_memory=False)
    keep = {scen(m, k): k for k in SC}
    d = d[d.Scenario.isin(keep) & d.Region.isin(REGS) & d.Variable.isin(["PROD", "CONS", "XPRP"])
          & d.Year.isin([BASEY[m], 2050]) & ~d.Unit.str.contains("dm", case=False)].copy()
    d["k"] = d.Scenario.map(keep)
    v = d.set_index(["Variable", "k", "Year", "Region", "Item"]).Value
    get = lambda var, k, y, r, i: v.get((var, k, y, r, i), np.nan)
    # 数量（カロリーベース）
    for var in ["PROD", "CONS"]:
        for r in REGS:
            def qk(k, item):
                if item == "CRP":
                    return sum(to_pj(np.nan_to_num(get(var, k, 2050, r, i)),
                                     "OCR_AIM" if (m == "AIM" and i == "OCR") else i) for i in CRP_Q[m])
                return to_pj(np.nan_to_num(get(var, k, 2050, r, item)), item)
            for item in ["CRP"] + ITEMS5:
                for e, (t, ref) in EFF.items():
                    rows.append(dict(Model=m, VAR=var, ITEM=item, Region=r, effect=e, value=qk(t, item) - qk(ref, item)))
    # 価格
    for r in REGS:
        def P(k, y, item):
            if item != "CRP":
                return get("XPRP", k, y, r, item)
            p = np.array([get("XPRP", k, y, r, i) for i in CRP_P[m]])
            q = np.array([get("PROD", k, y, r, i) for i in CRP_P[m]])
            ok = ~np.isnan(p) & ~np.isnan(q) & (q > 0)
            return (p[ok] * q[ok]).sum() / q[ok].sum()
        for item in ["CRP"] + ITEMS5:
            base = P("Baseline", BASEY[m], item)
            for e, (t, ref) in EFF.items():
                rows.append(dict(Model=m, VAR="XPRP", ITEM=item, Region=r, effect=e,
                                 value=(P(t, 2050, item) - P(ref, 2050, item)) / base * 100))
        if r == "WLD":   # 照合：CRP の価格を CSV の XPRP CRP と比べる（同じ品目なら一致するはず）
            check.append(dict(Model=m, P_CRP_own=P("Baseline", BASEY[m], "CRP"),
                              P_CRP_csv=get("XPRP", "Baseline", BASEY[m], "WLD", "CRP")))

# ---------------------------------------------------------------- AIM-ALPHA
C2A = {c: i for i in ["WHT", "RIC", "CGR", "OSD", "SGC", "VFN", "OCR"] for c in A2C[i]}
RL = pd.DataFrame([(c, r) for r in REGS for c in REGMEM[r]], columns=["cty", "Region"])
K = {v: k for k, v in SC_ALPHA.items()}
for var, src in [("PROD", qs), ("CONS", qd)]:
    x = src[(src.y == "2050") & src.s.isin(K) & src.c.isin(C2A)].copy()
    x["k"] = x.s.map(K); x["item"] = x.c.map(C2A)
    g = x.merge(RL, on="cty").groupby(["k", "Region", "item"]).v.sum()
    for r in REGS:
        def qk(k, item):
            if item == "CRP":
                return sum(to_pj(g.get((k, r, i), 0.0), i) for i in ["WHT", "RIC", "CGR", "OSD", "SGC", "VFN", "OCR"])
            return to_pj(g.get((k, r, item), 0.0), item)
        for item in ["CRP"] + ITEMS5:
            for e, (t, ref) in EFF.items():
                rows.append(dict(Model="AIM-ALPHA", VAR=var, ITEM=item, Region=r, effect=e, value=qk(t, item) - qk(ref, item)))
pq = pp.merge(qs, on=["s", "c", "cty", "y"], suffixes=("_p", "_q"))
pq = pq[pq.y.isin(["2020", "2050"]) & pq.s.isin(K) & pq.c.isin(C2A) & (pq.v_q > 0)].copy()
pq["k"] = pq.s.map(K); pq["item"] = pq.c.map(C2A); pq["pv"] = pq.v_p * pq.v_q
pq = pq.merge(RL, on="cty")
gi = pq.groupby(["k", "y", "Region", "item"])[["pv", "v_q"]].sum()
gc_ = pq.groupby(["k", "y", "Region"])[["pv", "v_q"]].sum()
for r in REGS:
    def P(k, y, item):
        try:
            z = gc_.loc[(k, y, r)] if item == "CRP" else gi.loc[(k, y, r, item)]
        except KeyError:
            return np.nan
        return z.pv / z.v_q
    for item in ["CRP"] + ITEMS5:
        base = P("Baseline", "2020", item)
        for e, (t, ref) in EFF.items():
            rows.append(dict(Model="AIM-ALPHA", VAR="XPRP", ITEM=item, Region=r, effect=e,
                             value=(P(t, "2050", item) - P(ref, "2050", item)) / base * 100))
res = pd.DataFrame(rows)
res.to_csv(os.path.join(DDIR, "csv_compare.csv"), index=False, encoding="utf-8-sig")
print(pd.DataFrame(check).to_string())
print("kcal/t:", {k: round(v) for k, v in KF.items()})

# ---------------------------------------------------------------- 欠損（AIM-ALPHA で 2015 年より後の値が無い国）
simulated = set(qd.cty)
p15 = pop[(pop.s == SC_ALPHA["Baseline"]) & (pop.y == "2015")].set_index("cty").v
miss = []
for r in REGS:
    cs = REGMEM[r]; ms = sorted(c for c in cs if c not in simulated)
    if r != "WLD":
        ms = [c for c in ms if c in set().union(*(REGMEM[b] for b in BASE13))]
    a = p15.reindex(sorted(cs)).sum(); b = p15.reindex(ms).sum()
    miss.append(dict(Region=r, countries=" ".join(ms), share_pop2015=b / a * 100 if a else np.nan,
                     named=" ".join(c for c in ms if p15.get(c, 0) >= 0.5),
                     n_small=sum(1 for c in ms if c in p15.index and p15[c] < 0.5),
                     no_pop=" ".join(c for c in ms if c not in p15.index)))
miss = pd.DataFrame(miss).set_index("Region")
miss.to_csv(os.path.join(DDIR, "missing_cty.csv"), encoding="utf-8-sig")
DAGGER = [r for r in REG17 if miss.loc[r, "countries"]]
def miss_line(r):
    x = miss.loc[r]
    parts = []
    if x.named:
        parts.append(", ".join(x.named.split()))
    if x.n_small:
        parts.append(f"{x.n_small} small territories (< 0.5 million people)")
    if x.no_pop:
        parts.append("no population data: " + ", ".join(x.no_pop.split()))
    return f"{r} {x.share_pop2015:.1f}%: " + "; ".join(parts)
MISS_TEXT = ("† Countries not simulated in AIM-ALPHA (no data after 2015; excluded from its regional totals; "
             "share of the regional population in 2015):  "
             + "  |  ".join(miss_line(r) for r in BASE13 if r in DAGGER)
             + f";  World {miss.loc['WLD', 'share_pop2015']:.1f}%.  NAM, OAM, AME and SAS include the countries of their member regions.")
# 図の注釈：計算方法と元の指標名は処理の流れの図（doc/flow_figCSV_compare.drawio）に書いたので、
# ここには例外の扱い（欠損・中央値から外したもの・単位や年の違い）だけを書く。
COMMON_NOTES = [
    "GLOBIOM (hollow symbol) is not included in the median: its output files contain only ozone scenarios with scenario-specific CH4 concentrations "
    "(the other models and AIM-ALPHA: fixed CH4 concentrations).",
    "GCAM is excluded from the median for EUR, MEN and AME: Turkey is included in EUR instead of MEN in GCAM (inferred from its population by region).  "
    "Regional definitions may differ slightly among models.",
    "AIM-Hub has no VFN; it is included in its OCR.",
    MISS_TEXT,
    "Taiwan is not included in AIM-ALPHA (no population and GDP projections).",
]
VAR_NOTES = {
    "PROD": [],
    "CONS": [],
    "XPRP": ["ENVISAGE: prices are indices (2014 = 1), and its base year is 2021 instead of 2020.  "
             "Points are missing where there is no production (e.g., rice in CAN)."],
}
YLAB = {"PROD": "Change in 2050 (PJ)",
        "CONS": "Change in 2050 (PJ)",
        "XPRP": "Change in 2050\n(% of the 2020 Baseline price)"}
TITLE = {"PROD": "Production", "CONS": "Domestic use", "XPRP": "Producer price"}

# ---------------------------------------------------------------- 図
fams = {f.name for f in font_manager.fontManager.ttflist}
FONT = next((f for f in ["Times New Roman", "TeX Gyre Termes", "Liberation Serif"] if f in fams), "serif")
plt.rcParams.update({"font.family": FONT, "font.size": 7, "axes.linewidth": 0.4,
                     "xtick.major.width": 0.4, "ytick.major.width": 0.4,
                     "axes.spines.top": False, "axes.spines.right": False})
CM = 1 / 2.54
MARK = {"AIM": "o", "ENVISAGE": "^", "GCAM": "s", "GLOBIOM": "P", "IMPACT": "X", "AIM-ALPHA": "D"}
COLR = {m: "0.35" for m in XIA}; COLR["AIM-ALPHA"] = "#C0504D"
OFF = dict(zip(MODELS, np.linspace(-0.28, 0.28, len(MODELS))))

def wrap(lines, width):
    out = []
    for ln in lines:
        out += textwrap.wrap(ln, width=width, subsequent_indent="  ", break_on_hyphens=False)
    return "\n".join(out)

def save(fig, name):
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=600); plt.close(fig)
    for _ in range(10):
        try:
            with open(os.path.join(FIGD, name), "wb") as f:
                f.write(buf.getvalue())
            return
        except OSError:
            time.sleep(2)
    raise OSError(name)

def panel(ax, d, region, small=False):
    xx = np.arange(len(EFFS))
    med_models = [m for m in XIA if m not in HOLLOW and not (m == "GCAM" and region in NO_GCAM_MEDIAN)]
    med = d[d.Model.isin(med_models)].groupby("effect").value.median().reindex(EFFS)
    ax.bar(xx, med.values, width=0.75, color="0.88", zorder=1)
    for m in MODELS:
        s = d[d.Model == m].set_index("effect").value.reindex(EFFS)
        if m in HOLLOW:
            ax.scatter(xx + OFF[m], s.values, marker=MARK[m], s=7 if small else 12, facecolors="none",
                       edgecolors=COLR[m], linewidths=0.5, zorder=3)
        else:
            ax.scatter(xx + OFF[m], s.values, marker=MARK[m], s=6 if small else 10, color=COLR[m], linewidths=0, zorder=3)
    ax.axhline(0, color="black", lw=0.4, zorder=2)
    ax.set_xticks(xx); ax.set_xticklabels(EFFS, fontsize=5.5 if small else 6.5)
    ax.set_xlim(-0.6, len(xx) - 0.4)
    ax.tick_params(axis="y", labelsize=5.5 if small else 6)

def legend(fig, y):
    h = [Line2D([], [], ls="", marker=MARK[m], color=COLR[m], ms=3.5, label=LABEL.get(m, m) + (" (not in median)" if m in HOLLOW else ""),
                markerfacecolor="none" if m in HOLLOW else COLR[m], markeredgewidth=0.5 if m in HOLLOW else 0) for m in MODELS]
    h.append(Patch(color="0.88", label="Median (excl. AIM-ALPHA, GLOBIOM)"))
    fig.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, y), ncol=7, frameon=False,
               fontsize=6, handletextpad=0.2, columnspacing=0.7)

for var in ["PROD", "CONS", "XPRP"]:
    notes = VAR_NOTES[var] + COMMON_NOTES
    # 世界
    fig, axs = plt.subplots(2, 3, figsize=(16 * CM, 15 * CM))
    for ax, item in zip(axs.flat, ["CRP"] + ITEMS5):
        panel(ax, res[(res.VAR == var) & (res.ITEM == item) & (res.Region == "WLD")], "WLD")
        ax.set_title(NAME[item], fontsize=7, pad=2)
        ax.set_ylabel(YLAB[var], fontsize=6)
    fig.text(0.5, 0.995, f"{TITLE[var]}: World", ha="center", va="top", fontsize=8)
    legend(fig, 0.975)
    fig.text(0.5, 0.94, EFF_LINE, ha="center", va="top", fontsize=6.5)
    fig.text(0.01, 0.005, wrap(notes, 185), ha="left", va="bottom", fontsize=4.6)
    fig.tight_layout(rect=(0, 0.16, 1, 0.925), h_pad=0.8, w_pad=0.6)
    save(fig, f"figCSV_{var}_world.png")
    # 17 地域
    for item in ["CRP"] + ITEMS5:
        fig, axs = plt.subplots(3, 6, figsize=(16 * CM, 15 * CM))
        for i, ax in enumerate(axs.flat):
            if i >= len(REG17):
                ax.axis("off"); continue
            r = REG17[i]
            panel(ax, res[(res.VAR == var) & (res.ITEM == item) & (res.Region == r)], r, small=True)
            ax.set_title(r + (" †" if r in DAGGER else ""), fontsize=6.5, pad=2)
            if i % 6 == 0:
                ax.set_ylabel(YLAB[var], fontsize=5.5)
        fig.text(0.5, 0.995, f"{TITLE[var]} of {NAME[item].lower() if item != 'CRP' else 'crops (CRP)'}: AgMIP 17 regions",
                 ha="center", va="top", fontsize=8)
        legend(fig, 0.975)
        fig.text(0.5, 0.94, EFF_LINE, ha="center", va="top", fontsize=6.5)
        fig.text(0.01, 0.005, wrap(notes, 185), ha="left", va="bottom", fontsize=4.6)
        fig.tight_layout(rect=(0, 0.12, 1, 0.925), h_pad=0.6, w_pad=0.3)
        save(fig, f"figCSV_{var}_{item}_region.png")
print("font:", FONT, "| dagger:", DAGGER)
print(miss[["share_pop2015", "named", "n_small"]].to_string())
