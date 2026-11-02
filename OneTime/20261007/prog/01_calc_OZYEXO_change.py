# -*- coding: utf-8 -*-
"""OZYEXO（land = tot）の rice・wheat について、RCP7.0・RCP2.6 の NoCC からの変化を計算する。
  入力 : ../define/ClimateShifters2.gdx（元の名前は 収量入力ClimateShifters2.gdx）
  出力 : ../data/ozyexo_tot_rice_wheat.csv
  変化率 chg2050_* = ((1+g_RCP)/(1+g_NoCC))^30 − 1（%）。g は 2020→2050 年の年平均成長率。
  元は アウトプット/calc.py（2026-10-07）。Interim と同じ形に整理するため、パスだけを書き換えた。
"""
import os
HERE   = os.path.dirname(os.path.abspath(__file__))
ROOT   = os.path.normpath(os.path.join(HERE, '..'))
GDX    = os.path.join(ROOT, 'define', 'ClimateShifters2.gdx')
DATA   = os.path.join(ROOT, 'data')
OUTDIR = os.path.join(ROOT, 'output')
import gams.transfer as gt, gamspy_base, pandas as pd, sys
c=gt.Container(GDX, system_directory=gamspy_base.directory)
o=c['OZYEXO'].records
o=o[(o.land=='tot')&(o.j.isin(['jrice','jwhea']))]
p=o.pivot_table(index=['j','CTY'],columns='rcp',values='value',observed=True).reset_index()
for r in ['rcp7p0','rcp2p6']:
    p[f'diff_pp_{r}']=(p[r]-p['nocc'])*100
    p[f'chg2050_{r}']=(((1+p[r])/(1+p['nocc']))**30-1)*100
p.to_csv(os.path.join(DATA, 'ozyexo_tot_rice_wheat.csv'),index=False)
print(p.groupby('j',observed=True).describe().T.to_string())
print(p[p.nocc.isna()|p.rcp7p0.isna()|p.rcp2p6.isna()])
