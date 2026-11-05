# OneTime/20261106 : Xia et al. (2026) と AIM-Alpha の比較（生産量・価格）

2026-11-06 に、Xia et al. (2026) の6モデルと AIM-Alpha について、2050年の効果（気候・緩和・オゾン）を比べる図を作ったフォルダ。
指標・シナリオ・作物・地域の対応と、計算方法を決めた経緯は `OneTime/20261105/ClaudeCode/README.md` にある。
カロリーの図は、Xia 側の FAO 補正の方法が不透明なため、今回は作っていない。
このファイル内のパスはすべて `OneTime/20261106/` からの相対パス。AI の利用申告は同じフォルダの `AI利用申告.md` を参照。

## 図とプログラムの対応

| 内容 | output | prog |
|---|---|---|
| 作物の生産量の変化（2050年、効果別、6地域）。作物ごとに1枚 | `figXia_prod_<作物>.png`（WHT, RIC, CGR, OSD, SGC の5枚） | `figXia_prod.py` |
| 農産物全体（AGR）の世界の生産者価格の変化（2050年、効果別） | `figXia_price_world.png` | `figXia_price.py` |

- `prog/common.py` は2つのプログラムが共通で使う定義（シナリオ・効果・地域・品目の対応、読み込み、欠損の注記）。単独では実行しない。

## 1. 生産量の図（figXia_prod）

| 項目 | Xia et al. | AIM-Alpha |
|---|---|---|
| 値の出どころ | `Xiadata.xlsx` のシート Crop prod change in 2050（Variable = PROD）をそのまま使う | `qs_load`（Domestic production [1000 t]）を国から6地域に足し、効果を計算する |
| 作物 | WHT, RIC, CGR, OSD, SGC | wht, rce, mze＋crl, ocr, sgr |
| 効果 | RCP7.0：Climate, Ozone／RCP2.6：Climate, Mitigation, Ozone（Excel に Combined は無い） | 同じ式（SI Table 1） |
| 地域 | 6地域 | Xia SI Table 4 の国の割り当て（`define/xia_region_map.csv`）で集計 |
| 単位 | 1000 t（GLOBIOM は 1000 t dm）。図では百万 t で表示 | 1000 t。図では百万 t で表示 |

## 2. 価格の図（figXia_price）

純粋な価格の変化を比べるため、Xia 側も AIM-Alpha 側も、**重みを基準年の生産量に固定した方法（方法A）**で計算した。Xia の Excel の値は使っていない（Excel の値はその時の生産量で重み付けした方法B）。

- P(s, t) = Σ p(s, t) × Q0 ÷ Σ Q0
- Q0：基準シナリオ（BAU_NoCC）・基準年の生産量
- 値 = SI Table 1 の式で P(s, 2050) を組み合わせた効果 ÷ P(BAU_NoCC, 基準年) × 100 [%]

| 項目 | Xia et al. の各モデル | AIM-Alpha |
|---|---|---|
| 値の出どころ | `data/モデル間比較用model_output/*.csv` の XPRP と PROD | `pp_load`（Producer price [USD/t]）と `qs_load` [1000 t] |
| 足し合わせる単位 | AgMIP の13地域 × 品目 | 国 × 品目 |
| 品目 | AIM-Hub：WHT, RIC, CGR, OSD, SGC, OCR, RUM, NRM, DRY（VFN は OCR に含まれる）／ENVISAGE, GLOBIOM, IMPACT：これに VFN を加えた10品目／GCAM：VFN の内訳（FRU, LEG, NUT, RTB, VEG）を使う | 作物13品目＋畜産6品目（`define/AgMIP_c.map` の AGR） |
| 基準年 | 2020年（ENVISAGE は 2021年。CSV に 2020年が無いため） | 2020年 |
| 対象モデル | AIM-Hub, ENVISAGE, GCAM, GLOBIOM, IMPACT（MAGNET は CSV が無いので図に無い） | — |

- 13地域 × 品目の生産量の合計は、どのモデルも WLD の生産量と一致した（`data/xia_price_weights_info.csv` の share_of_WLD_PROD = 1.0）。
- ENVISAGE の価格は品目ごとの指数（2014 = 1）なので、まとめた値は USD/t の平均ではなく、指数の生産量加重平均になる。
- GLOBIOM の重みには生重量（1000 t）を使った。
- GCAM は CSV に AGR の価格が無いが、品目ごとの価格から方法A で計算できた。

