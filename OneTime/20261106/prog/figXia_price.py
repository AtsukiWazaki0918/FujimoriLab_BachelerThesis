# -*- coding: utf-8 -*-
"""
figXia_price.py : 2050 年の農産物（AGR）の世界の生産者価格の変化（効果別）を、
  重みを固定した方法（方法A）で Xia et al. (2026) の各モデルと AIM-Alpha について計算し、比べる。
  入力 : ../data/モデル間比較用model_output/{AIM,ENVISAGE,GCAM,GLOBIOM,IMPACT}.csv（XPRP, PROD）
         ../data/all_scenario_World.gdx（pp_load：Producer price [USD/t]、qs_load：Domestic production [1000 t]）
         ../data/Xiadata.xlsx（シート Price change in 2050。照合用）
  出力 : ../output/figXia_price_world.png
         ../data/xia_price_compare.csv（図の数値と照合用の値）
  方法A : P(s, t) = Σ_{地域 or 国, 品目} p(s, t) × Q0 ÷ Σ Q0
          Q0 = 基準シナリオ（BAU_NoCC）・基準年（2020 年。ENVISAGE は 2021 年）の生産量
          効果 = 中間報告の4つの効果（common.py の EFF4。Xia の効果の組み合わせ）の式で P(s, 2050) を組み合わせた値
                 ÷ P(BAU_NoCC, 基準年)
          重みを固定するので、生産の構成の変化は入らず、価格の変化だけを表す。
  方法B（照合用） : CSV の XPRP AGR WLD（その時の生産量で重み付けした値）から同じ式で計算する。
          Xia の Excel の値はこの方法で作られている（AIM, IMPACT は 2026-11-04 に一致を確認）。
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

EFFS = EFF4      # 中間報告の4つの効果（common.py）
REG13 = ["CAN", "USA", "BRA", "OSA", "FSU", "EUR", "MEN", "SSA", "CHN", "IND", "SEA", "OAS", "ANZ"]
ITEM10 = ["WHT", "RIC", "CGR", "OSD", "SGC", "VFN", "OCR", "RUM", "NRM", "DRY"]
# 各モデルで AGR を作る品目（AIM-Alpha の AGR = 作物13品目＋畜産6品目 に対応する AgMIP の品目）
ITEMS = {
    "AIM":      ["WHT", "RIC", "CGR", "OSD", "SGC", "OCR", "RUM", "NRM", "DRY"],   # VFN は OCR に含まれる
    "ENVISAGE": ITEM10,
    "GCAM":     ["WHT", "RIC", "CGR", "OSD", "SGC", "OCR", "VFN|FRU", "VFN|LEG", "VFN|NUT", "VFN|RTB", "VFN|VEG",
                 "RUM", "NRM", "DRY"],                                             # VFN は内訳しか無い
    "GLOBIOM":  ITEM10,
    "IMPACT":   ITEM10,
}
BASEY = {"AIM": 2020, "ENVISAGE": 2021, "GCAM": 2020, "GLOBIOM": 2020, "IMPACT": 2020}
XIA_EFF = {"Climate change effect": "Climate", "Mitigation effect": "Mitigation",
           "Ozone change effect": "Ozone", "Combined effect": "Combined"}
SCENS = list(SCEN_ALPHA)

rows, info = [], []
# ---------------------------------------------------------------- Xia の各モデル（CSV）
for m in ITEMS:
    d = pd.read_csv(os.path.join(MDIR, m + ".csv"), low_memory=False)
    d = d[d.Variable.isin(["XPRP", "PROD"]) & d.Year.isin([BASEY[m], 2050])]
    d = d[~((d.Variable == "PROD") & d.Unit.str.contains("dm", case=False))]   # GLOBIOM は生重量を使う
    cs = {s: csv_scen(m, s) for s in SCENS}
    d = d[d.Scenario.isin(cs.values())]
    inv = {v: k for k, v in cs.items()}
    d["scen"] = d.Scenario.map(inv)
    # 方法A
    g = d[d.Region.isin(REG13) & d.Item.isin(ITEMS[m])]
    q0 = g[(g.Variable == "PROD") & (g.scen == "BAU_NoCC") & (g.Year == BASEY[m])].set_index(["Region", "Item"]).Value
    q0 = q0[q0 > 0]
    p = g[g.Variable == "XPRP"].set_index(["scen", "Year", "Region", "Item"]).Value
    need = [(s, y) for s in SCENS for y in [2050]] + [("BAU_NoCC", BASEY[m])]
    keep = [k for k in q0.index if all((s, y) + k in p.index for s, y in need)]
    drop = sorted(set(q0.index) - set(keep))
    q0 = q0.loc[keep]
    def P(s, y):
        return float((p.loc[[(s, y) + k for k in q0.index]].values * q0.values).sum() / q0.sum())
    base = P("BAU_NoCC", BASEY[m])
    # 照合：13 地域の PROD の合計と WLD の PROD
    w = d[(d.Region == "WLD") & (d.Variable == "PROD") & (d.scen == "BAU_NoCC") & (d.Year == BASEY[m])
          & d.Item.isin(ITEMS[m])].Value.sum()
    # 方法B（CSV の XPRP AGR WLD）
    b = d[(d.Region == "WLD") & (d.Item == "AGR") & (d.Variable == "XPRP")].set_index(["scen", "Year"]).Value
    for e in EFFS:
        a_val = effect_value(lambda s: P(s, 2050), e) / base
        b_val = (effect_value(lambda s: b[(s, 2050)], e) / b[("BAU_NoCC", BASEY[m])]) if len(b) else np.nan
        rows.append(dict(Model=m, effect=e, method_A=a_val, method_B_csv=b_val))
    info.append(dict(Model=m, base_year=BASEY[m], items="+".join(ITEMS[m]), n_pairs=len(q0),
                     dropped_pairs=";".join("/".join(k) for k in drop),
                     share_of_WLD_PROD=q0.sum() / w if w else np.nan))

# ---------------------------------------------------------------- AIM-Alpha（国 × 品目）
A = load_alpha(["pp_load", "qs_load"])
pp, qs = A["pp_load"], A["qs_load"]
inv = {v: k for k, v in SCEN_ALPHA.items()}
pp = pp[pp.c.isin(AGR_ALPHA) & pp.scen.isin(inv)].copy(); pp["scen"] = pp.scen.map(inv)
qs = qs[qs.c.isin(AGR_ALPHA) & qs.scen.isin(inv)].copy(); qs["scen"] = qs.scen.map(inv)
q0 = qs[(qs.scen == "BAU_NoCC") & (qs.year == "2020")].set_index(["cty", "c"]).v
q0 = q0[q0 > 0]
p = pp.set_index(["scen", "year", "cty", "c"]).v
need = [(s, "2050") for s in SCENS] + [("BAU_NoCC", "2020")]
keep = [k for k in q0.index if all((s, y) + k in p.index for s, y in need)]
drop = sorted(set(q0.index) - set(keep))
q0a = q0.loc[keep]
def PA(s, y):
    return float((p.loc[[(s, y) + k for k in q0a.index]].values * q0a.values).sum() / q0a.sum())
basea = PA("BAU_NoCC", "2020")
pp_raw = A["pp_load"][A["pp_load"].c.isin(AGR_ALPHA)].set_index(["scen", "year", "cty", "c"]).v
def PA2(scen_raw, y):
    """AIM-Alpha のシナリオ名で直接計算する（中間報告の定義の参考値用）。"""
    return float((pp_raw.loc[[(scen_raw, y) + k for k in q0a.index]].values * q0a.values).sum() / q0a.sum())
# 方法B（AIM-Alpha でも参考に計算）
qq = qs.set_index(["scen", "year", "cty", "c"]).v
def PB(s, y):
    pv = p.xs((s, y), level=[0, 1]); qv = qq.xs((s, y), level=[0, 1])
    j = pd.concat([pv, qv], axis=1, keys=["p", "q"]).dropna()
    return float((j.p * j.q).sum() / j.q.sum())
for e in EFFS:
    t, r = EFF4_INTERIM_ALPHA[e]
    rows.append(dict(Model="AIM-Alpha", effect=e,
                     method_A=effect_value(lambda s: PA(s, "2050"), e) / basea,
                     method_B_csv=effect_value(lambda s: PB(s, "2050"), e) / PB("BAU_NoCC", "2020"),
                     method_A_interim_def=(PA2(t, "2050") - PA2(r, "2050")) / basea))
info.append(dict(Model="AIM-Alpha", base_year=2020, items="+".join(AGR_ALPHA), n_pairs=len(q0a),
                 dropped_pairs=";".join("/".join(k) for k in drop), share_of_WLD_PROD=np.nan))

res = pd.DataFrame(rows)
# Excel（Xia）の値を同じ組み合わせで4つの効果にする
x = pd.read_excel(XLS, sheet_name="Price change in 2050")
x["RCP"] = x.RCP.str.replace("SSP2-2.6", "RCP2.6").str.replace("SSP2-7.0", "RCP7.0")
x["Effect"] = x.Effect.map(XIA_EFF)
xv = x.set_index(["Model", "RCP", "Effect"]).Value
xe = pd.DataFrame([dict(Model=m, effect=e, xia_excel=sum(xv[(m,) + pt] for pt in EFF4_FROM_XIA[e]))
                   for m in xv.index.get_level_values(0).unique() for e in EFF4])
res = res.merge(xe, on=["Model", "effect"], how="outer")
res["B_minus_excel"] = res.method_B_csv - res.xia_excel
res.to_csv(os.path.join(DDIR, "xia_price_compare.csv"), index=False, encoding="utf-8-sig")
pd.DataFrame(info).to_csv(os.path.join(DDIR, "xia_price_weights_info.csv"), index=False, encoding="utf-8-sig")
pd.set_option("display.width", 220)
print(pd.DataFrame(info).drop(columns="dropped_pairs").to_string())
print("dropped:", {r["Model"]: r["dropped_pairs"][:200] for r in info if r["dropped_pairs"]})
print(res.round(4).to_string())

# ---------------------------------------------------------------- 欠損の注記
note_lines, *_ = missing_note(set(A["pp_load"].cty) & set(A["qs_load"].cty),
                              "price (pp_load) and production (qs_load)", regions=REG6)

# ---------------------------------------------------------------- 図
fams = {f.name for f in font_manager.fontManager.ttflist}
FONT = next((f for f in ["Times New Roman", "TeX Gyre Termes", "Liberation Serif"] if f in fams), "serif")
plt.rcParams.update({"font.family": FONT, "font.size": 7, "axes.linewidth": 0.4,
                     "xtick.major.width": 0.4, "ytick.major.width": 0.4,
                     "axes.spines.top": False, "axes.spines.right": False})
CM = 1 / 2.54
MODELS = list(ITEMS) + ["AIM-Alpha"]
LABEL = {"AIM": "AIM-Hub"}
MARK = {"AIM": "o", "ENVISAGE": "^", "GCAM": "s", "GLOBIOM": "P", "IMPACT": "X", "AIM-Alpha": "D"}
COLR = {m: "0.35" for m in ITEMS}; COLR["AIM-Alpha"] = "#C0504D"
OFF = dict(zip(MODELS, np.linspace(-0.27, 0.27, len(MODELS))))
fig, ax = plt.subplots(figsize=(16 * CM, 11.5 * CM))
xx = np.arange(len(EFFS))
med = res[res.Model.isin(ITEMS)].groupby("effect").method_A.median().reindex(EFFS) * 100
ax.bar(xx, med.values, width=0.7, color="0.88", zorder=1)
for m in MODELS:
    s = res[res.Model == m].set_index("effect").method_A.reindex(EFFS) * 100
    ax.scatter(xx + OFF[m], s.values, marker=MARK[m], s=14, color=COLR[m], linewidths=0, zorder=3)
ax.axhline(0, color="black", lw=0.4, zorder=2)
ax.set_xticks(xx); ax.set_xticklabels([EFF4_LABEL[e] for e in EFFS])
ax.set_xlim(-0.6, len(xx) - 0.4)
ax.set_ylabel("Producer price of AGR (World): change in 2050\n(% of the baseline price in the base year)")
from matplotlib.patches import Patch
h = [Line2D([], [], ls="", marker=MARK[m], color=COLR[m], ms=4, label=LABEL.get(m, m)) for m in MODELS]
h.append(Patch(color="0.88", label="Median of Xia et al. models (excl. AIM-Alpha)"))
fig.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, 0.96), ncol=4, frameon=False, fontsize=7,
           handletextpad=0.2, columnspacing=1.0)
fig.text(0.5, 0.995, "Producer price of all agricultural products (AGR, crops + livestock) [XPRP / pp_load].  "
         "Region: World.  Fixed-weight (base-year production) aggregation for all models.",
         ha="center", va="top", fontsize=6.5)
notes = [
    EFF4_NOTE,
    "Bars: median of the five Xia et al. models shown (AIM-Hub, ENVISAGE, GCAM, GLOBIOM, IMPACT), excluding AIM-Alpha.",
    "Method: P(s,t) = sum p(s,t) x Q0 / sum Q0 over regions (AgMIP 13 regions; AIM-Alpha: countries) and items; "
    "Q0 = production in BAU_NoCC in the base year (2020; ENVISAGE: 2021, the first year after 2018 in its output).",
    "Value = effect of P in 2050 / P(BAU_NoCC, base year) x 100.  Production-mix changes are excluded, "
    "so the values differ from Xiadata.xlsx (current-production weights).",
    "Items: AIM-Hub WHT+RIC+CGR+OSD+SGC+OCR+RUM+NRM+DRY (VFN is in OCR); ENVISAGE, GLOBIOM, IMPACT add VFN; "
    "GCAM uses the VFN sub-items (FRU, LEG, NUT, RTB, VEG); AIM-Alpha: 13 crops + 6 livestock products (define/AgMIP_c.map).",
    "ENVISAGE prices are indices (2014 = 1) for each item, so its aggregate is a production-weighted mean of indices, "
    "not of USD/t.  GLOBIOM weights use fresh weight (1000 t).  MAGNET is not shown (no model output file).",
    "Source: Xia et al. models = data/モデル間比較用model_output/*.csv; AIM-Alpha = pp_load [USD/t], qs_load [1000 t] "
    "in all_scenario_World.gdx.  AIM-Hub = 'AIM' in Xia et al.",
] + note_lines
fig.text(0.01, 0.005, wrap_notes(notes).replace("モデル間比較用model_output", "model_output"),
         ha="left", va="bottom", fontsize=4.8)
fig.tight_layout(rect=(0, 0.30, 1, 0.89))
save_fig(fig, "figXia_price_world.png")
print("font:", FONT)
