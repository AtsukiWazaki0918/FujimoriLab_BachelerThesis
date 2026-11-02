# -*- coding: utf-8 -*-
"""
第4章用データ抽出スクリプト
  入力 : AGMIP_all_scenario.gdx (AGMIP_agg), Xiadata.xlsx
  出力 : ../data/ch4_data.xlsx ＋ ../data/*.csv
  （Interim 用にパスを変更。GDX と Xiadata.xlsx は ../data から読み、CSV も ../data に書く）
GDX 読み込みには GAMS 本体は不要（pip の gamspy_base 同梱の libgdxcclib64.so を使用）。
"""
import os
import pandas as pd

HOME   = os.path.expanduser('~')
HERE   = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.normpath(os.path.join(HERE, '..', 'data'))
GDX    = os.path.join(OUTDIR, 'AGMIP_all_scenario.gdx')
XIA    = os.path.join(OUTDIR, 'Xiadata.xlsx')
os.makedirs(OUTDIR, exist_ok=True)

# ---------------------------------------------------------------- 1. GDX 読み込み
if True:   # 別の GDX のキャッシュを誤って読まないよう、キャッシュは使わない
    import gamspy_base, gams.transfer as gt
    sd = os.path.dirname(gamspy_base.__file__)
    m = gt.Container(system_directory=sd)
    m.read(GDX, symbols=['AGMIP_agg'])
    agg = m['AGMIP_agg'].records
    agg.columns = ['SCENARIO', 'region', 'VAR', 'ITEM', 'UNIT', 'Y', 'value']
    for c in agg.columns[:-1]:
        agg[c] = agg[c].astype(str)

# ---------------------------------------------------------------- 2. 定義テーブル
BASE = 'SSP2_BaU_CS_NoCC_woO3'

scenario_def = pd.DataFrame([
    ('SSP2_BaU_CS_NoCC_woO3',  'BaU',  'NoCC',   'なし', 'BAU_NoCC (baseline)'),
    ('SSP2_BaU_CS_NoCC_wO3',   'BaU',  'NoCC',   'あり', '-'),
    ('SSP2_BaU_CS_RCP26_woO3', 'BaU',  'RCP2.6', 'なし', '-'),
    ('SSP2_BaU_CS_RCP26_wO3',  'BaU',  'RCP2.6', 'あり', '-'),
    ('SSP2_BaU_CS_RCP70_woO3', 'BaU',  'RCP7.0', 'なし', 'BAU'),
    ('SSP2_BaU_CS_RCP70_wO3',  'BaU',  'RCP7.0', 'あり', 'OZBAU'),
    ('SSP2_500C_CS_NoCC_woO3', '500C', 'NoCC',   'なし', '-'),
    ('SSP2_500C_CS_NoCC_wO3',  '500C', 'NoCC',   'あり', '-'),
    ('SSP2_500C_CS_RCP26_woO3','500C', 'RCP2.6', 'なし', 'BAU_MITI_RCP26'),
    ('SSP2_500C_CS_RCP26_wO3', '500C', 'RCP2.6', 'あり', 'OZBAU_MITI_RCP26'),
], columns=['SCENARIO', 'mitigation', 'climate', 'ozone', 'Xia_Table1'])
USED4 = ['SSP2_BaU_CS_NoCC_woO3', 'SSP2_BaU_CS_RCP70_wO3',
         'SSP2_500C_CS_NoCC_woO3', 'SSP2_500C_CS_RCP26_wO3']
scenario_def['interim'] = ['○' if x in USED4 else '-' for x in scenario_def['SCENARIO']]

# AIM-Hub 固有 17 地域（非重複・合計が World に一致することを確認済み）
R17 = [('CHN','China'),('IND','India'),('JPN','Japan'),('XSE','Rest of East and South East Asia'),
       ('XSA','Rest of Asia'),('XOC','New Zealand and Australia'),('USA','USA'),('CAN','Canada'),
       ('XE25','EU'),('XER','Rest of EU'),('TUR','Turkey'),('CIS','Former USSR'),
       ('BRA','Brazil'),('XLM','Rest of Latin America'),('XME','Middle East'),
       ('XNF','North Africa'),('XAF','Sub-Sahara')]
# Xia の 6 地域比較にだけ使うモデル内集計地域
XIA6 = [('SEA','South-East Asia'),('OAS','Other Asia'),('SSA','Sub-Saharan Africa')]

region_def = pd.DataFrame(
    [(c, n, '17地域') for c, n in R17] +
    [(c, n, 'Xia6地域(モデル間比較用)') for c, n in XIA6] +
    [('World', 'World', 'グローバル')],
    columns=['region', 'region_name', 'group'])
REGIONS = [c for c, _ in R17] + [c for c, _ in XIA6] + ['World']

