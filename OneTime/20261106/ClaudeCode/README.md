# OneTime/20261106 : Xia et al. (2026) と AIM-ALPHA の比較（生産量・価格、中間報告の4つの効果）

2026-11-06 に、Xia et al. (2026) のモデルと AIM-ALPHA について、中間報告の4つの効果（2050年）を比べる図を作ったフォルダ。
指標・シナリオ・作物・地域の対応と、計算方法を決めた経緯は `OneTime/20261105/ClaudeCode/README.md` にある。
カロリー摂取量の図は、Xia 側の FAO 補正の方法が不透明なため、今回は作っていない。
このファイル内のパスはすべて `OneTime/20261106/` からの相対パス。AI の利用申告は同じフォルダの `AI利用申告.md` を参照。

## 図とプログラムの対応

| 内容 | output | prog |
|---|---|---|
| 作物の生産量の変化（カロリーベース、PJ、6地域）。作物ごとに1枚 | `figXia_prod_<作物>.png`（WHT, RIC, CGR, OSD, SGC の5枚） | `figXia_prod.py` |
| 5作物の合計の生産量の変化（カロリーベース、PJ、6地域） | `figXia_prod_TOTAL.png` | `figXia_prod.py` |
| 作物全体（CRP。畜産・加工品を除く）の世界の生産者価格の変化 | `figXia_price_world.png` | `figXia_price.py` |

- `prog/common.py` は2つのプログラムが共通で使う定義（シナリオ・効果・地域・品目の対応、読み込み、欠損の注記、保存）。単独では実行しない。
- どの図も、灰色の棒は **AIM-ALPHA 以外のモデル（Xia et al. のモデル）の中央値**、記号は各モデルの値。図の凡例と注記にも書いた。

## 1. 中間報告の4つの効果

中間報告（`Interim/ClaudeCode/README.md`）の4つの効果を、Xia の効果（SI Table 1 の Climate・Mitigation・Ozone）を足し合わせて作った。中間報告ではオゾンの影響を気候の影響に含めるため、Ozone を Climate に足している。

| 効果 | Xia の効果の組み合わせ | シナリオの式（Xia の名前） |
|---|---|---|
| (1) 気候変動影響（SSP2-2.6） | RCP2.6 Climate ＋ RCP2.6 Ozone | OZBAU_MITI_RCP26 − BAU_MITI ＋ BAU − BAU_NoCC |
| (2) 緩和策影響（SSP2-2.6） | RCP2.6 Mitigation | BAU_MITI − BAU |
| (3) 総合影響（SSP2-2.6） | (1) ＋ (2) | OZBAU_MITI_RCP26 − BAU_NoCC |
| (4) 気候変動影響（SSP2-7.0） | RCP7.0 Climate ＋ RCP7.0 Ozone | OZBAU − BAU_NoCC |

- AIM-ALPHA も、対応するシナリオ（`common.py` の `SCEN_ALPHA`）で同じ式を使った。
- **中間報告の定義との違い：** 中間報告では、(1) を BaU_RCP26_wO3 − BaU_NoCC_woO3、(2) を 500C_RCP26_wO3 − BaU_RCP26_wO3 としていた。この定義を Xia 側で使うには「緩和なし・RCP2.6 の気候・オゾンあり（CH4 濃度もシナリオごと）」のシナリオが必要だが、各モデルの CSV では AIM-Hub にしか無い（`OZBAU_RCP26_W_CH4`）。そのため、全モデルで計算できる上の式を使った。
  - (3) と (4) は、中間報告の定義と同じになる。
  - (1) と (2) は、緩和策と気候の相互作用をどちらに含めるかが違う。AIM-ALPHA での差は、表の `*_interim_def` の列に残した。例：価格の (2) は、上の式で +2.0%、中間報告の定義で +1.6%。

## 2. 生産量の図（figXia_prod）

| 項目 | Xia et al. | AIM-ALPHA |
|---|---|---|
| 値の出どころ | `Xiadata.xlsx` のシート Crop prod change in 2050（PROD [1000 t]）。GLOBIOM だけは Excel が乾物重量なので、CSV の生重量（1000 t）から同じ式で計算した | `qs_load`（Domestic production [1000 t]）を国から6地域に足した |
| モデル | AIM-Hub, ENVISAGE, GCAM, GLOBIOM, IMPACT, MAGNET | — |
| 作物 | WHT, RIC, CGR, OSD, SGC | wht, rce, mze＋crl, ocr, sgr |
| 地域 | 6地域 | Xia SI Table 4 の国の割り当て（`define/xia_region_map.csv`）で集計 |

