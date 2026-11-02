# -*- coding: utf-8 -*-
"""
カロリーベース（million kcal）の水準データを GDX から取り出す。
  入力 : ../data/AGMIP_all_scenario.gdx (AGMIP_agg)
  出力 : ../data/level_kcal.csv       4 シナリオ × 2015〜2050 年
         ../data/level_kcal_2050.csv  上のうち 2050 年のみ（04_calc_effect_kcal.py が読む）

元の level_kcal.csv / level_kcal_2050.csv（2026-09-17 作成）は、作成時のスクリプトが保存されていなかった。
このスクリプトは 2026-11-02 に作り直したもので、8/31 版 GDX から元の CSV と同じ 35,542 行・同じ値
（相対誤差 3e-16 以下）が得られることを確認済み。
注意 : GDX の million kcal 単位には JPN の行が無いため、日本は含まれない。
"""
import os
import pandas as pd
import gamspy_base, gams.transfer as gt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, '..', 'data'))
GDX  = os.path.join(DATA, 'AGMIP_all_scenario.gdx')

SCEN = {'SSP2_BaU_CS_NoCC_woO3': 'Baseline', 'SSP2_BaU_CS_RCP26_wO3': 'RCP26',
        'SSP2_BaU_CS_RCP70_wO3': 'RCP70',    'SSP2_500C_CS_RCP26_wO3': 'RCP26_MITI'}
VARS   = ['PROD', 'NETT', 'FOOD', 'FEED', 'OTHU']
ITEMS  = ['wht','RIC','CGR','OSD','SGC','ocr','VFN','CRP','RUM','NRM','DRY','LSP','AGR','tot']
REGIONS = ['CHN','IND','XSE','XSA','XOC','USA','CAN','XE25','XER','TUR','CIS',
           'BRA','XLM','XME','XNF','XAF','World']           # 17 地域から JPN を除く（データが無い）
YEARS  = [str(y) for y in range(2015, 2051, 5)]

m = gt.Container(system_directory=os.path.dirname(gamspy_base.__file__))
m.read(GDX, symbols=['AGMIP_agg'])
a = m['AGMIP_agg'].records
a.columns = ['SCENARIO', 'region', 'VAR', 'ITEM', 'UNIT', 'Y', 'value']
for c in a.columns[:-1]:
    a[c] = a[c].astype(str)

d = a[(a.UNIT == 'million kcal') & a.VAR.isin(VARS) & a.ITEM.isin(ITEMS) &
      a.SCENARIO.isin(SCEN) & a.region.isin(REGIONS) & a.Y.isin(YEARS)].copy()
d['Y'] = d['Y'].astype(int)
d.insert(0, 'label', d['SCENARIO'].map(SCEN))
d = d[['label','SCENARIO','region','VAR','ITEM','UNIT','Y','value']].reset_index(drop=True)

d.to_csv(os.path.join(DATA, 'level_kcal.csv'), index=False, encoding='utf-8-sig')
d[d.Y == 2050].to_csv(os.path.join(DATA, 'level_kcal_2050.csv'), index=False, encoding='utf-8-sig')
print('level_kcal:', len(d), '行 / 2050 年:', (d.Y == 2050).sum(), '行')