YEARS = ['2015','2020','2025','2030','2035','2040','2045','2050']

# ---------------------------------------------------------------- 3. 概念の定義
# concept, VAR, UNIT, item_type, items, main_axis（図の主軸）
CROP6 = ['wht','RIC','CGR','OSD','SGC','AGR']
CONCEPTS = [
 ('外生収量',   'YEXO', 'fm t/ha',          'crop',       CROP6,                                  '作物×地域'),
 ('最終収量',   'YILD', 'fm t/ha',          'crop',       CROP6,                                  '作物×地域'),
 ('生産量',     'PROD', '1000 t',           'crop',       CROP6,                                  '作物×地域'),
 ('生産者価格', 'XPRP', 'Index (2015 = 1)', 'crop',       CROP6,                                  '作物×地域'),
 ('消費者価格', 'XPRC', 'Index (2015 = 1)', 'crop',       CROP6,                                  '作物×地域'),
 ('純貿易',     'NETT', '1000 t',           'crop',       CROP6,                                  '作物×地域'),
 ('農地面積',   'LAND', '1000 ha',          'land_cover', ['CRP','GRS','FOR','ONV','NLD',
                                                           'ECP','AGR','NAT','tot'],             '地域×土地被覆'),
 ('食糧需要',   'FOOD', '1000 t',           'demand_use', CROP6,                                  '地域×用途'),
 ('食糧需要',   'FEED', '1000 t',           'demand_use', CROP6,                                  '地域×用途'),
 ('食糧需要',   'OTHU', '1000 t',           'demand_use', CROP6,                                  '地域×用途'),
 ('カロリー摂取量','CALI','kcal/cap/d',     'crop',       CROP6 + ['CRP','LSP','tot'],            '地域×品目'),
 ('排出量',     'EMIS', 'MtCO2e',           'gas_sector', ['tot','AGR','LAN'],                    '地域×部門×ガス'),
 ('排出量',     'ECO2', 'MtCO2e',           'gas_sector', ['tot','AGR','LAN'],                    '地域×部門×ガス'),
 ('排出量',     'ECH4', 'MtCO2e',           'gas_sector', ['tot','AGR','LAN'],                    '地域×部門×ガス'),
 ('排出量',     'EN2O', 'MtCO2e',           'gas_sector', ['tot','AGR','LAN'],                    '地域×部門×ガス'),
]
concept_def = pd.DataFrame(
    [(c, v, u, t, ' / '.join(it), ax) for c, v, u, t, it, ax in CONCEPTS],
    columns=['concept', 'VAR', 'UNIT', 'item_type', 'items', 'main_axis'])

ITEM_LAB = {'wht':'Wheat','RIC':'Rice','CGR':'Coarse grains','OSD':'Oilseeds','SGC':'Sugar crops',
            'AGR':'Agriculture total','CRP':'Crops total','LSP':'Livestock','tot':'Total',
            'GRS':'Grassland','FOR':'Forest','ONV':'Other natural land','NLD':'Non-arable land',
            'ECP':'Energy crops','NAT':'Natural land (FOR+ONV)','LAN':'Land use sector'}
ITEM_LAB_BY_TYPE = {('land_cover','CRP'): 'Cropland', ('gas_sector','AGR'): 'Agriculture sector',
                    ('gas_sector','tot'): 'Total', ('land_cover','AGR'): 'Cropland + grassland'}

# ---------------------------------------------------------------- 4. level シート
frames = []
for concept, var, unit, itype, items, axis in CONCEPTS:
    d = agg[(agg.VAR == var) & (agg.UNIT == unit) & agg.ITEM.isin(items) &
            agg.region.isin(REGIONS) & agg.Y.isin(YEARS)].copy()
    d['concept'] = concept
    d['item_type'] = itype
    frames.append(d)
lv = pd.concat(frames, ignore_index=True)
lv['Y'] = lv['Y'].astype(int)
lv = lv.merge(scenario_def, on='SCENARIO', how='left')
lv['ITEM_label'] = [ITEM_LAB_BY_TYPE.get((t, i), ITEM_LAB.get(i, i))
                    for t, i in zip(lv['item_type'], lv['ITEM'])]
level = lv[['concept','VAR','ITEM','ITEM_label','item_type','UNIT','region','Y',
            'SCENARIO','mitigation','climate','ozone','value']] \
        .sort_values(['concept','VAR','ITEM','region','SCENARIO','Y']).reset_index(drop=True)