### カロリーベースへの換算式
```
E [PJ] = ΔPROD [1000 t] × 1000 [t / 1000 t] × f [kcal/t] × 4184 [J/kcal] × 10^-15 [PJ/J]
       = ΔPROD [1000 t] × f [kcal/t] × 4.184 × 10^-9

f [kcal/t] = Σ_国 cal_load [million kcal] ÷ Σ_国 qdFood_load [1000 t] × 1000
             （AIM-ALPHA、SSP2_BaU_CS_NoCC_woO3、2020年、世界。CGR は mze と crl をまとめる）
```

| 作物 | f [kcal/t] |
|---|---|
| WHT | 3,337,709 |
| RIC | 2,586,437 |
| CGR | 3,188,297 |
| OSD | 2,857,911 |
| SGC | 361,818 |

- 同じ f を全モデル・全地域に使うので、換算の違いによるモデル間の差は生じない。
- f は作物ごとに違う値である。CGR だけは、Xia の CGR がトウモロコシとその他穀物を分けていないので、mze と crl をまとめて1つの値にした。
- f は AIM-ALPHA の食料需要（人が食べる分）の値から作ったもので、国ごとの値を世界で合計した平均である。中間報告の図5.2（AGMIP_agg の million kcal）は国ごとの係数を使っているので、AIM-ALPHA の値はその図と少し違う。
- 合計（TOTAL）は、5作物の PJ を足したもの。
- 換算係数は `data/kcal_factor.csv` に保存した。

### 確認したこと
- GLOBIOM の CSV（乾物重量）から計算した Xia の効果は、5地域で Excel と一致した（差は 1e-11 以下）。RTW は一致しない（Xia の RTW の作り方が不明。11/4 と同じ）。図の GLOBIOM の RTW は WLD − 5地域で計算している。

## 3. 価格の図（figXia_price）

純粋な価格の変化を比べるため、Xia 側も AIM-ALPHA 側も、**重みを基準年の生産量に固定した方法（方法A）**で計算した。

- P(s, t) = Σ p(s, t) × Q0 ÷ Σ Q0
- Q0：基準シナリオ（BAU_NoCC）・基準年の生産量
- 値 = 1. の式で P(s, 2050) を組み合わせた効果 ÷ P(BAU_NoCC, 基準年) × 100 [%]

| 項目 | Xia et al. の各モデル | AIM-ALPHA |
|---|---|---|
| 値の出どころ | `data/モデル間比較用model_output/*.csv` の XPRP と PROD | `pp_load`（Producer price [USD/t]）と `qs_load` [1000 t] |
| 足し合わせる単位 | AgMIP の13地域 × 品目 | 国 × 品目 |
| 品目 | AIM-Hub：WHT, RIC, CGR, OSD, SGC, OCR（VFN は OCR に含まれる）／ENVISAGE, GLOBIOM, IMPACT：これに VFN を加えた7品目／GCAM：VFN の内訳（FRU, LEG, NUT, RTB, VEG）を使う | 作物13品目（`define/AgMIP_c.map` の CRP） |
| 基準年 | 2020年（ENVISAGE は CSV に 2020年が無いので 2021年） | 2020年 |
| モデル | AIM-Hub, ENVISAGE, GCAM, GLOBIOM, IMPACT（MAGNET は CSV が無いので図に無い） | — |

- 13地域 × 品目の生産量の合計は、どのモデルも WLD の生産量と一致した（`data/xia_price_weights_info.csv`）。
- ENVISAGE の価格は品目ごとの指数（2014 = 1）なので、まとめた値は指数の生産量加重平均になる。
- **畜産と加工品を除いた（作成者の指示）。** 除いた品目：畜産（RUM, NRM, DRY）、エネルギー作物（ECP）、繊維作物（PFB）、その他（OAP, OFD）。AgMIP の品目はどれも一次産品で、植物油や砂糖などの加工品は品目として入っていない。AIM-ALPHA 側も、加工品（vol, swt など）とエネルギー作物（ecr）を含まない作物13品目にした。
- Xia の Excel には AGR（作物＋畜産）の価格しか無いので、作物だけの値は CSV から計算した。Excel とは比べられない。
- **品目の範囲の確認：** 選んだ品目を、その時の生産量で重み付けして平均した値（`method_B_own`）を、CSV の XPRP CRP WLD（`method_B_csv`）と比べた。
  - AIM-Hub：全件一致。品目の範囲が CRP と同じことを確認した。
  - IMPACT：差は 0.1 ポイント以内。CRP に入っている繊維作物などを除いた分の差。
  - GLOBIOM：差は 1.6 ポイント以内。
  - ENVISAGE：価格が指数のため、差が出る（0.6 ポイント以内）。
  - GCAM：CSV に CRP の価格が無いので比べられない。CRP の生産量には、エネルギー作物と繊維作物が入っている。

