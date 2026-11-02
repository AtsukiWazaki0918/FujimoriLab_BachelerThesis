# OneTime/20261102

2026-11-02 の作業用フォルダ。中身は作成者が用意したもの。
このファイル内のパスはすべて `OneTime/20261102/` からの相対パス。

## アウトプットフォルダとの対応（2026-11-02 に確認）

- OneDrive `藤森研/卒論/アウトプット/` で 11/2 に更新されたファイルは次の2つで、どちらもこのフォルダの `define/` に同じ中身のファイルがある。重複を避けるため、新たにはコピーしていない。

| アウトプット内の名前 | このフォルダ内の名前 |
|---|---|
| `財の対応関係入力からモデルimpact_c.map` | `define/impact_c.map` |
| `財対応関係モデルからAgMIP_c.map` | `define/AgMIP_c.map` |

- 11/2 に作った図とプログラムは、アウトプットフォルダには無い。このため `output/` と `prog/` は空で、AI の利用申告も置いていない。

## 中身

| フォルダ | ファイル | 内容 |
|---|---|---|
| data | `AGMIP_all_scenario.gdx`, `all_scenario_global_17.gdx`, `all_scenario_World.gdx` | AIM-Alpha の出力（11/2 版）。Interim の 8/31 版、20261028 の 10/19 版とは別のファイル |
| data | `Xiadata.xlsx` | Xia et al. (2026) の公開データ |
| define | `AgMIP.set`, `AgMIP_var.set`, `AgMIP_c.map`, `AgMIP_src.map`, `impact_c.map`, `impact_cty.map`, `liv_c.map` | 品目・変数・地域の対応表 |
| define | `ClimateShifters2.gdx` | 収量入力データ |
| define | `ALPHA_doc/*.tex` | AIM-Alpha の説明文書 |
