# -*- coding: utf-8 -*-
"""
Xiadata.xlsx（Xia et al. 2026 の公開データ）の数値が、各モデルの AgMIP 形式の出力 CSV と一致するかを確かめる。
  入力 : ../data/Xiadata.xlsx
         ../data/モデル間比較用model_output/{AIM,ENVISAGE,GCAM,GLOBIOM,IMPACT}.csv
  出力 : ../data/xia_check_detail.csv   Excel の1行（モデル別の照合は1行×モデル）ごとの照合結果
         ../data/xia_check_summary.csv  シート × モデル × 効果 ごとの一致数
照合は Excel の行を軸にし、対応する CSV の値を探して比べる。
  一致 : |差| <= 1e-6 × max(1, |Excel の値|)
  効果とシナリオの対応（Crop prod change の PROD で全件一致を確かめたもの）
    RCP7.0 climate    = BAU − BAU_NoCC
    RCP7.0 ozone      = OZBAU_W_CH4 − BAU          （GLOBIOM は OZBAU − BAU）
    RCP2.6 mitigation = BAU_MITI − BAU
    RCP2.6 ozone      = OZBAU_MITI_RCP26_W_CH4 − BAU_MITI_RCP26（GLOBIOM は OZBAU_MITI_RCP26 − BAU_MITI_RCP26）
    RCP2.6 climate    = (BAU_MITI_RCP26 − BAU_MITI) + (BAU − BAU_NoCC)
                        （Crop prod change の PROD に最小二乗で当てはめて求めた。4モデルで全件一致）
    Combined          = その RCP の効果の和
  PROD の単位は 1000 t（GLOBIOM だけ 1000 t dm）。ENVISAGE は 2020 年の代わりに 2021 年の値を使う。
使い方 : python check_xia_vs_csv.py（引数なし。どこから実行してもよい）
"""
import os, numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data'); MDIR = os.path.join(DATA, 'モデル間比較用model_output')
MODELS = ['AIM', 'ENVISAGE', 'GCAM', 'GLOBIOM', 'IMPACT']
TOL = 1e-6
X = pd.read_excel(os.path.join(DATA, 'Xiadata.xlsx'), sheet_name=None)
D = {}
for m in MODELS:
    d = pd.read_csv(os.path.join(MDIR, m + '.csv'), low_memory=False)
    d['Region'] = d.Region.astype(str)
    D[m] = d.groupby(['Variable', 'Item', 'Unit', 'Region', 'Scenario', 'Year']).Value.first()

def unit(m, var):
    u = {'PROD': '1000 t dm' if m == 'GLOBIOM' else '1000 t', 'CALO': 'kcal/cap/d', 'POPT': None, 'XPRP': None}[var]
    return u
def get(m, var, item, reg, scen, year):
    if m == 'ENVISAGE' and year == 2020:
        year = 2021        # ENVISAGE の CSV には 2020 年が無い。2021 年を 2020 年として扱うと Baseline food price が一致する
    s = D[m]
    try:
        x = s.loc[(var, item)]
    except KeyError:
        return np.nan
    u = unit(m, var)
    if u is None:
        us = x.index.get_level_values(0).unique()
        if len(us) != 1: return np.nan
        u = us[0]
    try:
        return float(x.loc[(u, reg, scen, year)])
    except KeyError:
        return np.nan

def nrcp(s): return '26' if '2.6' in s else '70'
def neff(s):
    s = s.lower()
    return 'climate' if 'climate' in s else 'mitigation' if 'mitigation' in s else 'ozone' if 'ozone' in s else 'combined'
def pairs(m, rcp, eff):
    W = '' if m == 'GLOBIOM' else ('_w_CH4' if m == 'ENVISAGE' else '_W_CH4')
    P = {('70', 'climate'): [('BAU', 'BAU_NoCC')], ('70', 'ozone'): [('OZBAU' + W, 'BAU')],
         ('26', 'mitigation'): [('BAU_MITI', 'BAU')],
         ('26', 'ozone'): [('OZBAU_MITI_RCP26' + W, 'BAU_MITI_RCP26')],
         ('26', 'climate'): [('BAU_MITI_RCP26', 'BAU_MITI'), ('BAU', 'BAU_NoCC')]}
    if eff == 'combined':
        return sum((P[k] for k in P if k[0] == rcp), [])
    return P[(rcp, eff)]
def effect(m, rcp, eff, f):
    """f(scenario) -> 値。効果 = Σ (f(A) − f(B))"""
    return sum(f(a) - f(b) for a, b in pairs(m, rcp, eff))

