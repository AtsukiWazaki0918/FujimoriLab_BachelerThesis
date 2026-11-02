# -*- coding: utf-8 -*-
"""
model_compare_crp.py : 作物合計 (CRP) の生産量・消費量・価格のモデル間比較
  入力 : ../AGMIP_all_scenario.gdx (AIM-Alpha, 変数 AGMIP_agg)
         ../モデル間比較用model_output/{AIM,ENVISAGE,GCAM,GLOBIOM,IMPACT}.csv
  出力 : csv/model_compare_crp.csv
         fig/model_compare/figMC_world.png      World（3 指標 × 4 効果）
         fig/model_compare/figMC_<VAR>_region.png  AgMIP 17 地域（指標ごとに 1 枚）
  値は 2050 年の % 変化 = (対象シナリオ / 参照シナリオ − 1) × 100。
  % で比べるので、モデル間の単位の違い（USD/t と指数など）は影響しない。
  ALPHA.csv は使わず、最新の GDX から AIM-Alpha の値を取る。
  元は アウトプット/ch4/model_compare_crp.py（2026-10-28）。パスだけを書き換えた。
  figMC_world.py / figMC_PROD_region.py / figMC_CONS_region.py / figMC_XPRP_region.py は中身が同じ。
  どれを実行しても ../output に図4枚、../data に表が出る。
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GDX  = os.path.join(ROOT, "data", "AGMIP_all_scenario.gdx")
MDIR = os.path.join(ROOT, "data", "モデル間比較用model_output")
OUTC = os.path.join(ROOT, "data", "model_compare_crp.csv")
FIGD = os.path.join(ROOT, "output")
os.makedirs(FIGD, exist_ok=True)
YEAR = 2050

# ---------------------------------------------------------------- 定義
VARS = {"PROD": "Production", "CONS": "Consumption", "XPRP": "Producer price"}
REG17 = ["AME","ANZ","BRA","CAN","CHN","EUR","FSU","IND","MEN","NAM",
         "OAM","OAS","OSA","SAS","SEA","SSA","USA"]
MODELS = ["AIM","ENVISAGE","GCAM","GLOBIOM","IMPACT","AIM-Alpha"]
OTHERS = MODELS[:-1]

# 効果 : (ラベル, 対象シナリオ, 参照シナリオ)  他モデル名 / AIM-Alpha 名
EFF = [
 ("(1) Climate Effect",    "OZBAU",            "BAU_NoCC",
                           "SSP2_BaU_CS_RCP70_wO3",  "SSP2_BaU_CS_NoCC_woO3"),
 ("(2) Net Climate Effect under Mitigation", "OZBAU_MITI_RCP26", "BAU_MITI",
                           "SSP2_500C_CS_RCP26_wO3", "SSP2_500C_CS_NoCC_woO3"),
 ("(3) Net Mitigation Effect without Climate Effect", "BAU_MITI",         "BAU_NoCC",
                           "SSP2_500C_CS_NoCC_woO3", "SSP2_BaU_CS_NoCC_woO3"),
 ("(4) Total Mitigation Effect",  "OZBAU_MITI_RCP26", "BAU_NoCC",
                           "SSP2_500C_CS_RCP26_wO3", "SSP2_BaU_CS_NoCC_woO3"),
]
EFF_LAB = [e[0] for e in EFF]
EFF_TICK = ["(1)","(2)","(3)","(4)"]
EFF_NOTE = "   ".join(EFF_LAB[:2]) + "\n" + "   ".join(EFF_LAB[2:])

# ---------------------------------------------------------------- 読み込み
def load_alpha():
    import gamspy_base, gams.transfer as gt
    m = gt.Container(system_directory=os.path.dirname(gamspy_base.__file__))
    m.read(GDX, symbols=["AGMIP_agg"])
    a = m["AGMIP_agg"].records
    a.columns = ["Scenario","Region","Variable","Item","Unit","Year","Value"]
    for c in a.columns[:-1]:
        a[c] = a[c].astype(str)
    a = a[(a.Item == "CRP") & a.Variable.isin(VARS) & (a.Year == str(YEAR))]
    # 単位 : 数量は 1000 t、価格は USD/t（% 変化なので単位は結果に影響しない）
    a = a[((a.Variable != "XPRP") & (a.Unit == "1000 t")) |
          ((a.Variable == "XPRP") & (a.Unit == "USD/t"))]
    a["Region"] = a.Region.replace({"World": "WLD"})
    a["Model"] = "AIM-Alpha"
    a["Year"] = a.Year.astype(int)
    return a

def load_other(m):
    d = pd.read_csv(os.path.join(MDIR, m + ".csv"), low_memory=False)
    d = d[(d.Item == "CRP") & d.Variable.isin(VARS) & (d.Year == YEAR)]
    # GLOBIOM は 1000 t と 1000 t dm の両方があるので生重量 (1000 t) を使う
    d = d[~d.Unit.str.contains("dm", case=False)]
    return d

raw = pd.concat([load_other(m) for m in OTHERS] + [load_alpha()], ignore_index=True)
assert not raw.duplicated(["Model","Scenario","Region","Variable"]).any(), "重複あり"
val = raw.set_index(["Model","Scenario","Region","Variable"]).Value

# ---------------------------------------------------------------- % 変化
rows = []
for model in MODELS:
    for lab, t_o, r_o, t_a, r_a in EFF:
        tgt, ref = (t_a, r_a) if model == "AIM-Alpha" else (t_o, r_o)
        for reg in REG17 + ["WLD"]:
            for v in VARS:
                try:
                    vt, vr = val[(model, tgt, reg, v)], val[(model, ref, reg, v)]
                except KeyError:
                    continue
                rows.append(dict(Model=model, Region=reg, Variable=v, Effect=lab,
                                 scenario_target=tgt, scenario_ref=ref,
                                 value_target=vt, value_ref=vr, diff=vt - vr,
                                 pct=(vt / vr - 1) * 100 if vr else np.nan))
res = pd.DataFrame(rows)
res.to_csv(OUTC, index=False, encoding="utf-8-sig")
print("rows:", len(res))
print(res.groupby(["Model","Variable"]).Region.nunique().unstack())

# ---------------------------------------------------------------- 図の共通設定
fams = {f.name for f in font_manager.fontManager.ttflist}
FONT = next((f for f in ["Times New Roman","TeX Gyre Termes","Liberation Serif"] if f in fams), "serif")
plt.rcParams.update({"font.family": FONT, "font.size": 7, "axes.linewidth": 0.4,
                     "xtick.major.width": 0.4, "ytick.major.width": 0.4,
                     "axes.spines.top": False, "axes.spines.right": False})
CM = 1 / 2.54
MARK = {"AIM":"o","ENVISAGE":"^","GCAM":"s","GLOBIOM":"P","IMPACT":"X","AIM-Alpha":"D"}
COLR = {m: "0.35" for m in OTHERS}; COLR["AIM-Alpha"] = "#C0504D"
OFF = dict(zip(MODELS, np.linspace(-0.27, 0.27, len(MODELS))))

# 図に書く指標の説明（指標名・変数名・品目・元データの単位）
NAME = {"PROD": "Crop production",
        "CONS": "Crop consumption (total domestic use)",
        "XPRP": "Crop producer price"}
SRC_UNIT = {"PROD": "1000 t",
            "CONS": "1000 t",
            "XPRP": "USD/t (ENVISAGE: index, 2014 = 1; GCAM: no data)"}
YLAB = {v: f"{v} of CRP: change in 2050 (%)" for v in VARS}
COMMON = ("Item: CRP (all crops).  Value: % change in 2050 from the reference scenario "
          "of each effect, computed for each model.")

def panel(ax, d):
    """横軸 = 4 効果。灰色の棒 = AIM-Alpha 以外のモデルの中央値、記号 = 各モデル。"""
    x = np.arange(len(EFF_LAB))
    med = d[d.Model.isin(OTHERS)].groupby("Effect").pct.median().reindex(EFF_LAB)
    ax.bar(x, med.values, width=0.7, color="0.88", zorder=1)
    for m in MODELS:
        s = d[d.Model == m].set_index("Effect").pct.reindex(EFF_LAB)
        ax.scatter(x + OFF[m], s.values, marker=MARK[m], s=10, color=COLR[m],
                   linewidths=0, zorder=3)
    ax.axhline(0, color="black", lw=0.4, zorder=2)
    ax.set_xticks(x)
    ax.set_xticklabels(EFF_TICK, fontsize=7)
    ax.set_xlim(-0.6, len(x) - 0.4)

def legend(fig):
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    h = [Line2D([], [], ls="", marker=MARK[m], color=COLR[m], ms=3.5, label=m) for m in MODELS]
    h.append(Patch(color="0.88", label="Median of other models (excl. AIM-Alpha)"))
    fig.legend(handles=h, loc="lower center", ncol=7, frameon=False,
               fontsize=6.5, handletextpad=0.2, columnspacing=0.7)

def save(fig, name):
    """OneDrive の同期中に書き込みが一時的に失敗することがあるので再試行する。"""
    import io, time
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=600); plt.close(fig)
    for k in range(10):
        try:
            with open(os.path.join(FIGD, name), "wb") as f:
                f.write(buf.getvalue())
            return
        except OSError:
            time.sleep(2)
    raise OSError("保存できませんでした: " + name)

# ---------------------------------------------------------------- World
fig, axs = plt.subplots(1, 3, figsize=(16 * CM, 8.5 * CM))
for ax, v in zip(axs, VARS):
    panel(ax, res[(res.Region == "WLD") & (res.Variable == v)])
    ax.set_title(f"{NAME[v]}\n[{v}, source unit: {SRC_UNIT[v]}]".replace(" (ENVISAGE", "\n(ENVISAGE").replace("; GCAM", ";\nGCAM"),
                 fontsize=7, pad=3)
    ax.set_ylabel(YLAB[v])
fig.text(0.5, 0.995, "Region: World.  " + COMMON, ha="center", va="top", fontsize=7)
fig.text(0.5, 0.955, EFF_NOTE, ha="center", va="top", fontsize=7)
legend(fig)
fig.tight_layout(rect=(0, 0.06, 1, 0.88))
save(fig, "figMC_world.png")

# ---------------------------------------------------------------- 17 地域
for v in VARS:
    fig, axs = plt.subplots(3, 6, figsize=(16 * CM, 14 * CM))
    for i, ax in enumerate(axs.flat):
        if i >= len(REG17):
            ax.axis("off"); continue
        reg = REG17[i]
        panel(ax, res[(res.Region == reg) & (res.Variable == v)])
        ax.set_title(reg, fontsize=7, pad=2)
        ax.tick_params(axis="x", labelsize=6)
        ax.tick_params(axis="y", labelsize=6)
        if i % 6 == 0:
            ax.set_ylabel(YLAB[v])
    # 右下の空き枠に効果の一覧を置く
    axs.flat[-1].text(-0.1, 0.5, "\n".join(EFF_LAB).replace(" without", "\n     without")
                      .replace(" under", "\n     under"), fontsize=6, va="center",
                      transform=axs.flat[-1].transAxes)
    fig.text(0.5, 0.995, f"{NAME[v]} [{v}, source unit: {SRC_UNIT[v]}].  Region: AgMIP 17 regions.",
             ha="center", va="top", fontsize=7)
    fig.text(0.5, 0.968, COMMON, ha="center", va="top", fontsize=7)
    legend(fig)
    fig.tight_layout(rect=(0, 0.04, 1, 0.95), h_pad=0.6, w_pad=0.3)
    save(fig, f"figMC_{v}_region.png")
print("font:", FONT, "-> figures in", FIGD)