# ---------------------------------------------------------------- 5. effect シート
# 中間報告用の 4 分解。② + ③ = ④ が厳密に成立する（同じ 2 シナリオを経由するため）。
EFFECTS = [
 (1, 'Climate Change',   '気候・オゾン影響',
     'SSP2_BaU_CS_RCP70_wO3',   'SSP2_BaU_CS_NoCC_woO3'),
 (2, 'Mitigated Climate', '残存気候・オゾン影響',
     'SSP2_500C_CS_RCP26_wO3',  'SSP2_500C_CS_NoCC_woO3'),
 (3, 'Mitigation Policy', '緩和策の直接影響',
     'SSP2_500C_CS_NoCC_woO3',  'SSP2_BaU_CS_NoCC_woO3'),
 (4, 'Gross Mitigation',  '緩和策の総合影響',
     'SSP2_500C_CS_RCP26_wO3',  'SSP2_BaU_CS_NoCC_woO3'),
]
EFFECT_YEARS = [2050]        # 差分は 2050 年のみ（水準 level は全年入っている）
IDX = ['concept','VAR','ITEM','ITEM_label','item_type','UNIT','region','Y']
wide = level[level.Y.isin(EFFECT_YEARS)].pivot_table(index=IDX, columns='SCENARIO', values='value')
rows = []
for no, name_en, name_jp, tgt, ref in EFFECTS:
    d = wide[[tgt, ref]].dropna().reset_index()
    d['effect_no'] = no
    d['Factor'] = name_en
    d['effect'] = name_jp
    d['scenario_target'] = tgt
    d['scenario_ref'] = ref
    d['value_target'] = d[tgt]
    d['value_ref'] = d[ref]
    d['diff'] = d[tgt] - d[ref]
    d['pct']  = (d[tgt] / d[ref] - 1) * 100
    rows.append(d.drop(columns=[tgt, ref]))
effect = pd.concat(rows, ignore_index=True)
effect = effect[IDX + ['effect_no','Factor','effect','scenario_target','scenario_ref',
                       'value_target','value_ref','diff','pct']]

# 検算 : ② + ③ = ④ が成立するか
_k = IDX
_p = effect.pivot_table(index=_k, columns='effect_no', values='diff')
_gap = (_p[2] + _p[3] - _p[4]).abs().max()
print('検算 ②+③-④ の最大絶対誤差:', _gap)

# ---------------------------------------------------------------- 6. Xia 比較用（モデル間比較）
xf = pd.ExcelFile(XIA)
xia_prod = xf.parse('Crop prod change in 2050')
xia_prod['Model'] = xia_prod['Model'].replace({'AIM': 'AIM-Hub (Xia)'})
xia_prod = xia_prod.rename(columns={'Value': 'value'}); xia_prod['source'] = 'Xia et al. 2026'

XITEM = {'RIC':'RIC','wht':'WHT','CGR':'CGR','OSD':'OSD','SGC':'SGC'}
RMAP  = {'CHN':'China','IND':'India','SEA':'South-East Asia','OAS':'Other Asia','SSA':'Sub-Saharan Africa'}
EMAP  = {'Climate change effect':'climate effect','Mitigation effect':'mitigation effect',
         'Ozone change effect':'ozone reduction effect'}
p = effect[(effect.VAR == 'PROD') & (effect.Y == 2050) & (effect.ITEM.isin(XITEM))]
sub = p[p.region.isin(list(RMAP) + ['World'])][['region','ITEM','effect','Factor','effect_no','diff']]
pv = sub.pivot_table(index=['ITEM','effect','Factor','effect_no'], columns='region', values='diff').reset_index()
pv['RTW'] = pv['World'] - pv[list(RMAP)].sum(axis=1)
long = pv.melt(id_vars=['ITEM','effect','Factor','effect_no'], value_vars=list(RMAP) + ['RTW'],
               var_name='region', value_name='value')
RMAP2 = dict(RMAP); RMAP2['RTW'] = 'Rest of the world'
aim = pd.DataFrame({'Model':'AIM-Alpha (this study)', 'Region':long['region'].map(RMAP2),
                    'Item':long['ITEM'].map(XITEM), 'Variable':'PROD', 'Year':2050,
                    'value':long['value'],
                    'RCP':'-', 'Effect':long['Factor'], 'source':'This study'})
xia_prod_all = pd.concat([xia_prod, aim], ignore_index=True)

xia_price = xf.parse('Price change in 2050')
xia_price['Model'] = xia_price['Model'].replace({'AIM': 'AIM-Hub (Xia)'})
xia_price = xia_price.rename(columns={'Value': 'value'}); xia_price['source'] = 'Xia et al. 2026'
pw = level[(level.VAR == 'XPRP') & (level.ITEM == 'AGR') & (level.region == 'World')]
p2020 = pw[(pw.Y == 2020) & (pw.SCENARIO == BASE)]['value'].iloc[0]
pw50 = pw[pw.Y == 2050].set_index('SCENARIO')['value'] / p2020
prow = [{'Model':'AIM-Alpha (this study)', 'value':pw50[t] - pw50[r], 'RCP':'-',
         'Effect':name_en, 'source':'This study'}
        for no, name_en, name_jp, t, r in EFFECTS]
