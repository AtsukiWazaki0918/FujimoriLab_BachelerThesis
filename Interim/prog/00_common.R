# =============================================================================
# 00_common.R : 共通設定（すべての図スクリプトの冒頭で source する）
#   シナリオは 4 本。オゾンは明示的に扱わず、気候条件の一部として扱う。
#
#     Baseline    SSP2_BaU_CS_NoCC_woO3    緩和策なし・気候変化なし
#     RCP26       SSP2_BaU_CS_RCP26_wO3    緩和策なし・RCP2.6 の気候
#     RCP70       SSP2_BaU_CS_RCP70_wO3    緩和策なし・RCP7.0 の気候
#     RCP26_MITI  SSP2_500C_CS_RCP26_wO3   緩和策あり・RCP2.6 の気候
#
#   差分は 4 つ。SSP2-2.6 側は (1) + (2) = (3) が厳密に成立する。
#     (1) Climate change  (SSP2-2.6) = RCP26      - Baseline
#     (2) Mitigation      (SSP2-2.6) = RCP26_MITI - RCP26
#     (3) Combined effect (SSP2-2.6) = RCP26_MITI - Baseline
#     (4) Climate change  (SSP2-7.0) = RCP70      - Baseline
#
#   図は藤森研の規定に合わせる。枠なし・背景白・図内タイトルなし・軸に名前と単位・
#   図中の文字は本文と同じ Times 系フォント。図番号とタイトルと説明は Word 側に置く。
# =============================================================================
for (p in c("readr","dplyr","tidyr","tibble","stringr","purrr","ggplot2","scales"))
  suppressPackageStartupMessages(library(p, character.only = TRUE))

# --- パス -------------------------------------------------------------------
# 作業ディレクトリを Interim/prog/ にして実行する。数値は ../data、図は ../output。
CSV    <- "../data"
FIGDIR <- "../output"
if (!file.exists(file.path(CSV, "effect.csv")))
  stop("../data/effect.csv が見つかりません。作業ディレクトリを Interim/prog/ にしてください。")
dir.create(FIGDIR, showWarnings = FALSE, recursive = TRUE)

level  <- read_csv(file.path(CSV, "level4.csv"), show_col_types = FALSE)
effect <- read_csv(file.path(CSV, "effect.csv"), show_col_types = FALSE)

# カロリーベース（PJ）の差分。作物や品目をまたいで足し合わせる図はこちらを使う。
# VAR は "PROD_kcal" のように _kcal を付けて区別する。
.p_kcal <- file.path(CSV, "effect_kcal.csv")
if (file.exists(.p_kcal)) {
  effect <- bind_rows(effect,
    read_csv(.p_kcal, show_col_types = FALSE) %>% mutate(VAR = paste0(VAR, "_kcal")))
  message("カロリーベースの差分を読み込みました（単位 PJ）")
}

# --- 図の共通設定 -----------------------------------------------------------
YEAR      <- 2050
PANEL_COL <- 6            # 17 地域を 6 列 × 3 行に並べる（右下が欠ける）
FREE_Y    <- TRUE         # 地域ごとに縦軸を自由にする

# 出力サイズはすべて cm の実寸。本文幅 16 cm にそのまま貼れる大きさで作るので、
# R で指定したポイント数が Word 上のポイント数と一致する。
FIG_W     <- 16           # 地域別の図の幅（cm）
FIG_H     <- 12           # 地域別の図の高さ（cm）
FIG_W_WIDE <- 16
FIG_W_ONE  <- 14          # 世界計の図（1 パネル）の幅（cm）
FIG_H_ONE  <- 9           # 世界計の図の高さ（cm）
FIG_W_ONE_WIDE <- 14

# --- フォント（本文と同じ Times 系。Windows では Times New Roman が選ばれる）---
pick_font <- function() {
  cand <- c("Times New Roman", "TeX Gyre Termes", "Liberation Serif",
            "Nimbus Roman", "DejaVu Serif", "serif")
  fams <- tryCatch(unique(systemfonts::system_fonts()$family), error = function(e) NULL)
  if (is.null(fams)) return("serif")
  hit <- cand[cand %in% fams]
  if (length(hit)) hit[1] else "serif"
}
FONT <- pick_font()
message("使用フォント: ", FONT)

