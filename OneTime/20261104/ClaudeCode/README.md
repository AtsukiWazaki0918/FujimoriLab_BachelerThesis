# OneTime/20261104 : 外生収量の入出力の整合性確認（CTY × モデル品目 × 灌漑/天水）

2026-11-04 に、11/2 の散布図（17地域 × AgMIP 5作物）を、国（CTY）単位・モデル品目単位・灌漑と天水を分けた細かさで作り直したフォルダ。
このファイル内のパスはすべて `OneTime/20261104/` からの相対パス。AI の利用申告は同じフォルダの `AI利用申告.md` を参照。

## 図とプログラムの対応

| 内容 | output | prog |
|---|---|---|
| 外生収量の入力と出力の比較：2050年 ÷ 2020年の倍率（CTY × BaU の6シナリオ × 灌漑/天水）。モデル品目ごとに1枚 | `figC_yexo_io_cty_<品目>.png`（crl, frt, mze, nut, ocr, pls, rce, sgr, spc, stm, str, vgt, wht の13枚） | `figC_yexo_io_cty.py` |

- 1つのプログラムで13枚の図と表2つが出る。

## 比べる量

| 軸 | 内容 | 単位 |
|---|---|---|
| 横軸（入力） | (1 + g_c)^30。g_c は、モデル品目 c に対応する IMPACT 品目 j の年平均成長率 g（2020-2050）の単純平均 | 2050年の収量 ÷ 2020年の収量 [-] |
| 縦軸（出力） | `yldWat_load` の 2050年 ÷ 2020年 | 2050年の収量 ÷ 2020年の収量 [-] |

- 入力の g：オゾンなしは CEXO、オゾンありは OZYEXO（rcp2p6 は gfdl-esm4、rcp7p0 は ipsl-cm6a-lr、nocc は nocc の値）。
- NoCC＋オゾンありの g だけは、CEXO(nocc) ＋ {(OZYEXO − CEXO)(rcp2p6) ＋ (OZYEXO − CEXO)(rcp7p0)} ÷ 2 とした。ClimateShifters2 の OZYEXO(nocc) は CEXO(nocc) と同じ値で、オゾンの効果を含まないため。
- 灌漑は ClimateShifters2 の `air` と出力の `Irrigation`、天水は `arf` と `Rainfed` を対応させた。

## モデルの計算方法について確かめたこと（2026-11-04）

入力をどう作れば出力と一致するかを試し、次のことが分かった。

| 試した方法 | 結果 |
|---|---|
| j ごとに複利計算してから単純平均 | 複数の j が入る品目で一致しない（例：ocr で一致は5%） |
| j ごとに複利計算してから AREA で加重平均 | さらに一致しない |
| **g を単純平均してから複利計算** | **全品目・全組で一致（差は 1e-14 以下）** → 図に採用 |
| NoCC＋オゾンありを OZYEXO(nocc) のまま使う | 約8割の組で一致しない |
| **NoCC＋オゾンありを上の式で作る** | **全組で一致** → 図に採用 |

- 出力の倍率は、同じ国・品目・灌漑/天水なら全流域で同じだった。
- 出力では 2015年と 2020年の値が同じで、2020年から 30年かけて伸ばしている。

## 空間解像度（CTY）とモデルの国の対応

- ClimateShifters2 の CTY は 156 個。そのうち 18 個は複数国のまとまり（例：BLT＝バルト3国、BLX＝ベネルクス、CHM＝中国本土と台湾、CHP＝スイス）。
- モデルの国（ISO）は `iso2cty` で CTY に対応づけた。`iso2cty` に無い3つは CHN→CHM、HKG→CHM、ISL→ISL とした。HKG の値は CHN と同じだった。
- 複数国のまとまりの CTY（BLT, BLX, CRB, GSA, ITP, OBN, RAP）は、メンバー国の値がすべて同じだったので、その値を使った。
- 片方にしか無い組（入力だけ 6,798、出力だけ 1,146。例：エネルギー作物 ecr、SDN の pls）は図に入れていない。
- 1:1 線から 1e-4 以上ずれた点には名前を書く設定にしているが、該当する点は無かった。

## 処理の流れ

```
define/ClimateShifters2.gdx（入力：CEXO, OZYEXO, iso2cty）
define/impact_c.map（IMPACT j → モデル品目 c）
data/all_scenario_World.gdx（出力：yldWat_load）
 └─ prog/figC_yexo_io_cty.py → output/figC_yexo_io_cty_<品目>.png, data/yexo_io_cty.csv, data/yexo_io_cty_check.csv
```

## 実行方法

`pip install gamspy_base "gamsapi[transfer]" pandas numpy matplotlib` のあと `figC_yexo_io_cty.py` を実行する。どこから実行してもよい。

## data・define の中身

| フォルダ | ファイル | 内容 |
|---|---|---|
| data | `all_scenario_World.gdx` | AIM-Alpha の国別の出力。`OneTime/20261102/data/` のものと同じファイル |
| data | `yexo_io_cty.csv` | 図の数値（品目 × CTY × 灌漑/天水 × シナリオ。入力の g の平均、入力と出力の倍率、差） |
| data | `yexo_io_cty_check.csv` | 品目ごとの点の数、ずれた点の数、差の最大 |
| define | `ClimateShifters2.gdx`, `impact_c.map` | `OneTime/20261102/define/` からコピー。今回使った |
| define | `AgMIP_c.map` | `OneTime/20261102/define/` からコピー。今回は使っていない（出力の yldWat_load がモデル品目単位のため） |

- data・output は `.gitignore` で GitHub には上がらない。