R5 = ['CHN', 'IND', 'OAS', 'SEA', 'SSA']
R17 = ['AME', 'ANZ', 'BRA', 'CAN', 'CHN', 'EUR', 'FSU', 'IND', 'MEN', 'NAM', 'OAM', 'OAS', 'OSA', 'SAS', 'SEA', 'SSA', 'USA']
NAME = {'China': 'CHN', 'India': 'IND', 'Other Asia': 'OAS', 'South-East Asia': 'SEA',
        'Sub-Saharan Africa': 'SSA', 'Rest of the world': 'RTW'}
def reg_val(m, var, item, reg, scen, year):
    """RTW（Rest of the world）は WLD から5地域を引く。CALO は POPT で人口加重する。"""
    if reg != 'RTW':
        return get(m, var, item, reg, scen, year)
    if var == 'CALO':
        pw = get(m, 'POPT', 'TOT', 'WLD', scen, year)
        num = get(m, 'CALO', item, 'WLD', scen, year) * pw
        den = pw
        for r in R5:
            p = get(m, 'POPT', 'TOT', r, scen, year)
            num -= get(m, 'CALO', item, r, scen, year) * p; den -= p
        return num / den
    return get(m, var, item, 'WLD', scen, year) - sum(get(m, var, item, r, scen, year) for r in R5)

rows = []
def rec(sheet, m, key, xia, csv, method, note=''):
    if np.isnan(csv):
        st = '照合不可'
    else:
        st = '一致' if abs(csv - xia) <= TOL * max(1, abs(xia)) else '不一致'
    rows.append(dict(sheet=sheet, Model=m, key=key, xia=xia, csv=csv, diff=csv - xia if not np.isnan(csv) else np.nan,
                     status=st, method=method, note=note))

# ---------------- 1. Population（モデル列なし。各モデルの POPT と比べる）
for _, r in X['Population'].iterrows():
    for m in MODELS:
        rec('Population', m, f'{r.Region} {r.Year}', r.POP, get(m, 'POPT', 'TOT', r.Region, 'BAU_NoCC', int(r.Year)),
            'POPT TOT, BAU_NoCC')

# ---------------- 2. Baseline calorie intake（2020 年の値は FAO の値で、全モデル共通。2020 年比で比べる）
cb = X['Baseline calorie intake']
base = cb[cb.Year == 2020].set_index(['Model', 'Region']).CALO_fao
for _, r in cb.iterrows():
    m = r.Model
    if m not in D: rec('Baseline calorie intake', m, f'{r.Region} {r.Year}', r.CALO_fao, np.nan, '', 'CSV なし'); continue
    if r.Year == 2020:
        rec('Baseline calorie intake', m, f'{r.Region} {r.Year}', r.CALO_fao, np.nan, '', '2020 年は FAO の値（CSV に無い）'); continue
    c = get(m, 'CALO', 'AGR', r.Region, 'BAU_NoCC', int(r.Year)); c0 = get(m, 'CALO', 'AGR', r.Region, 'BAU_NoCC', 2020)
    rec('Baseline calorie intake', m, f'{r.Region} {r.Year}', r.CALO_fao, base[(m, r.Region)] * c / c0,
        'CALO_fao(2020) × CALO AGR(t) / CALO AGR(2020), BAU_NoCC')

# ---------------- 3. Baseline food price（XPRP AGR の 2020 年比）
for _, r in X['Baseline food price'].iterrows():
    m = r.Model
    if m not in D: rec('Baseline food price', m, f'{r.Region} {r.Year}', r.Value, np.nan, '', 'CSV なし'); continue
    reg = r.Region
    f = lambda y: reg_val(m, 'XPRP', 'AGR', reg, 'BAU_NoCC', y) if reg != 'RTW' else np.nan
    rec('Baseline food price', m, f'{r.Region} {r.Year}', r.Value, f(int(r.Year)) / f(2020), 'XPRP AGR(t) / XPRP AGR(2020), BAU_NoCC',
        'RTW は価格の集計方法が不明' if reg == 'RTW' else '')

