# -*- coding: utf-8 -*-
"""
外生収量の入出力の整合性確認（CTY × モデル品目 × 灌漑/天水）
  入力 : ../define/ClimateShifters2.gdx の CEXO（オゾンなし）と OZYEXO（オゾンあり）
         ../define/impact_c.map（IMPACT j → モデル品目 c）
  出力 : ../data/all_scenario_World.gdx の yldWat_load（外生収量、国 × 流域 × 灌漑/天水, t/ha）
比べる量（両軸とも 2020 年に対する 2050 年の倍率 [-]）
  横軸 = 入力 (1 + g_c)^30。g_c は、c に対応する IMPACT 品目 j の年平均成長率 g（2020-2050）の単純平均。
         モデルと同じく、g を先に平均してから複利計算する。
         NoCC + オゾンあり の g は CEXO(nocc) + {(OZYEXO - CEXO)(rcp2p6) + (OZYEXO - CEXO)(rcp7p0)} / 2
         （ClimateShifters2 の OZYEXO(nocc) は CEXO(nocc) と同じでオゾンの効果を含まないため。モデルの出力と一致する作り方）
  縦軸 = 出力 yldWat_load(2050) / yldWat_load(2020)。流域間で同じ値なので流域の平均をとる
空間解像度 : ClimateShifters2 の CTY。モデルの国（ISO）は iso2cty で CTY に対応づける。
  複数国からなる CTY は、メンバー国の値が同じであることを確かめてからその値を使う。
  図に使うシナリオは緩和策 BaU の6つ（緩和策が違っても入力は同じ）。
  入力と出力の差が 1e-4 以上の点には「CTY（I/R）」の名前を図中に書く。
使い方 : python figC_yexo_io_cty.py（引数なし。どこから実行してもよい）
  出力 : ../output/figC_yexo_io_cty_<c>.png（モデル品目ごと）, ../data/yexo_io_cty.csv, ../data/yexo_io_cty_check.csv
"""
import os, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
import gams.transfer as gt, gamspy_base

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DEF, DATA, OUT = (os.path.join(ROOT, x) for x in ('define', 'data', 'output'))
os.makedirs(OUT, exist_ok=True)
sd = gamspy_base.directory
LAND = {'air': 'Irrigation', 'arf': 'Rainfed'}
# 入力の (記号, rcp) → 出力のシナリオ名の (気候, オゾン)
CLIM = {'nocc': 'NoCC', 'rcp2p6': 'RCP26', 'rcp7p0': 'RCP70'}
O3 = {'CEXO': 'woO3', 'OZYEXO': 'wO3'}
MITI = 'BaU'   # 緩和策が違っても入力は同じなので BaU だけを使う

# ---------------- 1. 入力：j × CTY × 灌漑/天水 の年平均成長率 g
cin = gt.Container(os.path.join(DEF, 'ClimateShifters2.gdx'), system_directory=sd)
def piv(sym):
    r = cin[sym].records.astype({'j': str, 'CTY': str, 'land': str, 'rcp': str})
    r = r[r.land.isin(LAND)].assign(wat=lambda d: d.land.map(LAND))
    return r.pivot_table(index=['j', 'CTY', 'wat'], columns='rcp', values='value')
ce, oy = piv('CEXO'), piv('OZYEXO').reindex(piv('CEXO').index)
oy['nocc'] = ce['nocc'] + ((oy['rcp2p6'] - ce['rcp2p6']).fillna(0) + (oy['rcp7p0'] - ce['rcp7p0']).fillna(0)) / 2
inp = []
for sym, tab in [('CEXO', ce), ('OZYEXO', oy)]:
    t = tab.stack().rename('g').reset_index()
    inp.append(t.assign(clim=t.rcp.map(CLIM), o3=O3[sym]).drop(columns='rcp'))
inp = pd.concat(inp)