### 計算が正しいことの確認
同じプログラムで方法B（CSV の XPRP AGR WLD）の値も計算し、Excel の値と比べた（`data/xia_price_compare.csv`）。

| モデル | 方法B と Excel の差 |
|---|---|
| AIM-Hub, IMPACT | 全7効果で一致 |
| GLOBIOM | 0.15 ポイント以内 |
| ENVISAGE | 0.17 ポイント以内 |

## 3. 図の注釈に書いた欠損

- **データ無し**：Xia SI Table 4 の国のうち、AIM-Alpha の国リスト（`cty`）にはあるが、`qs_load`・`pp_load` に値が無い国（60か国・地域）。地域ごとに書いた。
  - SEA：BRN, PRK, SGP, TWN
  - OAS：BTN, COK, FSM, KIR, MDV, MHL, NCL, NIU, NRU, PLW, PYF, TKL, TON, TUV, WSM
  - SSA：CPV, ERI, GNQ, MUS, REU, SOM, SYC
  - RTW：ABW, AIA, AND, ANT, BHR, BMU, CUB, CYM, DMA, ESH, FLK, GGY, GIB, GLP, GRL, GUF, IMN, JEY, KNA, LIE, MCO, MSR, PRI, PSE, QAT, SJM, SMR, SYR, TCA, VAT, VEN, VGB, VIR, YEM
- **区分無し**：AIM-Alpha の国リストにあるが、Xia SI Table 4 に無いコード（76, ALA, ASM, SSD など）。どれもデータが無いので結果に影響しない。
- Xia SI Table 4 の国で、AIM-Alpha の国リストに無いものは無かった。
- データがある国でも、ある作物の値が無い組は、生産が0とみなした。

## 処理の流れ

```
data/Xiadata.xlsx（Crop prod change in 2050）
data/all_scenario_World.gdx（qs_load）
define/xia_region_map.csv, define/AgMIP_c.map
 └─ prog/figXia_prod.py → output/figXia_prod_<作物>.png, data/xia_prod_compare.csv

data/モデル間比較用model_output/*.csv（XPRP, PROD）
data/all_scenario_World.gdx（pp_load, qs_load）
data/Xiadata.xlsx（Price change in 2050。照合用）
 └─ prog/figXia_price.py → output/figXia_price_world.png, data/xia_price_compare.csv, data/xia_price_weights_info.csv
```

## 実行方法

`pip install gamspy_base "gamsapi[transfer]" pandas numpy matplotlib openpyxl` のあと、`figXia_prod.py` と `figXia_price.py` を実行する。どこから実行してもよい。

## data・define の中身

| フォルダ | ファイル | 内容 |
|---|---|---|
| data | `Xiadata.xlsx`, `all_scenario_World.gdx` | `OneTime/20261105/data/` と同じファイル |
| data | `モデル間比較用model_output/` | 各モデルの AgMIP 形式の出力。`OneTime/20261104/data/` と同じファイル |
| data | `xia_prod_compare.csv` | 生産量の図の数値（モデル × 地域 × 作物 × 効果）[1000 t] |
| data | `xia_price_compare.csv` | 価格の図の数値（method_A）と照合用の値（method_B_csv, xia_excel）[-] |
| data | `xia_price_weights_info.csv` | 価格の計算に使った品目、地域×品目の組の数、WLD の生産量に対する割合 |
| define | `xia_region_map.csv` | Xia SI Table 4 の国 → 地域（SI の PDF から作成。223か国・地域） |
| define | `AgMIP_c.map` | AIM-Alpha の品目 → AgMIP の品目。`OneTime/20261102/define/` からコピー |
| define | `agec12086-sup-0001-appendix.xlsx` | von Lampe et al. (2014) の補足（作成者が置いた）。Fig.1–9 の図のデータで、品目の定義表（Table SI-4）は入っていなかった |
| doc | `43016_2026_1322_MOESM1_ESM.pdf` | Xia et al. (2026) の SI。`OneTime/20261105/doc/` と同じファイル |

- data・output は `.gitignore` で GitHub には上がらない。doc の PDF と define の appendix の xlsx は、出版物のファイルなので GitHub に上げていない。
