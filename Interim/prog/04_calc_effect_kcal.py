# -*- coding: utf-8 -*-
"""../data/level_kcal_2050.csv（02_extract_level_kcal.py が作る）（AgMIP の million kcal 単位）から
   カロリーベースの差分 ../data/effect_kcal.csv を作る。

   単位は PJ（10^15 J）に換算する。1 million kcal = 4.184e-6 PJ。
   作物や品目をまたいで足し合わせる図は、この単位で描く。
"""
import os, pandas as pd

CSV = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data'))
SRC = os.path.join(CSV, 'level_kcal_2050.csv')
KCAL_TO_PJ = 4.184e-6          # 1 million kcal = 4.184e9 J = 4.184e-6 PJ

EFFECTS = [
    (1, 'Climate change (SSP2-2.6)',  '気候変動影響（SSP2-2.6）',   'SSP2-2.6', 'RCP26',      'Baseline'),
    (2, 'Mitigation (SSP2-2.6)',      '緩和策影響（SSP2-2.6）',     'SSP2-2.6', 'RCP26_MITI', 'RCP26'),
    (3, 'Combined effect (SSP2-2.6)', '総合影響（SSP2-2.6）',       'SSP2-2.6', 'RCP26_MITI', 'Baseline'),
    (4, 'Climate change (SSP2-7.0)',  '気候変動影響（SSP2-7.0）',   'SSP2-7.0', 'RCP70',      'Baseline'),
]
IDX = ['VAR', 'ITEM', 'region', 'Y']

d = pd.read_csv(SRC)
d.columns = [c.lstrip('﻿') for c in d.columns]
d['value'] = d['value'] * KCAL_TO_PJ
wide = d.pivot_table(index=IDX, columns='label', values='value')

rows = []
for no, en, jp, rcp, tgt, ref in EFFECTS:
    x = wide[[tgt, ref]].dropna().reset_index()
    x['effect_no'] = no; x['Factor'] = en; x['effect'] = jp; x['RCP'] = rcp
    x['scenario_target'] = tgt; x['scenario_ref'] = ref
    x['UNIT'] = 'PJ'
    x['value_target'] = x[tgt]; x['value_ref'] = x[ref]
    x['diff'] = x[tgt] - x[ref]
    x['pct'] = (x[tgt] / x[ref] - 1) * 100
    rows.append(x.drop(columns=[tgt, ref]))
eff = pd.concat(rows, ignore_index=True)
eff['concept'] = 'カロリーベース'
eff['ITEM_label'] = eff['ITEM']
eff['item_type'] = 'crop'
eff = eff[['concept','VAR','ITEM','ITEM_label','item_type','UNIT','region','Y',
           'effect_no','Factor','effect','RCP','scenario_target','scenario_ref',
           'value_target','value_ref','diff','pct']]

pv = eff.pivot_table(index=['VAR','ITEM','region','Y'], columns='effect_no', values='diff')
print('検算 (1)+(2)-(3) の最大絶対誤差:', (pv[1] + pv[2] - pv[3]).abs().max(), 'PJ')
eff.to_csv(os.path.join(CSV, 'effect_kcal.csv'), index=False, encoding='utf-8-sig')
print('行数:', len(eff))
