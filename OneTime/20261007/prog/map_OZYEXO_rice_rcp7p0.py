# -*- coding: utf-8 -*-
"""map_OZYEXO_rice_rcp7p0.py : rice・wheat × RCP7.0・RCP2.6 の変化率の世界地図
  map_OZYEXO_rice_rcp7p0.py / map_OZYEXO_rice_rcp2p6.py / map_OZYEXO_wheat_rcp7p0.py /
  map_OZYEXO_wheat_rcp2p6.py の 4 ファイルは中身が同じ（元は アウトプット/map.py の 1 本）。
  どれを実行しても ../output に 4 枚すべてが出る。ファイル名は output との対応を示すためのもの。
  入力 : ../define/ClimateShifters2.gdx（国対応表 iso2cty）、../data/ozyexo_tot_rice_wheat.csv（01 が作る）、
         ../data/ne_50m_admin_0_countries.geojson（Natural Earth の国境データ）
  元は アウトプット/map.py（2026-10-07）。パスと出力ファイル名だけを書き換えた。
"""
import os
HERE   = os.path.dirname(os.path.abspath(__file__))
ROOT   = os.path.normpath(os.path.join(HERE, '..'))
GDX    = os.path.join(ROOT, 'define', 'ClimateShifters2.gdx')
DATA   = os.path.join(ROOT, 'data')
OUTDIR = os.path.join(ROOT, 'output')
import geopandas as gpd, pandas as pd, numpy as np, sys, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
import gams.transfer as gt, gamspy_base
c=gt.Container(GDX, system_directory=gamspy_base.directory)
mp=c['iso2cty'].records[['ISO','CTY']].astype(str)
p=pd.read_csv(os.path.join(DATA, 'ozyexo_tot_rice_wheat.csv'))
w=gpd.read_file(os.path.join(DATA, 'ne_50m_admin_0_countries.geojson'))
w=w[w.ADM0_A3!='ATA']
iso=w['ADM0_A3'].astype(str)
fix={'SDS':'SSD','KOS':'KO-','PSX':'PSE','SAH':'ESH','CYN':'CYP','SOL':'SOM','KAB':'KAZ','ALD':'FIN'}
iso=iso.replace(fix)
m=dict(zip(mp.ISO,mp.CTY)); m['CHN']='CHM'
ctys=set(p.CTY)
w['CTY']=[i if i in ctys else m.get(i) for i in iso]
bounds=[-30,-10,-5,-1,1,5,10,20,40,90]
cols=['#b2182b','#ef8a62','#fddbc7','#f7f7f7','#d1e5f0','#92c5de','#4393c3','#2166ac','#053061']
cmap=ListedColormap(cols); norm=BoundaryNorm(bounds,cmap.N)
crop={'jrice':'Rice','jwhea':'Wheat'}; rcpn={'rcp7p0':'RCP7.0 (IPSL-CM6A-LR)','rcp2p6':'RCP2.6 (GFDL-ESM4)'}
for j in crop:
  for r in rcpn:
    s=p[p.j==j][['CTY',f'chg2050_{r}']]
    g=w.merge(s,on='CTY',how='left')
    fig,ax=plt.subplots(figsize=(11,5.6))
    g[g[f'chg2050_{r}'].isna()].plot(ax=ax,color='#d9d9d9',edgecolor='white',linewidth=0.2)
    g[g[f'chg2050_{r}'].notna()].plot(ax=ax,column=f'chg2050_{r}',cmap=cmap,norm=norm,edgecolor='#555555',linewidth=0.2)
    ax.set_axis_off(); ax.set_xlim(-180,180); ax.set_ylim(-58,85)
    ax.set_title(f'{crop[j]} — OZYEXO (tot), {rcpn[r]} vs NoCC\nYield change in 2050 [%]  = ((1+g_RCP)/(1+g_NoCC))^30 − 1',fontsize=11)
    sm=plt.cm.ScalarMappable(cmap=cmap,norm=norm)
    cb=fig.colorbar(sm,ax=ax,orientation='horizontal',fraction=0.045,pad=0.02,ticks=bounds,spacing='uniform')
    cb.set_label('% (grey = no data)')
    fig.tight_layout()
    fig.savefig(os.path.join(OUTDIR, f'map_OZYEXO_{crop[j].lower()}_{r}.png'),dpi=200,bbox_inches='tight',pad_inches=0.15); plt.close()
un=sorted(set(p.CTY)-set(w.CTY.dropna())); print('CTY not on map:',un)