# ---------------- 2. j → モデル品目 c（impact_c.map）。g を単純平均してから複利計算
jc = [tuple(x.strip() for x in ln.split('.')) for ln in open(os.path.join(DEF, 'impact_c.map'), encoding='utf-8')]
jc = pd.DataFrame([t for t in jc if len(t) == 2 and all(t)], columns=['j', 'c'])
x = inp.merge(jc, on='j')       # jothr は nut と spc の両方に入る
K = ['c', 'CTY', 'wat', 'clim', 'o3']
g = x.groupby(K)
ins = pd.DataFrame({'g_mean': g.g.mean(), 'n_j': g.j.nunique()}).reset_index()
ins['inp'] = (1 + ins.g_mean) ** 30

# ---------------- 3. 出力：yldWat_load の 2050 / 2020
w = gt.Container(system_directory=sd); w.read(os.path.join(DATA, 'all_scenario_World.gdx'), symbols=['yldWat_load'])
o = w['yldWat_load'].records; del w
o.columns = ['S', 'c', 'bas', 'cty', 'wat', 'Y', 'v']
for col in ['S', 'c', 'bas', 'cty', 'wat', 'Y']: o[col] = o[col].astype(str)
o = o[o.Y.isin(['2020', '2050']) & o.S.str.startswith('SSP2_' + MITI + '_')]
o = o.set_index(['S', 'c', 'bas', 'cty', 'wat', 'Y']).v.unstack('Y').dropna()
o = (o['2050'] / o['2020']).rename('q').reset_index()
sp = o.S.str.extract(r'SSP2_\w+?_CS_(?P<clim>\w+?)_(?P<o3>wO3|woO3)$'); o = pd.concat([o, sp], axis=1)
bs = o.groupby(['S', 'c', 'cty', 'wat']).q.agg(['mean', 'min', 'max']).reset_index()
# モデルの国（ISO）→ CTY。iso2cty に無い3か国は手で対応づける
i2c = cin['iso2cty'].records.astype(str)
iso2cty = dict(zip(i2c.ISO, i2c.CTY)); iso2cty.update({'CHN': 'CHM', 'HKG': 'CHM', 'ISL': 'ISL'})   # HKG は CHN と同じ値なので CHM（CHP はスイス）
bs['CTY'] = bs.cty.map(iso2cty)
bs = bs.merge(o[['S', 'clim', 'o3']].drop_duplicates(), on='S')
gc = bs.groupby(['c', 'CTY', 'wat', 'clim', 'o3'])
outs = pd.DataFrame({'out': gc['mean'].mean(), 'n_iso': gc.cty.nunique(),
                     'spread': gc['max'].max() - gc['min'].min()}).reset_index()

# ---------------- 4. 結合と一致の確認
df = ins.merge(outs, on=K, how='inner')
df['diff'] = df.out - df.inp
df.to_csv(os.path.join(DATA, 'yexo_io_cty.csv'), index=False, encoding='utf-8-sig')
TOL = 1e-4
chk = df.groupby('c').agg(n=('out', 'size'), n_j_max=('n_j', 'max'),
                          n_off=('diff', lambda s: int((s.abs() >= TOL).sum())),
                          max_absdiff=('diff', lambda s: s.abs().max()),
                          max_spread=('spread', 'max')).reset_index()
chk.to_csv(os.path.join(DATA, 'yexo_io_cty_check.csv'), index=False, encoding='utf-8-sig')
pd.set_option('display.width', 200); print(chk.to_string())
print('流域・メンバー国の間の差の最大:', df.spread.max())
print('入力だけにある組:', len(ins.merge(outs, on=K, how='left').query('out != out')),
      ' 出力だけにある組:', len(outs.merge(ins, on=K, how='left').query('inp != inp')))
print('対応のつかないモデルの国:', sorted(set(bs[bs.CTY.isna()].cty)))
print(df[df['diff'].abs() >= TOL][K + ['n_j', 'inp', 'out', 'diff']].to_string())
USE = 'inp'

