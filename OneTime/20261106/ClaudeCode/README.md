# OneTime/20261106 : AgMIP の各モデルの出力（CSV）と AIM-ALPHA の比較（卒論の4つの効果）

2026-11-06 に、AgMIP 形式の5モデルの出力（CSV）と AIM-ALPHA について、卒論（中間報告）の4つの効果（2050年）を比べる図を作ったフォルダ。
Xia et al. (2026) の Excel（`Xiadata.xlsx`）は使っていない。Excel を使って作った最初の版は `others/excel_version/` に移した（経緯は下の「版の履歴」）。
このファイル内のパスはすべて `OneTime/20261106/` からの相対パス。AI の利用申告は同じフォルダの `AI利用申告.md` を参照。

## 図とプログラムの対応

| 内容 | output | prog |
|---|---|---|
| 世界の効果。パネルは CRP と5作物（WHT, RIC, CGR, OSD, SGC） | `figCSV_<VAR>_world.png`（VAR = PROD, CONS, XPRP の3枚） | `figCSV_compare.py` |
| AgMIP 17地域の効果。品目ごとに1枚 | `figCSV_<VAR>_<ITEM>_region.png`（VAR 3つ × ITEM = CRP, WHT, RIC, CGR, OSD, SGC の18枚） | `figCSV_compare.py` |

- 1つのプログラムで21枚の図と表3つが出る。実行時間は約1分。
- どの図も、灰色の棒は **AIM-ALPHA 以外の5モデルの中央値**、記号は各モデルの値。EUR・MEN・AME では GCAM も中央値から外した（下の 5.）。

## 1. 比べるモデルとデータ

| | 内容 |
|---|---|
| 他のモデル | AIM-Hub（CSV の「AIM」）, ENVISAGE, GCAM, GLOBIOM, IMPACT。`data/モデル間比較用model_output/*.csv`（10/7 にダウンロードしたもの。`OneTime/20261028/data/` と同じファイル） |
| AIM-ALPHA | `data/all_scenario_World.gdx`（国別の出力） |
| MAGNET | CSV が無いので入っていない |

## 2. 卒論の4つの効果とシナリオ

| 効果 | 式 |
|---|---|
| (1) 気候変動影響（SSP2-2.6） | RCP26 − Baseline |
| (2) 緩和策影響（SSP2-2.6） | RCP26_MITI − RCP26 |
| (3) 総合影響（SSP2-2.6） | RCP26_MITI − Baseline |
| (4) 気候変動影響（SSP2-7.0） | RCP70 − Baseline |

| 卒論のシナリオ | 他のモデル（CSV） | AIM-ALPHA |
|---|---|---|
| Baseline | BAU_NoCC | SSP2_BaU_CS_NoCC_woO3 |
| RCP26 | OZBAU_RCP26 | SSP2_BaU_CS_RCP26_wO3 |
| RCP26_MITI | OZBAU_MITI_RCP26_W_CH4 | SSP2_500C_CS_RCP26_wO3 |
| RCP70 | OZBAU_W_CH4 | SSP2_BaU_CS_RCP70_wO3 |

- オゾンの影響は気候の影響に含める（卒論の設計）。
- **`_W_CH4`**：オゾン濃度を、シナリオごとの CH4（メタン）濃度で計算したもの（Xia et al. 本文 Methods）。Xia の主な結果はこちら。
  - **AIM-ALPHA の wO3 は CH4 濃度を変えていると判断して**、RCP26_MITI と RCP70 は `_W_CH4` を使った（作成者の判断。確認中）。
  - RCP26（緩和なし・RCP2.6）の `_W_CH4` は AIM-Hub にしか無いので、全モデルで CH4 なしの OZBAU_RCP26 を使った。RCP2.6 では CH4 の有無による差は小さい（作物全体の世界の生産量へのオゾン効果で 0.02–0.17 ポイント）。
  - GLOBIOM には `_W_CH4` が無いので、すべて CH4 なし。ENVISAGE は小文字の `_w_CH4`。
  - 作成者の確認の結果、AIM-ALPHA が CH4 濃度を変えていなかった場合は作り直す。

## 3. 指標

### 生産量（PROD）と消費量（CONS）：カロリーベース [PJ]
```
E [PJ] = Q [1000 t] × f [kcal/t] × 1000 [t / 1000 t] × 4184 [J/kcal] × 10^-15 [PJ/J]

f [kcal/t] = Σ cal_load [million kcal] ÷ Σ qdFood_load [1000 t] × 1000
   （AIM-ALPHA、SSP2_BaU_CS_NoCC_woO3、2020年、世界。cal_load と qdFood_load の両方に値がある国×品目の組で合計）
```

