# -*- coding: utf-8 -*-
"""
外生収量の入出力整合性チェック（17 地域 × 5 作物 × 10 シナリオ）
  入力 : 収量入力ClimateShifters2.gdx  CEXO（woO3 用）, OZYEXO（wO3 用）, AREA（重み）
  出力 : ../data/level.csv の YEXO（元は ch4/csv/level.csv。8/31 版 AGMIP_all_scenario.gdx 由来, fm t/ha）
  地域対応 : all_scenario_global_17.gdx の cty_reg_map ＋ 入力側 iso2cty
比較指標
  (A) 2020-2050 年平均成長率 [%/yr]
      入力 = 国別成長率 g の収穫面積（AREA tot）加重平均
      出力 = (YEXO2050 / YEXO2020)^(1/30) - 1
  (B) 2050 年の NoCC 比変化率 [%]
      入力 = 面積加重 ((1+g_s)/(1+g_nocc))^30 - 1
      出力 = YEXO_s,2050 / YEXO_(同じ緩和策の NoCC_woO3),2050 - 1
使い方 : python <このファイル>（引数なし。どこから実行してもよい）
  元は アウトプット/yexo_check/yexo_scatter.py（2026-10-28）。パスだけを書き換えた。
  figA_yexo_io_growth.py と figB_yexo_io_change.py は中身が同じ。どちらを実行しても図2枚と表が出る。
"""
import sys, os, pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
import gams.transfer as gt, gamspy_base

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DEF, DATA, OUT = (os.path.join(ROOT, x) for x in ('define', 'data', 'output'))
sd = gamspy_base.directory

# ---------------- 1. 地域対応（入力 CTY → 17 地域）
R17 = ["CHN","IND","JPN","XSE","XSA","XOC","USA","CAN","XE25","XER","TUR",
       "CIS","BRA","XLM","XME","XNF","XAF"]
cin = gt.Container(os.path.join(DEF, 'ClimateShifters2.gdx'), system_directory=sd)
g17 = gt.Container(system_directory=sd); g17.read(os.path.join(DATA, 'all_scenario_global_17.gdx'), symbols=['cty_reg_map'])
i2c = cin['iso2cty'].records[['ISO','CTY']].astype(str)
m = g17['cty_reg_map'].records.astype(str).iloc[:, :2]; m.columns = ['ISO','reg']
x = i2c.merge(m[m.reg.isin(R17)], on='ISO', how='inner')
# 1 つの CTY が複数地域にまたがる場合は CTY と同名 ISO（本体国）の地域を採る
x['self'] = x.ISO == x.CTY
x = x.sort_values('self', ascending=False).drop_duplicates('CTY')
cty2reg = dict(zip(x.CTY, x.reg))
cty2reg.update({'CHM':'CHN', 'CHP':'XER', 'ISL':'XER', 'HRV':'XER',   # iso2cty で拾えないもの
                'FRP':'XE25', 'OSA':'XSE', 'OAO':'XAF'})                # 本体国のない混在 CTY

# ---------------- 2. 作物対応（IMPACT j → AgMIP 5 作物）
J2I = {'jwhea':'wht', 'jrice':'RIC',
       'jmaiz':'CGR','jbarl':'CGR','jmill':'CGR','jsorg':'CGR','jocer':'CGR',
       'jsoyb':'OSD','jsbnt':'OSD','jrpsd':'OSD','jrpnt':'OSD','jgrnd':'OSD','jgdnt':'OSD',
       'jsnfl':'OSD','jsfnt':'OSD','jtols':'OSD','jtont':'OSD','jpalm':'OSD',
       'jsugc':'SGC','jsugb':'SGC'}
ITEM5 = ['wht','RIC','CGR','OSD','SGC']
ITEM_LAB = {'wht':'Wheat','RIC':'Rice','CGR':'Coarse grains','OSD':'Oilseeds','SGC':'Sugar crops'}