# ---------------- 5. 作図（モデル品目ごとに1枚）
for f in ['Times New Roman', 'Liberation Serif', 'DejaVu Serif']:
    if any(f in t.name for t in matplotlib.font_manager.fontManager.ttflist):
        plt.rcParams['font.family'] = f; break
plt.rcParams.update({'font.size': 8, 'axes.spines.top': False, 'axes.spines.right': False})
COL = {('NoCC', 'woO3'): '#4d4d4d', ('NoCC', 'wO3'): '#a6a6a6',
       ('RCP26', 'woO3'): '#2166ac', ('RCP26', 'wO3'): '#92c5de',
       ('RCP70', 'woO3'): '#b2182b', ('RCP70', 'wO3'): '#f4a582'}
LAB = {('NoCC', 'woO3'): 'NoCC (CEXO)', ('NoCC', 'wO3'): 'NoCC + O3 (OZYEXO)',
       ('RCP26', 'woO3'): 'RCP2.6 (CEXO)', ('RCP26', 'wO3'): 'RCP2.6 + O3 (OZYEXO)',
       ('RCP70', 'woO3'): 'RCP7.0 (CEXO)', ('RCP70', 'wO3'): 'RCP7.0 + O3 (OZYEXO)'}
XL = 'Input: (1 + g)$^{30}$ from ClimateShifters2 [-]\n(2050 yield / 2020 yield)'
YL = 'Output: yldWat 2050 / yldWat 2020 [-]\n(2050 yield / 2020 yield)'
for c, d in df.groupby('c'):
    fig, ax = plt.subplots(figsize=(9 / 2.54, 8 / 2.54))
    for (cl, o3), col in COL.items():
        for wt, mk in [('Irrigation', 'o'), ('Rainfed', '^')]:
            s = d[(d.clim == cl) & (d.o3 == o3) & (d.wat == wt)]
            ax.scatter(s[USE], s.out, s=10, marker=mk, linewidths=0.6,
                       facecolors=col if wt == 'Irrigation' else 'none', edgecolors=col)
    lo = np.nanmin(d[[USE, 'out']].values); hi = np.nanmax(d[[USE, 'out']].values)
    pad = (hi - lo) * 0.05; lo, hi = lo - pad, hi + pad
    ax.plot([lo, hi], [lo, hi], color='black', lw=0.5, ls='--')
    off = d[d['diff'].abs() >= TOL].drop_duplicates(['CTY', 'wat', 'inp', 'out'])
    for _, r in off.iterrows():
        ax.annotate(f"{r.CTY} ({r.wat[0]})", (r[USE], r.out), fontsize=5.5,
                    xytext=(3, -3), textcoords='offset points')
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi); ax.set_aspect('equal')
    ax.text(0.03, 0.97, f'Item: {c} (model commodity)\nn = {len(d)} (CTY x scenario x technology)'
            + (f'\nOff the 1:1 line (|diff| >= {TOL:g}): {len(d[d["diff"].abs() >= TOL])}' if (d['diff'].abs() >= TOL).any() else ''),
            transform=ax.transAxes, va='top', fontsize=7)
    ax.set_xlabel(XL); ax.set_ylabel(YL)
    h = [ax.scatter([], [], s=10, color=col, label=LAB[k]) for k, col in COL.items()]
    h += [ax.scatter([], [], s=10, marker='o', facecolors='k', edgecolors='k', label='Irrigated (filled)'),
          ax.scatter([], [], s=10, marker='^', facecolors='none', edgecolors='k', label='Rainfed (open)'),
          ax.plot([], [], color='black', lw=0.5, ls='--', label='1:1 line')[0]]
    if len(off): h.append(ax.scatter([], [], s=0, label='Label: CTY (I = irrigated, R = rainfed)'))
    ax.legend(handles=h, loc='center left', bbox_to_anchor=(1.02, 0.5), frameon=False, fontsize=6.5)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, f'figC_yexo_io_cty_{c}.png'), dpi=600, bbox_inches='tight'); plt.close(fig)
print('figures ->', OUT)