# ---------------- 4. Calorie intake change in 2050（WLD）
fao = cb[cb.Year == 2020].set_index(['Model', 'Region']).CALO_fao
POPX = X['Population'].set_index(['Region', 'Year']).POP
for _, r in X['Calorie intake change in 2050'].iterrows():
    m = r.Model
    if m not in D: rec('Calorie intake change in 2050', m, f'{r.RCP} {r.Effect}', r.Value, np.nan, '', 'CSV なし'); continue
    rc, ef = nrcp(r.RCP), neff(r.Effect)
    sc = fao[(m, 'WLD')] / get(m, 'CALO', 'AGR', 'WLD', 'BAU_NoCC', 2020)
    v1 = effect(m, rc, ef, lambda s: get(m, 'CALO', 'AGR', 'WLD', s, 2050))
    rec('Calorie intake change in 2050', m, f'{r.RCP} {r.Effect}', r.Value, v1, 'ΔCALO AGR WLD 2050（そのまま）')
    rec('Calorie intake change in 2050', m, f'{r.RCP} {r.Effect}', r.Value, v1 * sc,
        'ΔCALO AGR WLD 2050 × CALO_fao(WLD,2020) / CALO(WLD,2020)')
    # 17 地域を FAO の値で補正し、Xia の人口で加重して合計する
    def wld(s):
        return sum(fao[(m, g)] * get(m, 'CALO', 'AGR', g, s, 2050) / get(m, 'CALO', 'AGR', g, 'BAU_NoCC', 2020) * POPX[(g, 2050)]
                   for g in R17) / sum(POPX[(g, 2050)] for g in R17)
    rec('Calorie intake change in 2050', m, f'{r.RCP} {r.Effect}', r.Value, effect(m, rc, ef, wld),
        'Σ_17地域 CALO_fao(r,2020) × ΔCALO(r) / CALO(r,2020) × POP_Xia(r) / Σ POP_Xia')

# ---------------- 5. Price change in 2050（WLD）
for _, r in X['Price change in 2050'].iterrows():
    m = r.Model
    if m not in D: rec('Price change in 2050', m, f'{r.RCP} {r.Effect}', r.Value, np.nan, '', 'CSV なし'); continue
    rc, ef = nrcp(r.RCP), neff(r.Effect)
    p = lambda s, y=2050: get(m, 'XPRP', 'AGR', 'WLD', s, y)
    v1 = sum(p(a) / p(b) - 1 for a, b in pairs(m, rc, ef))
    v2 = effect(m, rc, ef, p) / p('BAU_NoCC', 2020)
    rec('Price change in 2050', m, f'{r.RCP} {r.Effect}', r.Value, v1, 'XPRP AGR WLD 2050 の A/B − 1')
    rec('Price change in 2050', m, f'{r.RCP} {r.Effect}', r.Value, v2, 'ΔXPRP AGR WLD 2050 / XPRP(BAU_NoCC, 2020)')

# ---------------- 6. Crop prod change in 2050（PROD, CALO。5地域と RTW）
for _, r in X['Crop prod change in 2050'].iterrows():
    m = r.Model; key = f'{r.Region} {r.Item} {r.Variable} {r.RCP} {r.Effect}'
    if m not in D: rec('Crop prod change in 2050', m, key, r.Value, np.nan, '', 'CSV なし'); continue
    reg = NAME[r.Region]
    v = effect(m, nrcp(r.RCP), neff(r.Effect), lambda s: reg_val(m, r.Variable, r.Item, reg, s, 2050))
    rec('Crop prod change in 2050', m, key, r.Value, v,
        f'Δ{r.Variable} 2050' + ('（RTW = WLD − 5地域' + ('、POPT で人口加重）' if r.Variable == 'CALO' else '）') if reg == 'RTW' else ''))

# ---------------- 7. CSV に無い変数のシート
for sh in ['Baseline hunger risk', 'Hunger risk change in 2050', 'regional hunger change in 2050']:
    for _, r in X[sh].iterrows():
        val = r.RoH if 'RoH' in r else r.Value
        rec(sh, r.Model, ' '.join(str(r[c]) for c in X[sh].columns if c not in ('Model', 'Value', 'RoH')), val, np.nan, '',
            '飢餓リスク（RoH）は CSV に無い')
for _, r in X['sensitivity analysis'].iterrows():
    rec('sensitivity analysis', 'AIM?', f'{r.Category} {r.Group} {r.Variable} {r.RCP} {r.Effect}', r.Value, np.nan, '',
        'SSP1・大気汚染の感度分析のシナリオは CSV に無い')

# ---------------- 出力
det = pd.DataFrame(rows)
det.to_csv(os.path.join(DATA, 'xia_check_detail.csv'), index=False, encoding='utf-8-sig')
det['eff'] = det.key.str.extract(r'((?:SSP2-|RCP)\d\.\d \w+)', expand=False)
summ = det.groupby(['sheet', 'method', 'Model', 'status'], dropna=False).size().unstack('status', fill_value=0).reset_index()
summ.to_csv(os.path.join(DATA, 'xia_check_summary.csv'), index=False, encoding='utf-8-sig')
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 70); pd.set_option('display.max_rows', 500)
print(summ.to_string())
