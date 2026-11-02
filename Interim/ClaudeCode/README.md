# Interim : 中間報告の図

中間報告（修正版 `others/rivised/中間報告_和崎敦貴_clean.docx`）の第5章の図と、それを作るデータ・プログラムをまとめたフォルダ。
元の場所は OneDrive の `藤森研/卒論/アウトプット/ch4/`。2026-11-02 に整理した。
このファイル内のパスはすべて `Interim/` からの相対パス。AI の利用申告は同じフォルダの `AI利用申告.md` を参照。

## 図とプログラムの対応

| 報告書の番号 | 内容 | output | prog |
|---|---|---|---|
| 図5.1 | 2050年の地域別・作物別の外生収量の変化 | `fig5-1_YEXO_region.png` | `fig5-1_YEXO_region.R` |
| 図5.2 | 2050年の世界合計の作物別生産量の変化（million kcal） | `fig5-2_PROD_kcal_world.png` | `fig5-2_PROD_kcal_world.R` |
| 図5.3 | 2050年の世界平均の作物別消費者価格指数の変化 | `fig5-3_XPRC_world.png` | `fig5-3_XPRC_world.R` |
| 初版の図5.3 | 2050年の世界平均の作物別生産者価格指数の変化（修正版で削除） | `first_fig5-3_XPRP_world.png` | `first_fig5-3_XPRP_world.R` |

- 4つの R ファイルは中身が同じ（元は `ch4/R/17_report.R` の1本）。どれを実行しても4枚すべてが `output/` に出る。
- 図3.1（フロー図）は `others/modelflow/`、表3.1 は Word の表で、このフォルダの対象外。
- 初版では消費者価格が図5.4、生産者価格が図5.3だった。修正版で生産者価格を外し、消費者価格を図5.3に繰り上げた。

## 処理の流れ

```
data/AGMIP_all_scenario.gdx（8/31版）
 ├─ prog/01_extract_level.py      → data/level.csv ほか（Xiadata.xlsx も読む）
 │   └─ prog/03_calc_effect.py    → data/level4.csv, effect.csv, scenario.csv
 └─ prog/02_extract_level_kcal.py → data/level_kcal.csv, level_kcal_2050.csv
     └─ prog/04_calc_effect_kcal.py → data/effect_kcal.csv
data/effect.csv + effect_kcal.csv
 └─ prog/fig5-*.R（00_common.R を読む） → output/*.png
```

## 実行方法

1. Python（GDX を更新したときだけ）：`pip install gamspy_base "gamsapi[transfer]" pandas xlsxwriter openpyxl` のあと、01→02→03→04 の順に実行する。どこから実行してもよい。
2. R：作業ディレクトリを `Interim/prog/` にして、`fig5-*.R` のどれか1つを `source()` する。必要なパッケージは tidyverse と scales。

## data の中身

| ファイル | 内容 | 作るプログラム |
|---|---|---|
| `AGMIP_all_scenario.gdx` | AIM-Alpha の出力（8/31版、中間報告で使用） | モデル |
| `all_scenario_World.gdx`, `all_scenario_global_17.gdx` | 同じ実行の別集計（第5章の図では未使用） | モデル |
| `Xiadata.xlsx` | Xia et al. (2026) の公開データ（01 が読むため置いてある。図では未使用） | ― |
| `level.csv` | 10シナリオの水準 | 01 |
| `concept.csv`, `region.csv`, `xia_prod.csv`, `xia_price.csv`, `ch4_data.xlsx` | 定義表・Xia比較用・Excel版 | 01 |
| `level4.csv`, `scenario.csv` | 中間報告の4シナリオの水準とシナリオ定義 | 03 |
| `effect.csv` | 4つの効果（2050年の差分） | 03 |
| `level_kcal.csv`, `level_kcal_2050.csv` | million kcal 単位の水準 | 02 |
| `effect_kcal.csv` | million kcal 単位の効果（PJ に換算済み） | 04 |

## シナリオと効果

| シナリオ | GDX のシナリオ名 |
|---|---|
| Baseline | SSP2_BaU_CS_NoCC_woO3 |
| RCP26 | SSP2_BaU_CS_RCP26_wO3 |
| RCP70 | SSP2_BaU_CS_RCP70_wO3 |
| RCP26_MITI | SSP2_500C_CS_RCP26_wO3 |

| 効果 | 差し引き |
|---|---|
| Climate change (SSP2-2.6) | RCP26 − Baseline |
| Mitigation (SSP2-2.6) | RCP26_MITI − RCP26 |
| Combined effect (SSP2-2.6) | RCP26_MITI − Baseline（上2つの和） |
| Climate change (SSP2-7.0) | RCP70 − Baseline |

## 確認したこと（2026-11-02）

- Interim の 01〜04 を 8/31 版 GDX で実行し、data の CSV 9つが元の `ch4/csv/` と一致することを確かめた。
- `level_kcal*.csv` は元の作成スクリプトが保存されていなかった。`02_extract_level_kcal.py` は作り直したもので、元の CSV と同じ値が出る。
- million kcal 単位のデータには日本（JPN）が無い（GDX にその行が無い）。図5.2 は世界合計なので影響しない。
- output の PNG は元の `ch4/fig/report/` からのコピーで、修正版 docx に貼られた画像と一致する。