# --- 17 地域 ----------------------------------------------------------------
R17 <- c("CHN","IND","JPN","XSE","XSA","XOC","USA","CAN","XE25","XER","TUR",
         "CIS","BRA","XLM","XME","XNF","XAF")
R17_LAB <- c(CHN="China", IND="India", JPN="Japan", XSE="SE Asia", XSA="Other Asia",
             XOC="Oceania", USA="USA", CAN="Canada", XE25="EU", XER="Rest of EU",
             TUR="Turkey", CIS="Former USSR", BRA="Brazil", XLM="Rest of LAM",
             XME="Middle East", XNF="North Africa", XAF="Sub-Saharan\nAfrica")

# --- 4 つの個別効果 ---------------------------------------------------------
EFF_CC26 <- "Climate change (SSP2-2.6)"
EFF_MI26 <- "Mitigation (SSP2-2.6)"
EFF_CB26 <- "Combined effect (SSP2-2.6)"
EFF_CC70 <- "Climate change (SSP2-7.0)"
EFF4 <- c(EFF_CC26, EFF_MI26, EFF_CB26, EFF_CC70)
# 軸ラベルは 2 行に折って高さを抑える
EFF4_SHORT <- c("Climate change\n(SSP2-2.6)", "Mitigation\n(SSP2-2.6)",
                "Combined effect\n(SSP2-2.6)", "Climate change\n(SSP2-7.0)")
names(EFF4_SHORT) <- EFF4

# --- 配色 -------------------------------------------------------------------
COL_EFF  <- setNames(c("#4C9F70", "#C0504D", "#808080", "#E8A33D"), EFF4)
COL_CROP <- c("Wheat"="#4E79A7", "Rice"="#59A14F", "Coarse grains"="#F28E2B",
              "Oilseeds"="#B07AA1", "Sugar crops"="#E15759")
COL_CALI <- c(COL_CROP, "Other crops"="#9C755F", "Livestock"="#76B7B2")
COL_USE  <- c("Food"="#4E79A7", "Feed"="#F28E2B", "Other use"="#9C755F")
COL_EMIS <- c("Agriculture / CH4"="#E15759", "Agriculture / N2O"="#F1A7A6",
              "Land use / CO2"="#2F5C8A",   "Land use / CH4"="#6B9BD1",
              "Land use / N2O"="#B7CDE8")
COL_LAND <- c("Cropland (excl. energy crops)"="#E8B04B", "Energy crops"="#8C6D1F",
              "Grassland"="#9BC08A", "Forest"="#2E7D4F", "Other natural land"="#B9AE9B")

# --- テーマ（藤森研の規定準拠）----------------------------------------------
theme_ch4 <- function(base_size = 8, x_angle = 0) {
  theme_bw(base_size = base_size, base_family = FONT) +
    theme(panel.border     = element_blank(),
          panel.background = element_blank(),
          plot.background  = element_blank(),
          panel.grid       = element_blank(),
          axis.line        = element_line(colour = "black", linewidth = 0.3),
          axis.ticks       = element_line(colour = "black", linewidth = 0.3),
          strip.background = element_blank(),
          strip.text       = element_text(size = base_size, colour = "black"),
          axis.text        = element_text(colour = "black", size = base_size - 1),
          axis.title       = element_text(colour = "black", size = base_size),
          legend.position  = "bottom",
          legend.text      = element_text(size = base_size),
          legend.key.size  = unit(base_size * 1.2, "pt"),
          legend.margin    = margin(t = 0, b = 0),
          plot.margin      = margin(2, 4, 2, 2)) +
    (if (x_angle != 0)
       theme(axis.text.x = element_text(colour = "black", size = base_size - 1,
                                        angle = x_angle, hjust = 1, vjust = 0.5))
     else theme())
}

