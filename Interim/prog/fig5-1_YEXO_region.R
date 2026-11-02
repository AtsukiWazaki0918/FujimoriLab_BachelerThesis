# =============================================================================
# fig5-1_YEXO_region.R : 中間報告（Word 貼り付け用）の図
#   fig5-1_YEXO_region.R / fig5-2_PROD_kcal_world.R / fig5-3_XPRC_world.R /
#   first_fig5-3_XPRP_world.R の 4 ファイルは中身が同じ（元は ch4/R/17_report.R の 1 本）。
#   どれを実行しても ../output に下の 4 枚がすべて出る。ファイル名は output との対応を示すためのもの。
#   作業ディレクトリを Interim/prog/ にして実行する。
#   図の体裁は 00_common.R のテーマ（藤森研の規定準拠）をそのまま使う。
#   本文幅 16 cm の実寸で出力するので、R のポイント数が Word のポイント数と一致する。
#
#     図5.1 外生収量 YEXO   17 地域別（気候変動影響のみ 2 本）      → fig5-1_YEXO_region.png
#     図5.2 生産量   PROD   世界合計（4 効果、作物の積み上げ）       → fig5-2_PROD_kcal_world.png
#     図5.3 消費者価格 XPRC 世界平均                               → fig5-3_XPRC_world.png
#     初版の図5.3 生産者価格 XPRP 世界平均（修正版では削除）      → first_fig5-3_XPRP_world.png
# =============================================================================
source("00_common.R")

# 出力デバイス : "png"（既定）/ "emf"（規定の推奨形式、devEMF が必要）/ "svg"
OUT_DEV <- "png"

CROP5 <- c("wht","RIC","CGR","OSD","SGC")
CROP_LAB <- c(wht="Wheat", RIC="Rice", CGR="Coarse grains",
              OSD="Oilseeds", SGC="Sugar crops")
CROP_SHORT <- unname(CROP_LAB)

save_report <- function(p, name, w_cm, h_cm) {
  dir <- FIGDIR; dir.create(dir, showWarnings = FALSE, recursive = TRUE)
  w <- w_cm / 2.54; h <- h_cm / 2.54
  if (OUT_DEV == "emf") {
    if (!requireNamespace("devEMF", quietly = TRUE))
      stop("devEMF が入っていません。install.packages('devEMF') を実行してください。")
    devEMF::emf(file.path(dir, paste0(name, ".emf")), width = w, height = h,
                family = FONT, coordDPI = 600, emfPlus = TRUE)
    print(p); dev.off()
  } else if (OUT_DEV == "svg") {
    ggsave(file.path(dir, paste0(name, ".svg")), p, width = w, height = h, bg = "white")
  } else {
    ggsave(file.path(dir, paste0(name, ".png")), p, width = w, height = h,
           dpi = 600, bg = "white")
  }
  message("saved: ", file.path(dir, name), " (", w_cm, " x ", h_cm, " cm)")
}

# ---- 図5.1 外生収量（地域別・気候変動影響のみ）------------------------------
p51 <- fig_climate_only(get_eff("YEXO", items = CROP5),
                        ylab = "Change in exogenous yield (t/ha)",
                        crop_levels = CROP5, crop_labels = CROP_SHORT)
save_report(p51, "fig5-1_YEXO_region", 16, 12)

# ---- 図5.2 生産量（世界合計）------------------------------------------------
# 目盛りを a × 10^n の形で表示する。a は本文と同じ有効数字 3 桁（例 2.00）。0 は 0 のまま。
label_pow10 <- function(x, digits = 3) {
  lapply(x, function(v) {
    if (is.na(v)) return(NA)
    if (v == 0) return(quote(0))
    n <- floor(log10(abs(v)))
    a <- formatC(v / 10^n, format = "f", digits = digits - 1)
    bquote(.(a) %*% 10^.(n))
  }) |> as.expression()
}
# effect_kcal.csv は PJ に換算済みなので、GDX の元の単位 million kcal に戻して描く
d52 <- get_eff_world("PROD_kcal", items = CROP5) %>%
  mutate(value = value / 4.184e-6,
         Crop = factor(CROP_LAB[ITEM], levels = unname(CROP_LAB)))
p52 <- fig_by_effect(d52, "Crop", COL_CROP, ncol = 1,
                     ylab = "Change in production (million kcal)") +
  scale_y_continuous(labels = label_pow10)
save_report(p52, "fig5-2_PROD_kcal_world", 16, 9)

# ---- 初版の図5.3 生産者価格（世界平均。修正版では削除）--------------------------------------------
p53 <- fig_by_crop(get_eff_world("XPRP", items = CROP5), ncol = 1,
                   ylab = "Change in producer price index (2015 = 1)",
                   crop_levels = CROP5, crop_labels = CROP_SHORT)
save_report(p53, "first_fig5-3_XPRP_world", 16, 9)

# ---- 図5.3 消費者価格（世界平均。初版では図5.4）--------------------------------------------
p54 <- fig_by_crop(get_eff_world("XPRC", items = CROP5), ncol = 1,
                   ylab = "Change in consumer price index (2015 = 1)",
                   crop_levels = CROP5, crop_labels = CROP_SHORT)
save_report(p54, "fig5-3_XPRC_world", 16, 9)

# ---- 本文に書く数値の確認 ---------------------------------------------------
for (v in c("YEXO", "PROD_kcal", "XPRP", "XPRC")) {
  cat("\n==", v, "(World) ==\n")
  print(as.data.frame(get_eff_world(v, items = CROP5) %>%
    select(ITEM, Factor, value) %>%
    tidyr::pivot_wider(names_from = Factor, values_from = value)), digits = 4)
}
