# -*- coding: utf-8 -*-
"""
common.py : Xia et al. (2026) と AIM-Alpha の比較で使う共通の定義と読み込み関数。
  figXia_prod.py と figXia_price.py から import する（単独では実行しない）。
  パスはすべてこのファイルの場所（prog/）からの相対パス。
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GDX  = os.path.join(ROOT, "data", "all_scenario_World.gdx")
XLS  = os.path.join(ROOT, "data", "Xiadata.xlsx")
MDIR = os.path.join(ROOT, "data", "モデル間比較用model_output")
RMAP = os.path.join(ROOT, "define", "xia_region_map.csv")   # Xia SI Table 4（国 → 地域）
DDIR = os.path.join(ROOT, "data")
FIGD = os.path.join(ROOT, "output")
os.makedirs(FIGD, exist_ok=True)

# ---------------------------------------------------------------- シナリオ
# Xia（各モデルの CSV）のシナリオ名 → AIM-Alpha のシナリオ名
SCEN_ALPHA = {
    "BAU_NoCC":         "SSP2_BaU_CS_NoCC_woO3",
    "BAU":              "SSP2_BaU_CS_RCP70_woO3",
    "OZBAU":            "SSP2_BaU_CS_RCP70_wO3",
    "BAU_MITI":         "SSP2_500C_CS_RCP70_woO3",
    "BAU_MITI_RCP26":   "SSP2_500C_CS_RCP26_woO3",
    "OZBAU_MITI_RCP26": "SSP2_500C_CS_RCP26_wO3",
}

# 効果の定義（Xia SI Table 1）。{シナリオ: 係数} の線形結合
EFFECT = {
    ("RCP7.0", "Climate"):    {"BAU": 1, "BAU_NoCC": -1},
    ("RCP7.0", "Ozone"):      {"OZBAU": 1, "BAU": -1},
    ("RCP7.0", "Combined"):   {"OZBAU": 1, "BAU_NoCC": -1},
    ("RCP2.6", "Climate"):    {"BAU_MITI_RCP26": 1, "BAU_MITI": -1, "BAU": 1, "BAU_NoCC": -1},
    ("RCP2.6", "Mitigation"): {"BAU_MITI": 1, "BAU": -1},
    ("RCP2.6", "Ozone"):      {"OZBAU_MITI_RCP26": 1, "BAU_MITI_RCP26": -1},
    ("RCP2.6", "Combined"):   {"OZBAU_MITI_RCP26": 1, "BAU_NoCC": -1},
}

# 中間報告の4つの効果（Interim/ClaudeCode/README.md）を、Xia の効果の組み合わせで表したもの。
#   中間報告ではオゾンの影響を気候の影響に含める。
#   (1) 気候変動影響 SSP2-2.6 = Xia の RCP2.6 Climate + RCP2.6 Ozone
#   (2) 緩和策影響   SSP2-2.6 = Xia の RCP2.6 Mitigation
#   (3) 総合影響     SSP2-2.6 = (1) + (2) = OZBAU_MITI_RCP26 − BAU_NoCC
#   (4) 気候変動影響 SSP2-7.0 = Xia の RCP7.0 Climate + RCP7.0 Ozone = OZBAU − BAU_NoCC
EFF4 = ["(1)", "(2)", "(3)", "(4)"]
EFF4_LABEL = {"(1)": "(1) Climate change\n(SSP2-2.6)", "(2)": "(2) Mitigation\n(SSP2-2.6)",
              "(3)": "(3) Combined effect\n(SSP2-2.6)", "(4)": "(4) Climate change\n(SSP2-7.0)"}
EFF4_LINE = ("(1) Climate change (SSP2-2.6)   (2) Mitigation (SSP2-2.6)   "
             "(3) Combined effect (SSP2-2.6)   (4) Climate change (SSP2-7.0)")
EFF4_FROM_XIA = {"(1)": [("RCP2.6", "Climate"), ("RCP2.6", "Ozone")],
                 "(2)": [("RCP2.6", "Mitigation")],
                 "(3)": [("RCP2.6", "Climate"), ("RCP2.6", "Mitigation"), ("RCP2.6", "Ozone")],
                 "(4)": [("RCP7.0", "Climate"), ("RCP7.0", "Ozone")]}
EFFECT.update({e: {} for e in EFF4})
for e, parts in EFF4_FROM_XIA.items():
    for pt in parts:
        for sc, k in EFFECT[pt].items():
            EFFECT[e][sc] = EFFECT[e].get(sc, 0) + k
    EFFECT[e] = {sc: k for sc, k in EFFECT[e].items() if k != 0}
# 参考：中間報告での AIM-Alpha の定義（シナリオの差）。図には使わず、表に残す
EFF4_INTERIM_ALPHA = {"(1)": ("SSP2_BaU_CS_RCP26_wO3", "SSP2_BaU_CS_NoCC_woO3"),
                      "(2)": ("SSP2_500C_CS_RCP26_wO3", "SSP2_BaU_CS_RCP26_wO3"),
                      "(3)": ("SSP2_500C_CS_RCP26_wO3", "SSP2_BaU_CS_NoCC_woO3"),
                      "(4)": ("SSP2_BaU_CS_RCP70_wO3", "SSP2_BaU_CS_NoCC_woO3")}
EFF4_NOTE = ("Effects (interim report): (1) = Xia RCP2.6 Climate + RCP2.6 Ozone; (2) = Xia RCP2.6 Mitigation (BAU_MITI - BAU); "
             "(3) = (1) + (2) = OZBAU_MITI_RCP26 - BAU_NoCC; (4) = Xia RCP7.0 Climate + RCP7.0 Ozone = OZBAU - BAU_NoCC.  "
             "Ozone effects are included in the climate effects.  AIM-Alpha uses the same combination of its matching scenarios.")

def csv_scen(model, s):
    """各モデルの CSV でのシナリオ名。Xia の主な結果のオゾンは CH4 濃度をシナリオごとに変えたもの
    （_W_CH4）。GLOBIOM には _W_CH4 が無く、ENVISAGE は小文字の _w_CH4（2026-11-04 の照合で確認）。"""
    if s.startswith("OZBAU") and model != "GLOBIOM":
        return s + ("_w_CH4" if model == "ENVISAGE" else "_W_CH4")
    return s

def effect_value(f, eff):
    """f(シナリオ名) → 値 を受け取り、効果の値を返す。"""
    return sum(k * f(s) for s, k in EFFECT[eff].items())

# ---------------------------------------------------------------- 地域・品目
REG6 = ["CHN", "IND", "SEA", "OAS", "SSA", "RTW"]
REG6_NAME = {"CHN": "China", "IND": "India", "SEA": "South-East Asia", "OAS": "Other Asia",
             "SSA": "Sub-Saharan Africa", "RTW": "Rest of the world"}

def region_map():
    """Xia SI Table 4 の国 → 6 地域。5 地域以外は RTW。"""
    m = pd.read_csv(RMAP)
    m["reg6"] = m.xia_reg.where(m.xia_reg.isin(REG6[:-1]), "RTW")
    return dict(zip(m.iso3, m.reg6))

# AIM-Alpha の品目 → AgMIP の5作物（define/AgMIP_c.map と同じ）
CROP5 = {"WHT": ["wht"], "RIC": ["rce"], "CGR": ["mze", "crl"], "OSD": ["ocr"], "SGC": ["sgr"]}
CROP5_NAME = {"WHT": "Wheat", "RIC": "Rice", "CGR": "Coarse grains", "OSD": "Oilseeds", "SGC": "Sugar crops"}
# AIM-Alpha の品目 → AGR（define/AgMIP_c.map の AGR。作物13品目＋畜産6品目）
AGR_ALPHA = ["rce", "wht", "mze", "crl", "ocr", "sgr", "str", "pls", "nut", "vgt", "frt", "stm", "spc",
             "cmt", "rmt", "omt", "pmt", "egg", "mlk"]

# ---------------------------------------------------------------- AIM-Alpha の読み込み
def load_alpha(symbols):
    import gamspy_base, gams.transfer as gt
    c = gt.Container(system_directory=gamspy_base.directory)
    c.read(GDX, symbols=list(symbols))
    out = {}
    for s in symbols:
        d = c[s].records.copy()
        d.columns = [col.split("_")[0] if col.startswith(("SCENARIO", "cty", "Y")) else col
                     for col in d.columns]
        d = d.rename(columns={"SCENARIO": "scen", "Y": "year", "value": "v"})
        for col in d.columns:
            if col != "v":
                d[col] = d[col].astype(str)
        out[s] = d
    return out

def alpha_cty_all():
    import gamspy_base, gams.transfer as gt
    c = gt.Container(system_directory=gamspy_base.directory)
    c.read(GDX, symbols=["cty"])
    return set(c["cty"].records.iloc[:, 0].astype(str))

# ---------------------------------------------------------------- 欠損の注記
def missing_note(cty_with_data, label, regions=None):
    """Xia の区分にあるが AIM-Alpha にデータが無い国（データ無し）と、
    AIM-Alpha にあるが Xia の区分に無い国（区分無し）を、地域ごとの文字列にする。"""
    rm = region_map()
    allc = alpha_cty_all()
    no_data = {}
    for iso, r in rm.items():
        if iso not in cty_with_data:
            no_data.setdefault(r, []).append(iso if iso in allc else iso + "*")
    regs = regions or REG6
    star = any(v.endswith("*") for vs in no_data.values() for v in vs)
    lines = [f"No data in AIM-Alpha for {label} (countries in Xia et al. SI Table 4 that are in the AIM-Alpha "
             "country list but have no records" + ("; * = code not in the AIM-Alpha country list" if star else "") + "):"]
    for r in regs:
        if r in no_data:
            lines.append(f"  {r}: " + ", ".join(sorted(no_data[r])))
    extra = sorted(allc - set(rm))
    extra_d = sorted(set(extra) & set(cty_with_data))
    lines.append("Not classified in Xia et al. (AIM-Alpha codes absent from SI Table 4): "
                 + ", ".join(extra) + ("; none of them have data." if not extra_d
                                        else "; with data: " + ", ".join(extra_d)))
    import textwrap
    out = []
    for ln in lines:
        ind = "      " if ln.startswith("  ") else "  "
        out += textwrap.wrap(ln, width=190, subsequent_indent=ind, break_on_hyphens=False) or [ln]
    return out, no_data, extra, extra_d


def wrap_notes(lines, width=190):
    """図の下の注記を、右端で切れないように折り返す。"""
    import textwrap
    out = []
    for ln in lines:
        ind = "      " if ln.startswith("  ") else "  "
        out += textwrap.wrap(ln, width=width, subsequent_indent=ind, break_on_hyphens=False) or [ln]
    return "\n".join(out)


def save_fig(fig, name, dpi=600):
    """メモリ上で PNG にしてから書き込む。接続先のフォルダでは、上書き時に "w+b" で開くと失敗することがあるため。"""
    import io, time
    import matplotlib.pyplot as plt
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=dpi); plt.close(fig)
    for k in range(10):
        try:
            with open(os.path.join(FIGD, name), "wb") as f:
                f.write(buf.getvalue())
            return
        except OSError:
            time.sleep(2)
    raise OSError("保存できませんでした: " + name)