# --- 差分の取り出し ---------------------------------------------------------
#   regions を "World" にすれば世界計。既定は 17 地域。
get_eff <- function(var, items = NULL, value_col = "diff",
                    regions = R17, region_labels = R17_LAB, factors = EFF4) {
  d <- effect %>% filter(VAR %in% var, Y == YEAR, region %in% regions, Factor %in% factors)
  if (!is.null(items)) d <- d %>% filter(ITEM %in% items)
  labs <- if (is.null(region_labels)) regions else unname(region_labels[regions])
  d %>% mutate(region = factor(region, levels = regions, labels = labs),
               Factor = factor(Factor, levels = factors),
               eff    = factor(unname(EFF4_SHORT[as.character(Factor)]),
                               levels = unname(EFF4_SHORT[factors])),
               value  = .data[[value_col]])
}
get_eff_world <- function(var, items = NULL, value_col = "diff", factors = EFF4) {
  get_eff(var, items, value_col, regions = "World", region_labels = NULL, factors = factors)
}

# =============================================================================
# 図A : 横軸 = 4 効果、積み上げ = 品目（品目を足せる指標）
# =============================================================================
fig_by_effect <- function(d, fill_lab, palette, title = NULL, ylab, net = TRUE,
                          ncol = PANEL_COL, caption = NULL) {
  base <- if (ncol == 1) 10 else 8
  tot <- d %>% group_by(region, eff) %>%
    summarise(value = sum(value, na.rm = TRUE), .groups = "drop")
  p <- ggplot(d, aes(eff, value, fill = .data[[fill_lab]])) +
    geom_col(data = ~ dplyr::filter(.x, value >= 0), width = 0.7) +
    geom_col(data = ~ dplyr::filter(.x, value <  0), width = 0.7) +
    geom_hline(yintercept = 0, linewidth = 0.3, colour = "black") +
    scale_x_discrete(limits = levels(d$eff), drop = FALSE) +
    scale_fill_manual(values = palette, limits = levels(d[[fill_lab]]), drop = FALSE) +
    labs(x = NULL, y = ylab, fill = NULL, shape = NULL) +
    theme_ch4(base, x_angle = if (ncol == 1) 0 else 90) +
    guides(fill = guide_legend(order = 1, nrow = if (ncol == 1) 2 else 1))
  if (ncol > 1)
    p <- p + facet_wrap(~ region, ncol = ncol, drop = FALSE,
                        scales = if (FREE_Y) "free_y" else "fixed")
  # 黒い菱形は積み上げた品目の合計（正味）。凡例に出して説明なしでも読めるようにする。
  if (net) p <- p +
    geom_point(data = tot, aes(eff, value, shape = "Total"), inherit.aes = FALSE,
               size = base / 7, colour = "black") +
    scale_shape_manual(values = c("Total" = 18)) +
    guides(shape = guide_legend(order = 2, override.aes = list(size = base / 6)))
  p
}

