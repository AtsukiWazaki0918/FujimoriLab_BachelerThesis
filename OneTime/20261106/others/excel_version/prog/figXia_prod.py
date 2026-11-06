# -*- coding: utf-8 -*-
"""
figXia_prod.py : 2050 年の作物生産量の変化を、中間報告の4つの効果について、カロリーベース（PJ）で
  Xia et al. (2026) の6モデルと AIM-ALPHA で比べる。
  入力 : ../data/Xiadata.xlsx（シート Crop prod change in 2050, Variable = PROD [1000 t]）
         ../data/モデル間比較用model_output/GLOBIOM.csv（GLOBIOM の生重量の PROD）
         ../data/all_scenario_World.gdx（qs_load [1000 t]、cal_load [million kcal]、qdFood_load [1000 t]）
         ../define/xia_region_map.csv（Xia SI Table 4：国 → 地域）
  出力 : ../output/figXia_prod_<作物>.png（WHT, RIC, CGR, OSD, SGC）と figXia_prod_TOTAL.png（5作物の合計）
         ../data/xia_prod_compare.csv（図の数値）、../data/kcal_factor.csv（換算係数）
  効果 : common.py の EFF4（Xia の効果を組み合わせて中間報告の4つの効果を作る）
  カロリー換算 :
     E [PJ] = ΔPROD [1000 t] × 1000 [t / 1000 t] × f [kcal/t] × 4184 [J/kcal] × 1e-15 [PJ/J]
            = ΔPROD [1000 t] × f [kcal/t] × 4.184e-9
     f = Σ_国 cal_load ÷ Σ_国 qdFood_load（AIM-ALPHA、BaU_NoCC_woO3、2020 年、世界）× 1000
         （cal_load は million kcal、qdFood_load は 1000 t なので、比に 1000 を掛けると kcal/t）
     CGR は mze と crl をまとめて計算する。同じ f を全モデル・全地域に使う。
  GLOBIOM は Excel の PROD が乾物重量なので、CSV の生重量（1000 t）から同じ式で計算する（RTW = WLD − 5地域）。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from common import *

XIA_EFF = {"climate effect": "Climate", "mitigation effect": "Mitigation", "ozone reduction effect": "Ozone"}
XIA_REG = {"China": "CHN", "India": "IND", "South-East Asia": "SEA", "Other Asia": "OAS",
           "Sub-Saharan Africa": "SSA", "Rest of the world": "RTW"}
XIA_MODELS = ["AIM", "ENVISAGE", "GCAM", "GLOBIOM", "IMPACT", "MAGNET"]
LABEL = {"AIM": "AIM-Hub"}
J_PER_KCAL = 4184.0

# ---------------------------------------------------------------- カロリー換算係数（AIM-ALPHA から）
A = load_alpha(["qs_load", "cal_load", "qdFood_load"])
fb = A["cal_load"].merge(A["qdFood_load"], on=["scen", "c", "cty", "year"], suffixes=("_cal", "_q"))
fb = fb[(fb.scen == SCEN_ALPHA["BAU_NoCC"]) & (fb.year == "2020")]
KF = {}
for item, cs in CROP5.items():
    g = fb[fb.c.isin(cs)]
    KF[item] = g.v_cal.sum() / g.v_q.sum() * 1000          # kcal/t
pd.DataFrame({"item": list(KF), "alpha_items": ["+".join(CROP5[i]) for i in KF],
              "kcal_per_t": list(KF.values())}).to_csv(os.path.join(DDIR, "kcal_factor.csv"),
                                                       index=False, encoding="utf-8-sig")
to_pj = lambda d1000t, item: d1000t * KF[item] * 1000 * J_PER_KCAL * 1e-15

# ---------------------------------------------------------------- Xia（Excel）→ 4つの効果 [1000 t]
x = pd.read_excel(XLS, sheet_name="Crop prod change in 2050")
x = x[x.Variable == "PROD"].copy()
x["Region"] = x.Region.map(XIA_REG)
x["eff"] = list(zip(x.RCP, x.Effect.map(XIA_EFF)))
xv = x.set_index(["Model", "Region", "Item", "eff"]).Value

# GLOBIOM：CSV（生重量）から Xia の効果を計算する。乾物重量で Excel と一致することも確かめる
g = pd.read_csv(os.path.join(MDIR, "GLOBIOM.csv"), low_memory=False)
g = g[(g.Variable == "PROD") & (g.Year == 2050) & g.Item.isin(CROP5)]
def glob_region(unit):
    t = g[g.Unit == unit].pivot_table(index=["Scenario", "Item"], columns="Region", values="Value")
    out = t[REG6[:-1]].copy()
    out["RTW"] = t["WLD"] - t[REG6[:-1]].sum(axis=1)
    return out
chk = {"5regions": [], "RTW": []}
for unit in ["1000 t dm", "1000 t"]:
    gr = glob_region(unit)
    for reg in REG6:
        for item in CROP5:
            for eff in [k for k in EFFECT if k[0] in ("RCP2.6", "RCP7.0") and k[1] != "Combined"]:
                v = effect_value(lambda s: gr.loc[(csv_scen("GLOBIOM", s), item), reg], eff)
                if unit == "1000 t":
                    xv[("GLOBIOM", reg, item, eff)] = v          # 生重量で置き換える
                else:
                    chk["RTW" if reg == "RTW" else "5regions"].append(abs(v - xv[("GLOBIOM", reg, item, eff)]))
print(f"GLOBIOM（乾物重量）の CSV と Excel の差の最大 [1000 t]：5地域 {max(chk['5regions']):.3g}、RTW {max(chk['RTW']):.3g}")

rows = []
for (m, reg, item), _ in xv.groupby(level=[0, 1, 2]):
    for e in EFF4:
        v = sum(xv[(m, reg, item, pt)] for pt in EFF4_FROM_XIA[e])
        rows.append(dict(Model=m, Region=reg, item=item, effect=e, d_1000t=v))

# ---------------------------------------------------------------- AIM-ALPHA [1000 t]
qs = A["qs_load"]; qs = qs[qs.year == "2050"].copy()
rm = region_map(); qs["reg"] = qs.cty.map(rm)
assert qs.reg.notna().all()
alpha_interim = []
for item, cs in CROP5.items():
    agg = qs[qs.c.isin(cs)].groupby(["scen", "reg"]).v.sum()
    for reg in REG6:
        get = lambda sc: agg.get((sc, reg), 0.0)
        for e in EFF4:
            rows.append(dict(Model="AIM-ALPHA", Region=reg, item=item, effect=e,
                             d_1000t=effect_value(lambda s: get(SCEN_ALPHA[s]), e)))
            t, r = EFF4_INTERIM_ALPHA[e]
            alpha_interim.append(dict(Region=reg, item=item, effect=e, d_1000t_interim_def=get(t) - get(r)))
res = pd.DataFrame(rows)
res["PJ"] = [to_pj(v, i) for v, i in zip(res.d_1000t, res.item)]
tot = res.groupby(["Model", "Region", "effect"], as_index=False)[["PJ"]].sum(); tot["item"] = "TOTAL"
res = pd.concat([res, tot], ignore_index=True)
ai = pd.DataFrame(alpha_interim); ai["PJ_interim_def"] = [to_pj(v, i) for v, i in zip(ai.d_1000t_interim_def, ai.item)]
ai = pd.concat([ai, ai.groupby(["Region", "effect"], as_index=False)[["PJ_interim_def"]].sum().assign(item="TOTAL")])
res = res.merge(ai.assign(Model="AIM-ALPHA"), on=["Model", "Region", "item", "effect"], how="left")
res.to_csv(os.path.join(DDIR, "xia_prod_compare.csv"), index=False, encoding="utf-8-sig")
print("kcal/t:", {k: round(v) for k, v in KF.items()})

# ---------------------------------------------------------------- 欠損の注記
note_lines, *_ = missing_note(set(qs.cty), "production (qs_load)")

# ---------------------------------------------------------------- 図
fams = {f.name for f in font_manager.fontManager.ttflist}
FONT = next((f for f in ["Times New Roman", "TeX Gyre Termes", "Liberation Serif"] if f in fams), "serif")
plt.rcParams.update({"font.family": FONT, "font.size": 7, "axes.linewidth": 0.4,
                     "xtick.major.width": 0.4, "ytick.major.width": 0.4,
                     "axes.spines.top": False, "axes.spines.right": False})
CM = 1 / 2.54
MODELS = XIA_MODELS + ["AIM-ALPHA"]
MARK = {"AIM": "o", "ENVISAGE": "^", "GCAM": "s", "GLOBIOM": "P", "IMPACT": "X", "MAGNET": "v", "AIM-ALPHA": "D"}
COLR = {m: "0.35" for m in XIA_MODELS}; COLR["AIM-ALPHA"] = "#C0504D"
OFF = dict(zip(MODELS, np.linspace(-0.3, 0.3, len(MODELS))))
NAME = dict(CROP5_NAME, TOTAL="Total of 5 crops (WHT + RIC + CGR + OSD + SGC)")
fstr = ", ".join(f"{k} {KF[k]:,.0f}" for k in CROP5)

for item in list(CROP5) + ["TOTAL"]:
    fig, axs = plt.subplots(2, 3, figsize=(16 * CM, 13.5 * CM))
    for ax, reg in zip(axs.flat, REG6):
        d = res[(res.item == item) & (res.Region == reg)]
        xx = np.arange(len(EFF4))
        med = d[d.Model.isin(XIA_MODELS)].groupby("effect").PJ.median().reindex(EFF4)
        ax.bar(xx, med.values, width=0.75, color="0.88", zorder=1)
        for m in MODELS:
            s = d[d.Model == m].set_index("effect").PJ.reindex(EFF4)
            ax.scatter(xx + OFF[m], s.values, marker=MARK[m], s=10, color=COLR[m], linewidths=0, zorder=3)
        ax.axhline(0, color="black", lw=0.4, zorder=2)
        ax.set_xticks(xx); ax.set_xticklabels(EFF4, fontsize=6.5)
        ax.set_xlim(-0.6, len(xx) - 0.4)
        ax.tick_params(axis="y", labelsize=6)
        ax.set_title(REG6_NAME[reg], fontsize=7, pad=2)
    for ax in axs[:, 0]:
        ax.set_ylabel(f"PROD of {item}: change in 2050 (PJ)")
    h = [Line2D([], [], ls="", marker=MARK[m], color=COLR[m], ms=3.5, label=LABEL.get(m, m)) for m in MODELS]
    h.append(Patch(color="0.88", label="Median of Xia et al. models (excl. AIM-ALPHA)"))
    fig.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, 0.972), ncol=8, frameon=False,
               fontsize=6, handletextpad=0.2, columnspacing=0.6)
    fig.text(0.5, 0.995, f"{NAME[item]} production [PROD], calorie basis (PJ).  Region: 6 regions of Xia et al. (2026).  "
             "Value: change in 2050.", ha="center", va="top", fontsize=6.5)
    fig.text(0.5, 0.935, EFF4_LINE, ha="center", va="top", fontsize=6.5)
    notes = [
        EFF4_NOTE,
        "Calorie basis: E [PJ] = dPROD [1000 t] x f [kcal/t] x 1000 x 4184 [J/kcal] x 1e-15.  f = sum cal_load / sum qdFood_load of AIM-ALPHA "
        f"(BaU_NoCC_woO3, 2020, world) x 1000 [kcal/t]: {fstr}.  The same f is used for all models and regions"
        + ("; TOTAL = sum of the 5 crops in PJ." if item == "TOTAL" else "."),
        "Xia et al.: Xiadata.xlsx (sheet 'Crop prod change in 2050'); GLOBIOM from its model output in fresh weight (1000 t) because the Excel "
        "values are in dry matter (Rest of the world = WLD - 5 regions).  AIM-Hub = 'AIM' in Xia et al.  "
        "AIM-ALPHA: qs_load [1000 t] summed over countries by Xia et al. SI Table 4.",
        "Bars: median of the six Xia et al. models (AIM-Hub, ENVISAGE, GCAM, GLOBIOM, IMPACT, MAGNET), excluding AIM-ALPHA.",
    ] + note_lines
    fig.text(0.01, 0.005, wrap_notes(notes), ha="left", va="bottom", fontsize=4.8)
    fig.tight_layout(rect=(0, 0.21, 1, 0.915), h_pad=0.8, w_pad=0.6)
    save_fig(fig, f"figXia_prod_{item}.png")
print("font:", FONT)
