# OneTime/20261102 : 外生収量の入出力の整合性確認（11/2 版の出力と map による作物対応）

2026-11-02 に、10/28 の散布図（`OneTime/20261028/` の figA・figB）を、11/2 版の AIM-Alpha 出力と作物の対応表（map）で作り直したフォルダ。
このファイル内のパスはすべて `OneTime/20261102/` からの相対パス。AI の利用申告は同じフォルダの `AI利用申告.md` を参照。

## 図とプログラムの対応

| 内容 | output | prog |
|---|---|---|
| 外生収量の入力と出力の比較：2020→2050 年の年平均成長率（17地域 × 5作物 × 12シナリオ） | `figA_yexo_io_growth.png` | `figA_yexo_io_growth.py` |
| 外生収量の入力と出力の比較：2050 年の NoCC からの変化率 | `figB_yexo_io_change.png` | `figB_yexo_io_change.py` |

- `figA_*.py` と `figB_*.py` は中身が同じ。どちらを実行しても図2枚と表（`data/yexo_io_check.csv`・`.xlsx`）が出る。
- 10/28 の CRP のモデル間比較（figMC）は作っていない。他の5モデルの出力がこのフォルダに無いため。

## 10/28 版からの変更点

| 項目 | 10/28 | 11/2 |
|---|---|---|
| 出力の YEXO | `level.csv`（8/31 版 GDX から作成） | `data/AGMIP_all_scenario.gdx`（11/2 版）から直接読む |
| 作物の対応 | プログラム内に手で書いた対応（J2I） | `define/impact_c.map`（IMPACT j → モデル品目）と `define/AgMIP_c.map`（モデル品目 → AgMIP 品目）を組み合わせる |
| シナリオ数 | 10 | 12（`SSP2_500C_CS_RCP70_wO3`・`_woO3` が増えた） |

- 比べ方、集計の重み（AREA tot）、国から17地域への対応、作図は 10/28 と同じ。
- map に変えたことで、油糧作物（OSD）に `jcott`（綿）と `jplol` が新たに入った。入力側で値が変わったのは OSD だけである。
- `AgMIP_c.map` では小麦が `WHT`、GDX の出力では `wht` なので、プログラム内で `wht` にそろえている。

## 処理の流れの図（draw.io、2026-11-06 に追加）

`doc/flow_figA_figB_yexo_io.drawio`：figA・figB ができるまでの全ステップを、入力側（ClimateShifters2 から直接）と出力側（AIM-ALPHA の出力）の2本の流れで示した。各ステップ（単位換算か集計を1回）の後の単位・品目・地域と、使った式・対応表のファイルを書いた。draw.io（diagrams.net）で開いて編集できる。

| 対応表のファイル（2026-11-06 に追加） | 内容 |
|---|---|
| `define/j2agmip5.csv` | IMPACT の品目 j → モデルの品目 c → AgMIP の5作物（impact_c.map と AgMIP_c.map を組み合わせた結果。22行） |
| `define/cty2reg_input.csv` | 入力の CTY → AIM-ALPHA の17地域（iso2cty と cty_reg_map から作った対応と、プログラムで指定した7つ。157行） |

- 2つのファイルは、プログラム（figA・figB）の中で作っている対応表を、確認のために書き出したもの。プログラムは変えていない。

## 処理の流れ

```
define/ClimateShifters2.gdx（入力：CEXO, OZYEXO, AREA, iso2cty）
define/impact_c.map, define/AgMIP_c.map（作物の対応）
data/all_scenario_global_17.gdx（国→17地域の対応表 cty_reg_map だけを使う）
data/AGMIP_all_scenario.gdx（出力：AGMIP_agg の YEXO, fm t/ha）
 └─ prog/figA・figB → output/figA・figB, data/yexo_io_check.csv・.xlsx
```

## 実行方法

`pip install gamspy_base "gamsapi[transfer]" pandas numpy matplotlib openpyxl` のあと、`figA_*.py` か `figB_*.py` のどちらかを実行する。どこから実行してもよい。

## data・define の中身

| フォルダ | ファイル | 内容 |
|---|---|---|
| data | `AGMIP_all_scenario.gdx`, `all_scenario_global_17.gdx`, `all_scenario_World.gdx` | AIM-Alpha の出力（11/2 版）。Interim の 8/31 版、20261028 の 10/19 版とは別のファイル。`all_scenario_World.gdx` は今回使っていない |
| data | `Xiadata.xlsx` | Xia et al. (2026) の公開データ。今回は使っていない |
| data | `yexo_io_check.csv`, `.xlsx` | 散布図の数値と、作物 × 気候 × オゾン × 緩和策ごとの相関・傾き・差の統計（figA・figB が作る） |
| define | `AgMIP.set`, `AgMIP_var.set`, `AgMIP_src.map`, `impact_cty.map`, `liv_c.map` | 品目・変数・地域の対応表。今回は使っていない |
| define | `impact_c.map`, `AgMIP_c.map` | 作物の対応表。今回使った。OneDrive `藤森研/卒論/アウトプット/` の `財の対応関係入力からモデルimpact_c.map`・`財対応関係モデルからAgMIP_c.map` と同じ中身 |
| define | `ClimateShifters2.gdx` | 収量入力データ |
| define | `ALPHA_doc/*.tex` | AIM-Alpha の説明文書 |

## 確認したこと（2026-11-02）

- 入力側の地域・作物で対応がとれなかったものは無かった。ただしコメ（RIC）は CAN に入力も出力も無いため 16 地域になっている（10/28 と同じ）。
- 10/28 の表と比べ、入力側の値が変わったのは OSD だけ（map の変更による）。出力側の YEXO はほぼすべての行で変わった（GDX の版の違いによる）。
- data・output は `.gitignore` で GitHub には上がらない。
