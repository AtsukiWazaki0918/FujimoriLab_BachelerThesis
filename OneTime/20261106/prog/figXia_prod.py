# -*- coding: utf-8 -*-
"""
figXia_prod.py : 2050 年の作物生産量の変化（効果別）を Xia et al. (2026) の6モデルと AIM-Alpha で比べる。
  入力 : ../data/Xiadata.xlsx（シート Crop prod change in 2050, Variable = PROD）
         ../data/all_scenario_World.gdx（qs_load：Domestic production [1000 t]、国別）
         ../define/xia_region_map.csv（Xia SI Table 4：国 → 地域）
  出力 : ../output/figXia_prod_<作物>.png（WHT, RIC, CGR, OSD, SGC の5枚）
         ../data/xia_prod_compare.csv（図の数値）
  値   : 2050 年の効果（シナリオの差、SI Table 1 の式）[1000 t]。図では百万 t で表示する。
  Xia の値は Excel の値をそのまま使う。AIM-Alpha は国の値を 6 地域に足してから効果を計算する。
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
from common import *

YEAR = "2050"
EFF_PROD = [("RCP7.0", "Climate"), ("RCP7.0", "Ozone"),
            ("RCP2.6", "Climate"), ("RCP2.6", "Mitigation"), ("RCP2.6", "Ozone")]
XIA_EFF = {"climate effect": "Climate", "mitigation effect": "Mitigation", "ozone reduction effect": "Ozone"}
XIA_REG = {"China": "CHN", "India": "IND", "South-East Asia": "SEA", "Other Asia": "OAS",
           "Sub-Saharan Africa": "SSA", "Rest of the world": "RTW"}
XIA_MODELS = ["AIM", "ENVISAGE", "GCAM", "GLOBIOM", "IMPACT", "MAGNET"]
LABEL = {"AIM": "AIM-Hub", "AIM-Alpha": "AIM-Alpha"}

# ---------------------------------------------------------------- Xia
x = pd.read_excel(XLS, sheet_name="Crop prod change in 2050")
x = x[x.Variable == "PROD"].copy()
x["Region"] = x.Region.map(XIA_REG)
x["eff"] = list(zip(x.RCP, x.Effect.map(XIA_EFF)))
x = x.rename(columns={"Item": "item", "Value": "value"})[["Model", "Region", "item", "eff", "value"]]

# ---------------------------------------------------------------- AIM-Alpha
qs = load_alpha(["qs_load"])["qs_load"]
qs = qs[qs.year == YEAR]
rm = region_map()
qs["reg"] = qs.cty.map(rm)
assert qs.reg.notna().all(), "Xia の区分に無い国にデータがある"
rows = []
for item, cs in CROP5.items():
    agg = qs[qs.c.isin(cs)].groupby(["scen", "reg"]).v.sum()
    for reg in REG6:
        for eff in EFF_PROD:
            f = lambda s: agg.get((SCEN_ALPHA[s], reg), 0.0)
            rows.append(dict(Model="AIM-Alpha", Region=reg, item=item, eff=eff, value=effect_value(f, eff)))
a = pd.DataFrame(rows)
res = pd.concat([x, a], ignore_index=True)
res["RCP"] = res.eff.str[0]; res["Effect"] = res.eff.str[1]
res.drop(columns="eff").to_csv(os.path.join(DDIR, "xia_prod_compare.csv"), index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------- 欠損の注記
cty_data = set(qs.cty)
note_lines, *_ = missing_note(cty_data, "production (qs_load)")

# ---------------------------------------------------------------- 図
fams = {f.name for f in font_manager.fontManager.ttflist}
FONT = next((f for f in ["Times New Roman", "TeX Gyre Termes", "Liberation Serif"] if f in fams), "serif")
plt.rcParams.update({"font.family": FONT, "font.size": 7, "axes.linewidth": 0.4,
                     "xtick.major.width": 0.4, "ytick.major.width": 0.4,
                     "axes.spines.top": False, "axes.spines.right": False})
CM = 1 / 2.54
MODELS = XIA_MODELS + ["AIM-Alpha"]
MARK = {"AIM": "o", "ENVISAGE": "^", "GCAM": "s", "GLOBIOM": "P", "IMPACT": "X", "MAGNET": "v", "AIM-Alpha": "D"}
COLR = {m: "0.35" for m in XIA_MODELS}; COLR["AIM-Alpha"] = "#C0504D"
OFF = dict(zip(MODELS, np.linspace(-0.3, 0.3, len(MODELS))))
TICK = [f"{r}\n{e}" for r, e in EFF_PROD]

def save(fig, name):
    fig.savefig(os.path.join(FIGD, name), dpi=600); plt.close(fig)

for item in CROP5:
    fig, axs = plt.subplots(2, 3, figsize=(16 * CM, 13.5 * CM))
    for ax, reg in zip(axs.flat, REG6):
        d = res[(res.item == item) & (res.Region == reg)]
        xx = np.arange(len(EFF_PROD))
        for m in MODELS:
            s = d[d.Model == m].set_index("eff").value.reindex(EFF_PROD) / 1000
            ax.scatter(xx + OFF[m], s.values, marker=MARK[m], s=10, color=COLR[m],
                       linewidths=0, zorder=3)
        ax.axhline(0, color="black", lw=0.4, zorder=2)
        for b in [1.5]:
            ax.axvline(b, color="0.7", lw=0.4, ls=":")
        ax.set_xticks(xx); ax.set_xticklabels(TICK, fontsize=5.5)
        ax.set_xlim(-0.6, len(xx) - 0.4)
        ax.tick_params(axis="y", labelsize=6)
        ax.set_title(REG6_NAME[reg], fontsize=7, pad=2)
    for ax in axs[:, 0]:
        ax.set_ylabel(f"PROD of {item}: change in 2050 (million t)")
    h = [Line2D([], [], ls="", marker=MARK[m], color=COLR[m], ms=3.5, label=LABEL.get(m, m)) for m in MODELS]
    fig.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, 0.965), ncol=7, frameon=False,
               fontsize=6.5, handletextpad=0.2, columnspacing=0.8)
    fig.text(0.5, 0.995,
             f"{CROP5_NAME[item]} ({item}) production [PROD].  Region: 6 regions of Xia et al. (2026).  "
             "Value: change from the reference scenario of each effect (SI Table 1) in 2050.",
             ha="center", va="top", fontsize=6.5)
    notes = [f"AIM-Alpha: qs_load [1000 t] of {' + '.join(CROP5[item])}, summed over countries by Xia et al. SI Table 4.  "
             "Xia et al.: values in Xiadata.xlsx (sheet 'Crop prod change in 2050').  AIM-Hub = 'AIM' in Xia et al.",
             "GLOBIOM PROD is in dry matter (1000 t dm); other models are in fresh weight (1000 t)."] + note_lines
    fig.text(0.01, 0.005, wrap_notes(notes), ha="left", va="bottom", fontsize=4.8)
    fig.tight_layout(rect=(0, 0.15, 1, 0.93), h_pad=0.8, w_pad=0.6)
    save(fig, f"figXia_prod_{item}.png")
print("font:", FONT)
print(res.pivot_table(index=["item", "Region"], columns="Model", values="value",
                      aggfunc=lambda s: s.notna().sum()).to_string())
