# TeamMeeting/20261109 : 11/9 個別ゼミ資料の素材（README・AI 利用申告）

11/9 の個別ゼミ資料のために、OneTime/20261104（外生収量のチェック図）と OneTime/20261106（モデル間比較図の完成版）のファイルをコピーしたフォルダ。コピーしたファイルはすべてコピー元と同じことを確かめた。各図の詳しい説明はコピー元の `ClaudeCode/README.md` を参照。

## 中身

| 内容 | output | prog | data | define | コピー元 |
|---|---|---|---|---|---|
| 外生収量の入力と出力の比較（国 × モデル品目 × 灌漑/天水、2050年 ÷ 2020年） | `figC_yexo_io_cty_<品目>.png`（13枚） | `figC_yexo_io_cty.py` | `all_scenario_World.gdx`, `yexo_io_cty.csv`, `yexo_io_cty_check.csv` | `ClimateShifters2.gdx`, `impact_c.map` | 20261104 |
| AgMIP の各モデルと AIM-ALPHA の比較（卒論の4つの効果、2050年） | `figCSV_*.png`（21枚） | `figCSV_compare.py` | `all_scenario_World.gdx`, `モデル間比較用model_output/`, `csv_compare.csv`, `kcal_factor.csv`, `missing_cty.csv` | `AgMIP_c.map`, `cty_reg_map_AgMIP17.csv`, `kcal_factor.csv` | 20261106 |

- doc：`flow_figC_yexo_io_cty.drawio`（figC の処理の流れの図、2026-11-06 に作成）、`flow_figCSV_compare.drawio`（figCSV の処理の流れの図）、`43016_2026_1322_MOESM1_ESM.pdf`（Xia et al. (2026) の SI）。
- プログラムはこのフォルダでもそのまま実行できる書き方になっている（実行はしていない）。

## AI 利用申告

- **ツール**：Claude（Anthropic）。claude.ai 上で作成者の PC のフォルダにつないで作業した。設定上のモデルは claude-opus-5-5（実際に応答したモデルは異なる可能性がある）。
- **図・プログラムの作成**：figC は 2026-11-04（流れの図は 2026-11-06）、figCSV と流れの図は 2026-11-06 に、AI がプログラムを書き、作成者が手順・比較方法・シナリオ・指標を指示・決定した。詳細はコピー元の `ClaudeCode/AI利用申告.md`。
- **このフォルダの作成（2026-11-06）**：作成者の指示で AI がファイルをコピーした。コピー先とコピーする範囲は AI が決め、コピー元と同じことを AI が確かめた。あわせて、draw.io の自動バックアップと `__pycache__` を削除し、`.gitignore` に追記した。
- **本人による確認**：作成者が確認する。最終的な内容と判断の責任は作成者が負う。
- **保存先**：GitHub https://github.com/AtsukiWazaki0918/FujimoriLab_BachelerThesis.git の `TeamMeeting/20261109/`（data・output は `.gitignore` で除外。ローカルの `C:\FujimoriLab_BachelerThesis\TeamMeeting\20261109\` にある）。