# ---------------- 3. 入力の集計
area = cin['AREA'].records
area = area[area.land == 'tot'][['j','CTY','value']].rename(columns={'value':'w'})
def prep(sym):
    r = cin[sym].records
    r = r[r.land == 'tot'][['j','CTY','rcp','value']].astype({'j':str,'CTY':str,'rcp':str})
    return r.pivot_table(index=['j','CTY'], columns='rcp', values='value').reset_index()
inp = []
for sym, o3 in [('CEXO','woO3'), ('OZYEXO','wO3')]:
    p = prep(sym)
    for rcp, clim in [('nocc','NoCC'), ('rcp2p6','RCP26'), ('rcp7p0','RCP70')]:
        d = p[['j','CTY']].copy()
        d['g'] = p[rcp]
        d['chg'] = ((1 + p[rcp]) / (1 + p['nocc']))**30 - 1
        d['clim'], d['o3'] = clim, o3
        inp.append(d)
inp = pd.concat(inp).dropna(subset=['g'])
inp['ITEM'] = inp.j.map(J2I); inp['region'] = inp.CTY.map(cty2reg)
area = area.astype({'j':str,'CTY':str})
inp = inp.merge(area, on=['j','CTY'], how='left').dropna(subset=['ITEM','region'])
inp = inp[inp.w > 0]
agg = (inp.assign(gw=inp.g*inp.w, cw=inp.chg*inp.w)
          .groupby(['ITEM','region','clim','o3'])[['gw','cw','w']].sum().reset_index())
agg['in_g'] = agg.gw / agg.w * 100
agg['in_chg'] = agg.cw / agg.w * 100

# ---------------- 4. 出力の整理
lv = pd.read_csv(os.path.join(DATA, 'level.csv'))
lv = lv[(lv.VAR == 'YEXO') & (lv.UNIT == 'fm t/ha') & lv.ITEM.isin(ITEM5) &
        lv.region.isin(R17) & lv.Y.isin([2020, 2050])]
w = lv.pivot_table(index=['ITEM','region','SCENARIO'], columns='Y', values='value').reset_index()
w['out_g'] = ((w[2050] / w[2020])**(1/30) - 1) * 100
sp = w.SCENARIO.str.extract(r'SSP2_(?P<miti>\w+?)_CS_(?P<clim>\w+?)_(?P<o3>wO3|woO3)')
w = pd.concat([w, sp], axis=1)
base = w[(w.clim == 'NoCC') & (w.o3 == 'woO3')][['ITEM','region','miti',2050]].rename(columns={2050:'b'})
w = w.merge(base, on=['ITEM','region','miti'])
w['out_chg'] = (w[2050] / w.b - 1) * 100

df = w.merge(agg[['ITEM','region','clim','o3','in_g','in_chg','w']],
             on=['ITEM','region','clim','o3'], how='left')
df = df[['ITEM','region','SCENARIO','miti','clim','o3', 2020, 2050, 'w',
         'in_g','out_g','in_chg','out_chg']].rename(columns={2020:'YEXO2020', 2050:'YEXO2050','w':'area_1000ha'})
df.to_csv(os.path.join(DATA, 'yexo_io_check.csv'), index=False, encoding='utf-8-sig')

# ---------------- 5. 作図
for f in ['Times New Roman','Liberation Serif','DejaVu Serif']:
    if any(f in x.name for x in matplotlib.font_manager.fontManager.ttflist):
        plt.rcParams['font.family'] = f; break
plt.rcParams.update({'font.size': 8, 'axes.spines.top': False, 'axes.spines.right': False})
COL = {('NoCC','woO3'):'#4d4d4d', ('NoCC','wO3'):'#a6a6a6',
       ('RCP26','woO3'):'#2166ac', ('RCP26','wO3'):'#92c5de',
       ('RCP70','woO3'):'#b2182b', ('RCP70','wO3'):'#f4a582'}