| AgMIP の品目 | AIM-ALPHA の品目 | f [kcal/t] |
|---|---|---|
| WHT | wht | 3,337,709 |
| RIC | rce | 2,586,437 |
| CGR | mze, crl | 3,188,297 |
| OSD | ocr | 2,857,911 |
| SGC | sgr | 361,818 |
| VFN | str, pls, nut, vgt, frt | 613,293 |
| OCR | stm, spc | 1,340,465 |
| AIM-Hub の OCR（VFN を含む） | str, pls, nut, vgt, frt, stm, spc | 626,094 |

- 同じ品目には、全モデル・全地域で同じ f を使う。換算の違いによるモデル間の差は生じない。
- Q：他のモデルは CSV の PROD・CONS（GLOBIOM は生重量）、AIM-ALPHA は `qs_load`（生産量）・`qd_load`（国内需要の合計）。
- CONS は国内利用の合計（食料・飼料・その他）。
- 換算係数は `data/kcal_factor.csv` に保存した。

### 生産者価格（XPRP）：価格指数の効果 [%]
```
値 = (P_対象シナリオ,2050 − P_参照シナリオ,2050) ÷ P_Baseline,2020 × 100
```
- 作物別・地域別の価格は、各モデルの CSV の XPRP をそのまま使う。
- CRP の価格は、作物別の価格を、**同じシナリオ・同じ年の生産量（重量、t）**で重み付けして平均する（Xia・AgMIP の CSV と同じ重み付け）。
- AIM-ALPHA は、国 × 品目の `pp_load` を、同じシナリオ・同じ年の `qs_load` で重み付けして、品目・地域にまとめる。
- ENVISAGE の価格は品目ごとの指数（2014 = 1）で、CSV に2020年が無いので、基準年は2021年。
- 確認：自分で作った CRP の価格を CSV の XPRP CRP（世界、Baseline、基準年）と比べた。AIM-Hub は一致した（0.498345 と 0.498342）。IMPACT は、CRP に含まれる繊維作物などを除いた分だけ違う。

## 4. 作物と地域

- **CRP**：WHT＋RIC＋CGR＋OSD＋SGC＋VFN＋OCR。一次産品の作物だけで、畜産・加工品・エネルギー作物（ECP）・繊維作物（PFB）・その他（OAP, OFD）は含まない。AIM-Hub には VFN が無い（OCR に含まれる）。GCAM の VFN の価格は内訳（FRU, LEG, NUT, RTB, VEG）から作る。AIM-ALPHA は作物13品目（`define/AgMIP_c.map` の CRP）。
- **作物別**：WHT, RIC, CGR, OSD, SGC。
- **地域**：世界と AgMIP の17地域（CAN, USA, BRA, OSA, FSU, EUR, MEN, SSA, CHN, IND, SEA, OAS, ANZ, NAM, OAM, AME, SAS）。AIM-ALPHA は `cty_reg_map` で国を集計した。
- 生産の無い組（例：カナダのコメ）は、価格の値が無いので描かれない。

## 5. 図の注釈に書いたこと（欠損と地域の定義）

- **† AIM-ALPHA で計算されていない国**：人口などが2015年までしか無く、生産量・消費量・価格の値が無い国。AIM-ALPHA の地域の合計から抜けている。他の5モデルの地域の人口は、これらの国を含めた人口とほぼ同じで、欠けているのは AIM-ALPHA だけである。地域の人口（2015年）に占める割合は次のとおり（`data/missing_cty.csv`）。

| 地域 | 割合 | 国 |
|---|---|---|
| OSA | 11.0% | CUB, PRI, VEN と小さな地域2つ、人口データの無い7つ（BMU, CYM, DMA, GRL, KNA, TCA, VGB） |
| MEN | 9.3% | SYR, YEM、人口データの無い PSE |
| SEA | 3.7% | PRK, SGP |
| SSA | 3.1% | CPV, ERI, GNQ, MUS, SOM, SSD と小さな地域1つ、人口データの無い F206 |
| OAS | 0.5% | 小さな地域9つ、人口データの無い6つ |
| EUR, FSU | 0.0% | 人口データの無い小さな国のみ |
| 世界 | 2.1% | — |

  - 集計地域（OAM, AME, SAS）は、メンバーの地域の欠損を含む。17地域の図では、該当する地域のパネルのタイトルに † を付けた。
  - BHR, QAT, BTN は、計算されているが農地と生産が無い国なので、欠損として扱っていない。作物ごとの値が無い組も、生産が無いとみなした。