xia_price_all = pd.concat([xia_price, pd.DataFrame(prow)], ignore_index=True)

# ---------------------------------------------------------------- 7. 書き出し
readme = pd.DataFrame([
 ('concept',   '概念と変数の対応表。item_type と図の主軸もここに書いてある。'),
 ('scenario',  'シナリオ定義。interim 列に○が付く 4 本だけを中間報告で使う。'),
 ('region',    '地域定義。17地域は非重複で合計が World に一致する。'),
 ('level',     '水準データ。concept×VAR×ITEM×region×Y×SCENARIO の long 形式（10 シナリオ全部）。'),
 ('effect',    '差分データ。2050 年。effect_no が 1〜4 の 4 分解のみ。'),
 ('xia_prod',  'モデル間比較用（生産量）。当面は使わない。'),
 ('xia_price', 'モデル間比較用（農産物価格指数）。当面は使わない。'),
 ('', ''),
 ('個別効果の分解（中間報告版）', ''),
 ('① Climate Change',    'SSP2_BaU_CS_RCP70_wO3 − SSP2_BaU_CS_NoCC_woO3 : 気候・オゾン影響'),
 ('② Mitigated Climate', 'SSP2_500C_CS_RCP26_wO3 − SSP2_500C_CS_NoCC_woO3 : 残存気候・オゾン影響'),
 ('③ Mitigation Policy', 'SSP2_500C_CS_NoCC_woO3 − SSP2_BaU_CS_NoCC_woO3 : 緩和策の直接影響'),
 ('④ Gross Mitigation',  'SSP2_500C_CS_RCP26_wO3 − SSP2_BaU_CS_NoCC_woO3 : 緩和策の総合影響（② + ③ に厳密一致）'),
 ('', ''),
 ('item_type の意味', ''),
 ('crop',       'ITEM が作物（wht/RIC/CGR/OSD/SGC）と集計（AGR/CRP/LSP/tot）'),
 ('land_cover', 'ITEM が土地被覆区分。CRP+GRS+FOR+ONV+NLD = tot（非重複）。NAT=FOR+ONV、AGR=CRP+GRS、ECP は CRP の内数なので積み上げに入れない。'),
 ('demand_use', 'VAR が用途（FOOD 食用 / FEED 飼料 / OTHU その他）。CONS は使わない。'),
 ('gas_sector', 'ITEM が部門（tot / AGR 農業 / LAN 土地利用）。tot = AGR + LAN。EMIS = ECO2 + ECH4 + EN2O。ECO2 には AGR の行が無い（農業部門の直接CO2は報告されない）。'),
], columns=['sheet / 項目', '説明'])

# OneDrive フォルダへの直接書き込みは遅いので、いったんローカルに書いてからコピーする
import shutil
TMP = os.path.join(HOME, '_ch4_build'); os.makedirs(TMP, exist_ok=True)
tmp_xlsx = os.path.join(TMP, 'ch4_data.xlsx')
with pd.ExcelWriter(tmp_xlsx, engine='xlsxwriter') as w:
    readme.to_excel(w, sheet_name='README', index=False)
    concept_def.to_excel(w, sheet_name='concept', index=False)
    scenario_def.to_excel(w, sheet_name='scenario', index=False)
    region_def.to_excel(w, sheet_name='region', index=False)
    level.to_excel(w, sheet_name='level', index=False)
    effect.to_excel(w, sheet_name='effect', index=False)
    xia_prod_all.to_excel(w, sheet_name='xia_prod', index=False)
    xia_price_all.to_excel(w, sheet_name='xia_price', index=False)

csvdir = OUTDIR; os.makedirs(csvdir, exist_ok=True)
for nm, df in [('level', level), ('effect', effect), ('concept', concept_def),
               ('scenario', scenario_def), ('region', region_def),
               ('xia_prod', xia_prod_all), ('xia_price', xia_price_all)]:
    tmp = os.path.join(TMP, nm + '.csv')
    df.to_csv(tmp, index=False, encoding='utf-8-sig')
    shutil.copyfile(tmp, os.path.join(csvdir, nm + '.csv'))

out = os.path.join(OUTDIR, 'ch4_data.xlsx')
try:                                   # Excel で開いたままだと上書きできないので別名に退避
    shutil.copyfile(tmp_xlsx, out)
except PermissionError:
    out = os.path.join(OUTDIR, 'ch4_data_new.xlsx')
    shutil.copyfile(tmp_xlsx, out)
    print('!! ch4_data.xlsx を開いたままなので', os.path.basename(out), 'に書き出しました')

print('written:', out)
print('level', level.shape, 'effect', effect.shape)
print(level.groupby(['concept','VAR'])['value'].size().to_string())