LAB = {('NoCC','woO3'):'NoCC (CEXO)', ('NoCC','wO3'):'NoCC + O3 (OZYEXO)',
       ('RCP26','woO3'):'RCP2.6 (CEXO)', ('RCP26','wO3'):'RCP2.6 + O3 (OZYEXO)',
       ('RCP70','woO3'):'RCP7.0 (CEXO)', ('RCP70','wO3'):'RCP7.0 + O3 (OZYEXO)'}

def scatter(xc, yc, xl, yl, fname, skip_base=False):
    fig, axs = plt.subplots(2, 3, figsize=(16/2.54, 11/2.54))
    for ax, it in zip(axs.flat, ITEM5):
        d = df[df.ITEM == it]
        if skip_base: d = d[~((d.clim == 'NoCC') & (d.o3 == 'woO3'))]
        for (cl, o3), col in COL.items():
            for mi, mk in [('BaU', 'o'), ('500C', '^')]:
                s = d[(d.clim == cl) & (d.o3 == o3) & (d.miti == mi)]
                ax.scatter(s[xc], s[yc], s=10, marker=mk, linewidths=0.6,
                           facecolors=col if mi == 'BaU' else 'none', edgecolors=col)
        lo = np.nanmin(d[[xc, yc]].values); hi = np.nanmax(d[[xc, yc]].values)
        pad = (hi - lo) * 0.05; lo, hi = lo - pad, hi + pad
        ax.plot([lo, hi], [lo, hi], color='black', lw=0.5, ls='--')
        ax.set_xlim(lo, hi); ax.set_ylim(lo, hi); ax.set_aspect('equal')
        ax.text(0.03, 0.97, ITEM_LAB[it], transform=ax.transAxes, va='top')
        ax.set_xlabel(xl); ax.set_ylabel(yl)
    lax = axs.flat[5]; lax.axis('off')
    for (k, col) in COL.items():
        if skip_base and k == ('NoCC','woO3'): continue
        lax.scatter([], [], s=10, color=col, label=LAB[k])
    lax.scatter([], [], s=10, marker='o', facecolors='k', edgecolors='k', label='BaU (filled)')
    lax.scatter([], [], s=10, marker='^', facecolors='none', edgecolors='k', label='500C (open)')
    lax.plot([], [], color='black', lw=0.5, ls='--', label='1:1 line')
    lax.legend(loc='center', frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, fname), dpi=600); plt.close(fig)

scatter('in_g', 'out_g', 'Input shifter (%/yr)',
        'Output YEXO (%/yr)', 'figA_yexo_io_growth.png')
scatter('in_chg', 'out_chg', 'Input shifter (%)',
        'Output YEXO (%)', 'figB_yexo_io_change.png', skip_base=True)

# ---------------- 6. 数値の要約
def stats(xc, yc):
    r = []
    for (it, cl, o3, mi), d in df.groupby(['ITEM','clim','o3','miti']):
        d = d.dropna(subset=[xc, yc])
        if len(d) < 3 or d[xc].std() < 1e-9: continue
        r.append((it, cl, o3, mi, len(d), np.corrcoef(d[xc], d[yc])[0,1],
                  np.polyfit(d[xc], d[yc], 1)[0], (d[yc]-d[xc]).mean(), (d[yc]-d[xc]).abs().max()))
    return pd.DataFrame(r, columns=['ITEM','clim','o3','miti','n','r','slope','mean_diff','max_absdiff'])
sa, sb = stats('in_g','out_g'), stats('in_chg','out_chg')
with pd.ExcelWriter(os.path.join(DATA, 'yexo_io_check.xlsx')) as xw:
    df.to_excel(xw, sheet_name='data', index=False); sa.to_excel(xw, sheet_name='stats_growth', index=False)
    sb.to_excel(xw, sheet_name='stats_change', index=False)
pd.set_option('display.width', 200)
print(sa.round(3).to_string()); print(sb.round(3).to_string())
print('missing input:', df[df.in_g.isna()][['ITEM','region']].drop_duplicates().values.tolist())