## 4. 図の注釈に書いた欠損

- **データ無し**：Xia SI Table 4 の国のうち、AIM-ALPHA の国リスト（`cty`）にはあるが、`qs_load`・`pp_load` に値が無い国（60か国・地域）。地域ごとに書いた。
  - SEA：BRN, PRK, SGP, TWN
  - OAS：BTN, COK, FSM, KIR, MDV, MHL, NCL, NIU, NRU, PLW, PYF, TKL, TON, TUV, WSM
  - SSA：CPV, ERI, GNQ, MUS, REU, SOM, SYC
  - RTW：ABW, AIA, AND, ANT, BHR, BMU, CUB, CYM, DMA, ESH, FLK, GGY, GIB, GLP, GRL, GUF, IMN, JEY, KNA, LIE, MCO, MSR, PRI, PSE, QAT, SJM, SMR, SYR, TCA, VAT, VEN, VGB, VIR, YEM
- **区分無し**：AIM-ALPHA の国リストにあるが、Xia SI Table 4 に無いコード（76, ALA, ASM, SSD など）。どれもデータが無いので結果に影響しない。
- Xia SI Table 4 の国で、AIM-ALPHA の国リストに無いものは無かった。

## 処理の流れ

```
data/Xiadata.xlsx（Crop prod change in 2050）
data/モデル間比較用model_output/GLOBIOM.csv
data/all_scenario_World.gdx（qs_load, cal_load, qdFood_load）
define/xia_region_map.csv
 └─ prog/figXia_prod.py → output/figXia_prod_<作物>.png, figXia_prod_TOTAL.png, data/xia_prod_compare.csv, data/kcal_factor.csv

data/モデル間比較用model_output/*.csv（XPRP, PROD）
data/all_scenario_World.gdx（pp_load, qs_load）
 └─ prog/figXia_price.py → output/figXia_price_world.png, data/xia_price_compare.csv, data/xia_price_weights_info.csv
```

## 実行方法

`pip install gamspy_base "gamsapi[transfer]" pandas numpy matplotlib openpyxl` のあと、`figXia_prod.py` と `figXia_price.py` を実行する。どこから実行してもよい。

## data・define の中身

| フォルダ | ファイル | 内容 |
|---|---|---|
| data | `Xiadata.xlsx`, `all_scenario_World.gdx` | `OneTime/20261105/data/` と同じファイル |
| data | `モデル間比較用model_output/` | 各モデルの AgMIP 形式の出力。`OneTime/20261104/data/` と同じファイル |
| data | `xia_prod_compare.csv` | 生産量の図の数値（モデル × 地域 × 作物 × 効果）。d_1000t [1000 t]、PJ、AIM-ALPHA の中間報告の定義での値 |
| data | `kcal_factor.csv` | カロリー換算係数 f [kcal/t] |
| data | `xia_price_compare.csv` | 価格の図の数値（method_A）と照合用の値（method_B_csv, method_B_own）、AIM-ALPHA の中間報告の定義での値 [-] |
| data | `xia_price_weights_info.csv` | 価格の計算に使った品目、地域×品目の組の数、WLD の生産量に対する割合 |
| define | `xia_region_map.csv` | Xia SI Table 4 の国 → 地域（SI の PDF から作成。223か国・地域） |
| define | `AgMIP_c.map` | AIM-ALPHA の品目 → AgMIP の品目。`OneTime/20261102/define/` からコピー |
| define | `agec12086-sup-0001-appendix.xlsx` | von Lampe et al. (2014) の補足（作成者が置いた）。Fig.1–9 の図のデータで、品目の定義表（Table SI-4）は入っていなかった |
| doc | `43016_2026_1322_MOESM1_ESM.pdf` | Xia et al. (2026) の SI。`OneTime/20261105/doc/` と同じファイル |

- data・output は `.gitignore` で GitHub には上がらない。doc の PDF と define の appendix の xlsx は、出版物のファイルなので GitHub に上げていない。
- `output/_t2.png` は、作業中に書き込みの確認で作った空のファイル（削除の権限が無いため残っている）。不要なので削除してよい。
