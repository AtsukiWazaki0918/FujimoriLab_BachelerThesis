# OneTime/20261105 : Xia et al. (2026) と AIM-Alpha の比較の方針決め

2026-11-05 に、Xia et al. (2026) の公開データ（`data/Xiadata.xlsx`）と AIM-Alpha の出力（`data/all_scenario_World.gdx`）を比べる図の方針を決めたフォルダ。
この日は図を作っていないので、prog と output は空である。図は `OneTime/20261106/` で作った。
AI の利用申告は同じフォルダの `AI利用申告.md` を参照。

## フォルダの中身

| フォルダ | ファイル | 内容 |
|---|---|---|
| data | `Xiadata.xlsx` | Xia et al. (2026) の公開データ。`OneTime/20261104/data/` のものと同じファイル |
| data | `all_scenario_World.gdx` | AIM-Alpha の国別の出力。`OneTime/20261104/data/` のものと同じファイル |
| doc | `43016_2026_1322_MOESM1_ESM.pdf` | Xia et al. (2026) の Supplementary Information（作成者が置いた） |

## 1. Xia et al. (2026) とデータの概要（本文と SI で確認したこと）

- 論文：Xia et al., *Nature Food* 7, 356–368 (2026)。6つの農業経済モデル（AIM-Hub, ENVISAGE, GCAM, GLOBIOM, IMPACT, MAGNET）で、気候変動・緩和策・オゾン濃度変化が食料安全保障に与える影響を比べている。Excel の「AIM」は AIM-Hub であり、AIM-Alpha ではない。
- 社会経済シナリオは SSP2（感度分析だけ SSP1 も）。

### シナリオ（本文 Table 1）と効果（SI Table 1）

| シナリオ | 緩和 / 気候 / オゾン |
|---|---|
| BAU_NoCC | なし / NoCC / 変化なし |
| BAU | なし / RCP7.0 / 変化なし |
| OZBAU | なし / RCP7.0 / RCP7.0 |
| BAU_MITI | RCP2.6 / RCP7.0 / 変化なし（SI の注記：SSP2-7.0 の設定に 1.5℃ 目標の緩和策を入れたもの） |
| BAU_MITI_RCP26 | RCP2.6 / RCP2.6 / 変化なし |
| OZBAU_MITI_RCP26 | RCP2.6 / RCP2.6 / RCP2.6 |

| 効果 | 式 |
|---|---|
| RCP7.0 Climate | BAU − BAU_NoCC |
| RCP7.0 Ozone | OZBAU − BAU |
| RCP2.6 Mitigation | BAU_MITI − BAU |
| RCP2.6 Climate | (BAU_MITI_RCP26 − BAU_MITI) ＋ (BAU − BAU_NoCC) |
| RCP2.6 Ozone | OZBAU_MITI_RCP26 − BAU_MITI_RCP26 |
| Combined | 上の効果の和 |

- 各モデルの CSV では、OZBAU 系の主な結果は `_W_CH4` 付きのシナリオ（GLOBIOM は付かない、ENVISAGE は小文字の `_w_CH4`）。
- 感度分析の高汚染シナリオは LoAQ の排出を使ったもの（SI Fig. 15）。CSV には入っていない。

### 収量の入力
- 気候：GGCMI Phase 3 の4作物（トウモロコシ・コメ・小麦・大豆）。IMPACT の37品目に割り当てた（参考文献77：SPAM2010）。
- オゾン：GEOS-Chem（2°×2.5°）の AOT40 と、5作物の曝露反応関数（SI Table 2。RYL = 係数 × AOT40。コメ 0.00415、トウモロコシ 0.00356、小麦 0.0163、油糧 0.0113、糖料 0.0150）。
- グリッドの値を将来の土地利用で重み付けして17地域に集計し、全モデルに入れた。ベースラインの収量は IMPACT の推計。
- 緩和策が外生収量に影響するのは IMPACT だけ（土地の伸び率の違いによる水のショック）。

### Excel のシート
| シート | 指標・単位 | 地域 |
|---|---|---|
| Crop prod change in 2050 | PROD [1000 t]（GLOBIOM は 1000 t dm）、CALO [kcal/人/日]。5作物（WHT, RIC, CGR, OSD, SGC）。Combined なし | 6地域（China, India, South-East Asia, Other Asia, Sub-Saharan Africa, Rest of the world） |
| Price change in 2050 | XPRP（AGR）の変化 ÷ BAU_NoCC の2020年の値 [-] | 世界 |
| Calorie intake change in 2050 | CALO_fao の変化 [kcal/人/日] | 世界 |
| その他 | Baseline（RoH, CALO_fao, XPRPindex, Population）、地域別の飢餓、感度分析 | 18地域など |

- 6地域は AgMIP の地域を SSA, CHN, IND, SEA, OAS とそれ以外（RTW）にまとめたもの（SI Table 3）。日本と台湾は SEA。国の割り当ては SI Table 4。

## 2. 比べる指標と AIM-Alpha の変数の対応（決定事項）

