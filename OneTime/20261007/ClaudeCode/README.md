# OneTime/20261007 : 外生収量の入力データ（ClimateShifters2）の地図

2026-10-07 に作った、収量入力データ `ClimateShifters2.gdx` の OZYEXO（land = tot）の地図4枚と、それを作るデータ・プログラムをまとめたフォルダ。
元の場所は OneDrive の `藤森研/卒論/アウトプット/`（10/7 更新のファイル）。2026-11-02 に整理した。
このファイル内のパスはすべて `OneTime/20261007/` からの相対パス。AI の利用申告は同じフォルダの `AI利用申告.md` を参照。

## 図とプログラムの対応

| 内容 | output | prog |
|---|---|---|
| 米・RCP7.0（IPSL-CM6A-LR）の 2050 年の外生収量の NoCC からの変化率 | `map_OZYEXO_rice_rcp7p0.png` | `map_OZYEXO_rice_rcp7p0.py` |
| 米・RCP2.6（GFDL-ESM4）の同上 | `map_OZYEXO_rice_rcp2p6.png` | `map_OZYEXO_rice_rcp2p6.py` |
| 小麦・RCP7.0 の同上 | `map_OZYEXO_wheat_rcp7p0.png` | `map_OZYEXO_wheat_rcp7p0.py` |
| 小麦・RCP2.6 の同上 | `map_OZYEXO_wheat_rcp2p6.png` | `map_OZYEXO_wheat_rcp2p6.py` |

- 4つの `map_*.py` は中身が同じ（元は `アウトプット/map.py` の1本）。どれを実行しても4枚すべてが `output/` に出る。
- 元のファイル名は `map_rice_rcp7p0.png` など。何の値の地図かが分かるように `OZYEXO` を付けた。
- 図の中にタイトルが入っている（研究室の書式では図内タイトルなし）。元の図のまま残している。

## 処理の流れ

```
define/ClimateShifters2.gdx（OZYEXO, iso2cty）
 └─ prog/01_calc_OZYEXO_change.py → data/ozyexo_tot_rice_wheat.csv
     └─ prog/map_OZYEXO_*.py（+ data/ne_50m_admin_0_countries.geojson）→ output/map_OZYEXO_*.png
```

- 変化率 = ((1 + g_RCP) / (1 + g_NoCC))^30 − 1（%）。g は OZYEXO の 2020→2050 年の年平均成長率。
- OZYEXO は IMPACT の収量トレンドに気候変動とオゾン濃度変化の影響を加えた値。NoCC との比をとるので、収量トレンドの寄与はおおむね打ち消される。

## 実行方法

`pip install gamspy_base "gamsapi[transfer]" pandas geopandas matplotlib` のあと、`01_calc_OZYEXO_change.py` → `map_OZYEXO_*.py`（どれか1つ）の順に実行する。どこから実行してもよい。

## data・define の中身

| ファイル | 内容 | 作るもの |
|---|---|---|
| `define/ClimateShifters2.gdx` | 収量入力データ（元の名前は `収量入力ClimateShifters2.gdx`、10/5 更新）。`Interim/define/` のものと同じファイル | 研究室で用意 |
| `data/ozyexo_tot_rice_wheat.csv` | 米・小麦の OZYEXO（tot）と変化率 | 01 |
| `data/ne_50m_admin_0_countries.geojson` | Natural Earth の国境データ（1:50m）。元のフォルダには無かったので、10/7 と同じ入手先（GitHub `nvkelso/natural-earth-vector`）から取り直した | ― |

## 確認したこと（2026-11-02）

- 新しい場所で 01 を実行し、`ozyexo_tot_rice_wheat.csv` が元の CSV と同じ値になることを確かめた。
- `map_*.py` を実行し、元の図と見比べて同じ地図になることを確かめた（フォントだけが異なる）。output には元の PNG を名前を変えてコピーしている。
- data・output は `.gitignore` で GitHub には上がらない。
