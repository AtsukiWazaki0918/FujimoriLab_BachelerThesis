# -*- coding: utf-8 -*-
"""../data/level.csv（01_extract_level.py が作る）から新しいシナリオ定義・差分（effect）を作り直す。

シナリオは 4 本だけを使う。オゾンは明示的に扱わず、気候条件の一部として扱う。
  Baseline    = SSP2_BaU_CS_NoCC_woO3    緩和策なし・気候変化なし（オゾン変化なし）
  RCP26       = SSP2_BaU_CS_RCP26_wO3    緩和策なし・RCP2.6 の気候
  RCP70       = SSP2_BaU_CS_RCP70_wO3    緩和策なし・RCP7.0 の気候
  RCP26_MITI  = SSP2_500C_CS_RCP26_wO3   緩和策あり・RCP2.6 の気候

差分は 4 つ。SSP2-2.6 側は Climate change + Mitigation = Combined effect が厳密に成立する。
  1 Climate change (SSP2-2.6) = RCP26      - Baseline
  2 Mitigation     (SSP2-2.6) = RCP26_MITI - RCP26
  3 Combined effect(SSP2-2.6) = RCP26_MITI - Baseline
  4 Climate change (SSP2-7.0) = RCP70      - Baseline
"""
import os, pandas as pd

CSV = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data'))
SCEN = {                       # 短縮名 : (GDX のシナリオ名, 緩和策条件, 気候条件)
    'Baseline'  : ('SSP2_BaU_CS_NoCC_woO3',  'BaU',  'NoCC'),
    'RCP26'     : ('SSP2_BaU_CS_RCP26_wO3',  'BaU',  'RCP2.6'),
    'RCP70'     : ('SSP2_BaU_CS_RCP70_wO3',  'BaU',  'RCP7.0'),
    'RCP26_MITI': ('SSP2_500C_CS_RCP26_wO3', '500C', 'RCP2.6'),
}
EFFECTS = [
    (1, 'Climate change (SSP2-2.6)',  '気候変動影響（SSP2-2.6）',   'SSP2-2.6', 'RCP26',      'Baseline'),
    (2, 'Mitigation (SSP2-2.6)',      '緩和策影響（SSP2-2.6）',     'SSP2-2.6', 'RCP26_MITI', 'RCP26'),
    (3, 'Combined effect (SSP2-2.6)', '総合影響（SSP2-2.6）',       'SSP2-2.6', 'RCP26_MITI', 'Baseline'),
    (4, 'Climate change (SSP2-7.0)',  '気候変動影響（SSP2-7.0）',   'SSP2-7.0', 'RCP70',      'Baseline'),
]
YEAR = 2050
IDX = ['concept','VAR','ITEM','ITEM_label','item_type','UNIT','region','Y']

level = pd.read_csv(os.path.join(CSV, 'level.csv'))
level.columns = [c.lstrip('﻿') for c in level.columns]
inv = {v[0]: k for k, v in SCEN.items()}
level['label'] = level['SCENARIO'].map(inv)

scenario_def = pd.DataFrame(
    [{'シナリオ名': k, 'GDXのシナリオ名': v[0], '緩和策条件': v[1], '気候条件': v[2]}
     for k, v in SCEN.items()])

lv = level[level['label'].notna() & (level.Y == YEAR)]
wide = lv.pivot_table(index=IDX, columns='label', values='value')

rows = []
for no, en, jp, rcp, tgt, ref in EFFECTS:
    d = wide[[tgt, ref]].dropna().reset_index()
    d['effect_no'] = no; d['Factor'] = en; d['effect'] = jp; d['RCP'] = rcp
    d['scenario_target'] = tgt; d['scenario_ref'] = ref
    d['value_target'] = d[tgt]; d['value_ref'] = d[ref]
    d['diff'] = d[tgt] - d[ref]
    d['pct'] = (d[tgt] / d[ref] - 1) * 100
    rows.append(d.drop(columns=[tgt, ref]))
effect = pd.concat(rows, ignore_index=True)[
    IDX + ['effect_no','Factor','effect','RCP','scenario_target','scenario_ref',
           'value_target','value_ref','diff','pct']]

pv = effect.pivot_table(index=IDX, columns='effect_no', values='diff')
print('検算 (1)+(2)-(3) の最大絶対誤差:', (pv[1] + pv[2] - pv[3]).abs().max())
print('行数 effect:', len(effect), ' level(4シナリオ):', len(lv))

effect.to_csv(os.path.join(CSV, 'effect.csv'), index=False, encoding='utf-8-sig')
scenario_def.to_csv(os.path.join(CSV, 'scenario.csv'), index=False, encoding='utf-8-sig')
level[level['label'].notna()].to_csv(os.path.join(CSV, 'level4.csv'), index=False, encoding='utf-8-sig')
print('書き出し完了')