| Xia の指標 | AIM-Alpha の変数 | 処理 |
|---|---|---|
| Crop prod change：PROD | `qs_load` [1000 t] | 5作物にまとめ、6地域に足す |
| Crop prod change：CALO | `calPc_load` [kcal/人/年] | 365 で割り、5作物にまとめ、人口加重で6地域の平均 |
| Price change | `pp_load`（Producer price）[USD/t] | AGR と世界にまとめ、指数にする |
| Calorie intake change | `foodCal_load` [kcal/人/日] | 人口（`pop_load`）加重で世界平均 |

- Xia の price は生産者価格（XPRP）である。根拠：CSV の XPRP AGR と一致した（AIM, IMPACT）、本文に「agricultural commodity producer prices」とある。

### シナリオの対応
| Xia | AIM-Alpha |
|---|---|
| BAU_NoCC | `SSP2_BaU_CS_NoCC_woO3` |
| BAU | `SSP2_BaU_CS_RCP70_woO3` |
| OZBAU | `SSP2_BaU_CS_RCP70_wO3` |
| BAU_MITI | `SSP2_500C_CS_RCP70_woO3` |
| BAU_MITI_RCP26 | `SSP2_500C_CS_RCP26_woO3` |
| OZBAU_MITI_RCP26 | `SSP2_500C_CS_RCP26_wO3` |

- AIM-Alpha の `500C` と AIM-Hub の炭素予算 500 GtCO2 は同じ設定（作成者が確認）。
- AIM-Alpha の wO3 は、Xia の `_W_CH4` と同じオゾンのデータとして扱う（作成者の判断）。

### 作物の対応（`define/AgMIP_c.map`）
| Xia | AIM-Alpha：生産量 | AIM-Alpha：カロリー |
|---|---|---|
| WHT | wht | wht |
| RIC | rce | rce |
| CGR | mze＋crl | mze＋crl |
| OSD | ocr | **ocr＋vol（植物油）** |
| SGC | sgr | **sgr＋swt（甘味料）** |
| AGR（価格） | 作物13品目＋畜産6品目 | — |

- カロリーで vol と swt を足す根拠：各モデルの CSV の CALO（世界、BAU_NoCC、2020年）は OSD が 253–428 kcal、SGC が 166–247 kcal。AIM-Alpha の ocr だけでは 59 kcal、sgr だけでは 4.5 kcal で、vol と swt を足すと 351 kcal と 245 kcal になる。GLOBIOM だけは OSD が 44 kcal で、加工品を含まないとみられる（SGC は値なし）。品目の定義の文書（von Lampe et al. 2014 の Table SI-4）は手元に無い。

### 地域の対応
- Xia SI Table 4 の国の割り当てに合わせる（MNG は AIM-Alpha では SEA だが OAS に移す）。
- AIM-Alpha にデータが無い国は、図の注釈にすべて書く。「データ無し」と「区分無し」を分けて書く。

### 単位と時点
- AIM-Alpha は 2015–2050 の5年おき（基準年 2015）。Xia は 2020–2050。どちらも 2020 と 2050 がある。

## 3. 計算方法の決定事項

### 価格のまとめ方
- 方法A（重みを固定）：P(s,t) = Σ p(s,t) × Q0 ÷ Σ Q0。Q0 は基準シナリオ・基準年の生産量。
- 方法B（その時の生産量で重み付け）：P(s,t) = Σ p(s,t) × Q(s,t) ÷ Σ Q(s,t)。
- 各モデルの CSV の XPRP AGR WLD は方法B で作られていた（AIM-Hub, IMPACT, GLOBIOM は一致、ENVISAGE は 1–2% ずれ）。
- **決定：** 純粋な価格の変化を比べるため、Xia 側も AIM-Alpha 側も方法A で計算する（作成者の指示）。

### カロリーの FAO 補正
- Xia の補正：CALO_fao(t) = FAO(2020) × CALO_モデル(t) ÷ CALO_モデル(2020)。FAO の値は6モデル共通（世界 2,957.4 kcal）。
- 11/4 の照合で、1か国の地域（BRA, CAN, IND, USA）だけ一致した。複数国の地域と世界は再現できなかった（補正の単位が細かいためとみられる）。世界の変化量に FAO(世界)/モデル(世界) を掛けると差は約1%。
- Crop prod の CALO は FAO の補正をしていない値で一致した。
- **決定：** Xia 側の計算方法が不透明なため、カロリーの図はいったん作らない。生産量と価格の図を先に作る（作成者の指示、2026-11-06）。

## 4. 確認できていないこと
- 4作物から IMPACT の37品目への割り当ての方法（ESSD の SPAM2010 の論文の本文には書かれていない）。
- IMPACT で灌漑と天水の割合が変わるか。
- 各モデルの実際の計算の刻み（AIM-Hub は1年刻み。CSV の年は、AIM 5年おき、ENVISAGE 2014/2018/2021/5年おき、GCAM 5年おき、GLOBIOM 10年おき、IMPACT 毎年）。