- **台湾**：AIM-ALPHA に台湾の値は無い。台湾の生産は CHN に含まれる（IMPACT の地域 CHM = 中国本土＋台湾。`impact_cty.map` で CHM → CHN）。この点は作成者が確認中で、違った場合は作り直す。
- **GCAM のトルコ**：GCAM の EUR と MEN の人口の差がトルコの人口とほぼ同じ（2015年：EUR +71、MEN −79、トルコ 78 百万人。2050年：+89、−95、96）なので、GCAM ではトルコが MEN ではなく EUR に入っていると判断した。CSV からトルコの分を取り出して直すことはできないので、EUR・MEN・AME のパネルでは GCAM を中央値の計算から外し、そのことを注釈に書いた。
- 地域の定義はモデルによって少し違う可能性がある、と注釈に1行書いた。

## 処理の流れ

```
data/モデル間比較用model_output/*.csv（PROD, CONS, XPRP）
data/all_scenario_World.gdx（qs_load, qd_load, pp_load, cal_load, qdFood_load, pop_load, cty_reg_map）
 └─ prog/figCSV_compare.py → output/figCSV_*.png（21枚）, data/csv_compare.csv, data/kcal_factor.csv, data/missing_cty.csv
```

## 実行方法

`pip install gamspy_base "gamsapi[transfer]" pandas numpy matplotlib` のあと、`figCSV_compare.py` を実行する。どこから実行してもよい。

## 確認したこと

- 次の値を、プログラムとは別のコードで計算し直し、一致を確かめた：
  - IMPACT の世界の WHT の生産量の (2)
  - GLOBIOM の SSA の RIC の価格の (4)
  - AIM-Hub の世界の CRP の消費量の (3)
  - AIM-ALPHA の SEA の OSD の生産量の (1)
  - AIM-ALPHA の世界の CRP の価格の (2)
- EUR の中央値が GCAM を除いて計算されていることを確かめた。
- 生産量・消費量で (1)＋(2)＝(3) が成り立つことを確かめた（差は 1e-12 以下）。
- 図を目で見て、注釈やラベルが切れたり重なったりしていないことを確かめた。

## data・define・others の中身

| フォルダ | ファイル | 内容 |
|---|---|---|
| data | `all_scenario_World.gdx` | AIM-ALPHA の出力。`OneTime/20261105/data/` と同じファイル |
| data | `モデル間比較用model_output/` | 5モデルの AgMIP 形式の出力 |
| data | `csv_compare.csv` | 図の数値（Model, VAR, ITEM, Region, effect, value）。単位は PROD・CONS が PJ、XPRP が % |
| data | `kcal_factor.csv` | カロリー換算係数 f |
| data | `missing_cty.csv` | AIM-ALPHA で計算されていない国と、地域の人口に占める割合（2015年） |
| data | `Xiadata.xlsx` | 今回は使っていない（Excel 版で使用） |
| define | `AgMIP_c.map` | AIM-ALPHA の品目 → AgMIP の品目 |
| define | `xia_region_map.csv` | Xia SI Table 4 の国 → 地域。今回は使っていない（Excel 版で使用） |
| define | `agec12086-sup-0001-appendix.xlsx` | von Lampe et al. (2014) の補足。品目の定義表は入っていなかった |
| doc | `43016_2026_1322_MOESM1_ESM.pdf` | Xia et al. (2026) の SI |
| others | `excel_version/` | Excel を使った最初の版のプログラム・図・表 |

- data・output は `.gitignore` で GitHub には上がらない。doc の PDF と define の appendix の xlsx は、出版物のファイルなので GitHub に上げていない。

## 版の履歴（2026-11-06）

1. Xia の Excel の値を使い、Xia の効果（Climate・Mitigation・Ozone）別に、生産量（重量）と農産物全体（AGR）の価格の図を作った。
2. 卒論の4つの効果（Xia の効果の組み合わせ）、カロリーベース、中央値の棒に変えた。価格を作物だけ（CRP）にし、表記を AIM-ALPHA にそろえた。
3. Excel の解像度と指標の制約を外すため、Excel をやめて CSV だけで作り直した（この版）。17地域、消費量、作物別の価格を追加し、卒論の定義どおりのシナリオの差で4つの効果を計算した。1. と 2. のプログラム・図・表は `others/excel_version/` にある（2. の版）。