# =============================================================================
# 図B : 横軸 = 5 作物、各作物に 2 本（作物をまたいで足せない指標）
#   左 = (4) Climate change (SSP2-7.0) 単独
#   右 = (1) Climate change (SSP2-2.6) + (2) Mitigation (SSP2-2.6) の積み上げ
#        その合計（黒い菱形）が (3) Combined effect (SSP2-2.6) に等しい
#   ggplot は積み上げと並置を同時にできないので x 座標を手で ±0.21 ずらす。
# =============================================================================
fig_by_crop <- function(d, title = NULL, ylab, crop_levels, crop_labels,
                        ncol = PANEL_COL, caption = NULL) {
  base <- if (ncol == 1) 10 else 8
  d <- d %>%
    filter(Factor %in% c(EFF_CC70, EFF_CC26, EFF_MI26)) %>%
    mutate(Factor = factor(as.character(Factor), levels = c(EFF_CC70, EFF_CC26, EFF_MI26)),
           xi = as.integer(factor(ITEM, levels = crop_levels)),
           xn = xi + ifelse(Factor == EFF_CC70, -0.21, 0.21))
  tot <- d %>% filter(Factor != EFF_CC70) %>% group_by(region, xn) %>%
    summarise(value = sum(value, na.rm = TRUE), .groups = "drop")
  p <- ggplot(d, aes(xn, value, fill = Factor)) +
    geom_col(data = ~ dplyr::filter(.x, value >= 0), width = 0.38) +
    geom_col(data = ~ dplyr::filter(.x, value <  0), width = 0.38) +
    geom_point(data = tot, aes(xn, value, shape = EFF_CB26), inherit.aes = FALSE,
               size = base / 7, colour = "black") +
    geom_hline(yintercept = 0, linewidth = 0.3, colour = "black") +
    scale_x_continuous(breaks = seq_along(crop_levels), labels = crop_labels,
                       expand = expansion(add = 0.45)) +
    scale_y_continuous(expand = expansion(mult = 0.08)) +
    scale_fill_manual(values = COL_EFF, limits = levels(d$Factor), drop = FALSE) +
    scale_shape_manual(values = setNames(18, EFF_CB26)) +
    labs(x = NULL, y = ylab, fill = NULL, shape = NULL) +
    theme_ch4(base, x_angle = if (ncol == 1) 0 else 90) +
    guides(fill  = guide_legend(order = 1, nrow = 2),
           shape = guide_legend(order = 2, override.aes = list(size = base / 6)))
  if (ncol > 1)
    p <- p + facet_wrap(~ region, ncol = ncol, drop = FALSE,
                        scales = if (FREE_Y) "free_y" else "fixed")
  p
}

# =============================================================================
# 図C : 横軸 = 5 作物、各作物に 2 本（気候変動影響のみ）
#   左 = (1) Climate change (SSP2-2.6)、右 = (4) Climate change (SSP2-7.0)
#   外生収量のように緩和策がほとんど効かない指標に使う。
# =============================================================================
fig_climate_only <- function(d, ylab, crop_levels, crop_labels, ncol = PANEL_COL) {
  base <- if (ncol == 1) 10 else 8
  d <- d %>%
    filter(Factor %in% c(EFF_CC26, EFF_CC70)) %>%
    mutate(Factor = factor(as.character(Factor), levels = c(EFF_CC26, EFF_CC70)),
           xi = as.integer(factor(ITEM, levels = crop_levels)),
           xn = xi + ifelse(Factor == EFF_CC26, -0.21, 0.21))
  p <- ggplot(d, aes(xn, value, fill = Factor)) +
    geom_col(width = 0.38) +
    geom_hline(yintercept = 0, linewidth = 0.3, colour = "black") +
    scale_x_continuous(breaks = seq_along(crop_levels), labels = crop_labels,
                       expand = expansion(add = 0.45)) +
    scale_y_continuous(expand = expansion(mult = 0.08)) +
    scale_fill_manual(values = COL_EFF) +
    labs(x = NULL, y = ylab, fill = NULL) +
    theme_ch4(base, x_angle = if (ncol == 1) 0 else 90) +
    guides(fill = guide_legend(nrow = 1))
  if (ncol > 1)
    p <- p + facet_wrap(~ region, ncol = ncol, drop = FALSE,
                        scales = if (FREE_Y) "free_y" else "fixed")
  p
}

# --- 保存（w, h は cm の実寸）-----------------------------------------------
FIG_SUB <- ""
save_fig <- function(p, name, w = FIG_W, h = FIG_H, sub = FIG_SUB) {
  dir <- if (nzchar(sub)) file.path(FIGDIR, sub) else FIGDIR
  dir.create(dir, showWarnings = FALSE, recursive = TRUE)
  ggsave(file.path(dir, paste0(name, ".png")), p,
         width = w / 2.54, height = h / 2.54, dpi = 600, bg = "white", limitsize = FALSE)
  message("saved: ", file.path(sub, paste0(name, ".png")), "  (", w, " x ", h, " cm)")
}
