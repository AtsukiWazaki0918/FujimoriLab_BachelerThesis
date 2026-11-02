# OneTime/20261028 : 外生収量の入出力の整合性確認と、CRP のモデル間比較

2026-10-28 に作った2種類の図（外生収量の入力と出力の散布図2枚、作物合計 CRP のモデル間比較4枚）と、それを作るデータ・プログラムをまとめたフォルダ。
元の場所は OneDrive の `藤森研/卒論/アウトプット/`（`yexo_check/` と `ch4/` のうち 10/28 更新のファイル）。2026-11-02 に整理した。
このファイル内のパスはすべて `OneTime/20261028/` からの相対パス。AI の利用申告は同じフォルダの `AI利用申告.md` を参照。

## 図とプログラムの対応

| 内容 | output | prog |
|---|---|---|
| 外生収量の入力と出力の比較：2020→2050 年の年平均成長率（17地域 × 5作物 × 10シナリオ） | `figA_yexo_io_growth.png` | `figA_yexo_io_growth.py` |
| 外生収量の入力と出力の比較：2050 年の NoCC からの変化率 | `figB_yexo_io_change.png` | `figB_yexo_io_change.py` |
| CRP の生産量・消費量・生産者価格のモデル間比較（World） | `figMC_world.png` | `figMC_world.py` |
| CRP の生産量のモデル間比較（AgMIP 17地域） | `figMC_PROD_region.png` | `figMC_PROD_region.py` |
| CRP の消費量（CONS）のモデル間比較（AgMIP 17地域） | `figMC_CONS_region.png` | `figMC_CONS_region.py` |
| CRP の生産者価格（XPRP）のモデル間比較（AgMIP 17地域） | `figMC_XPRP_region.png` | `figMC_XPRP_region.py` |

- `figA_*.py` と `figB_*.py` は中身が同じ（元は `アウトプット/yexo_check/yexo_scatter.py`）。どちらを実行しても図2枚と表が出る。
- `figMC_*.py` の4つは中身が同じ（元は `アウトプット/ch4/model_compare_crp.py`）。どれを実行しても図4枚と表が出る。
- `figMC_*` の図には、指標・品目・単位を示す文字が図の中に入っている（研究室の書式では図内タイトルなし）。元の図のまま残している。

## 処理の流れ

```
define/ClimateShifters2.gdx（入力の外生収量）
data/all_scenario_global_17.gdx（国→17地域の対応表 cty_reg_map だけを使う）
data/level.csv（出力の YEXO。8/31 版 AGMIP_all_scenario.gdx から Interim の 01_extract_level.py が作ったもの）
 └─ prog/figA・figB → output/figA・figB, data/yexo_io_check.csv・.xlsx

data/AGMIP_all_scenario.gdx（10/19 版、AIM-Alpha）
data/モデル間比較用model_output/{AIM,ENVISAGE,GCAM,GLOBIOM,IMPACT}.csv
 └─ prog/figMC_* → output/figMC_*, data/model_compare_crp.csv
```

- 2つの作業で使う AIM-Alpha の出力の版が違う。散布図は 8/31 版（`level.csv`）、モデル間比較は 10/19 版の GDX を使っている。元の作業のとおりにしている。

## 実行方法

`pip install gamspy_base "gamsapi[transfer]" pandas numpy matplotlib openpyxl` のあと、`figA_*.py`（または `figB_*.py`）と `figMC_*.py` のどれか1つずつを実行する。どこから実行してもよい。

## data・define の中身

| ファイル | 内容 | 作るもの |
|---|---|---|
| `define/ClimateShifters2.gdx` | 収量入力データ（元の名前は `収量入力ClimateShifters2.gdx`）。`Interim/define/` と同じファイル | 研究室で用意 |
| `data/AGMIP_all_scenario.gdx` | AIM-Alpha の出力（10/19 版）。`Interim/data/` の 8/31 版とは別のファイル | モデル |
| `data/all_scenario_global_17.gdx` | AIM-Alpha の出力（10/19 版）。散布図では国→地域の対応表だけを使う | モデル |
| `data/level.csv` | 10シナリオの水準（8/31 版 GDX から作成）。`Interim/data/level.csv` と同じファイル | Interim の 01 |
| `data/モデル間比較用model_output/*.csv` | 他の5モデルの出力（10/7 にダウンロード）。ALPHA.csv は使っていないので入れていない | ― |
| `data/yexo_io_check.csv`, `.xlsx` | 散布図の数値と、作物 × シナリオごとの相関・傾き・差の統計 | figA・figB |
| `data/model_compare_crp.csv` | モデル間比較の数値（シナリオ値・差・% 変化） | figMC |

## 確認したこと（2026-11-02）

- 新しい場所でプログラムを実行し、`yexo_io_check.csv` と `model_compare_crp.csv` が元と同じ値になることを確かめた。
- `figMC_*` の図4枚は元の PNG とバイト単位で同じだった。`figA`・`figB` は元の図と見比べて同じ図になることを確かめた。output には元の PNG をコピーしている。
- data・output は `.gitignore` で GitHub には上がらない。
