# =========================================================
# rGREAT analysis for 4 BED files
# =========================================================

# -----------------------------
# 0. Install packages if needed
# -----------------------------
if (!requireNamespace("BiocManager", quietly = TRUE)) install.packages("BiocManager")

BiocManager::install(c("rtracklayer", "rGREAT", "GenomicRanges", "GenomeInfoDb","stringr"))


library(rGREAT)
library(rtracklayer)
library(GenomicRanges)
library(GenomeInfoDb)
library(ggplot2)
library(dplyr)
library(rtracklayer)
library(stringr)

# -----------------------------
# 1. User settings
# -----------------------------
mouse_tss_source <- "mm10"
human_tss_source <- "hg38"

# ontology
ontology_to_run <- "GO:BP"

# make your own output directory
outdir <- "results/task_4_rgreat"
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)

# -----------------------------
# 2. Read BED files
# -----------------------------
mouse_specific <- import(file.path("/results/mapping/mouse_specific.bed"))
human_specific <- import(file.path("/results/mapping/human_specific.bed"))
conserved_mouse_in_human <- import(file.path("/results/mapping/conserved_mouse_in_human.bed"))
conserved_human_in_mouse <- import(file.path("/results/mapping/conserved_human_in_mouse.bed"))

# -----------------------------
# 3. Clean helper
# -----------------------------
clean_gr <- function(gr) {
  gr <- keepStandardChromosomes(gr, pruning.mode = "coarse")
  gr <- sort(gr)
  gr <- reduce(gr)
  gr
}

mouse_specific <- clean_gr(mouse_specific)
human_specific <- clean_gr(human_specific)
conserved_mouse_in_human <- clean_gr(conserved_mouse_in_human)
conserved_human_in_mouse <- clean_gr(conserved_human_in_mouse)

# -----------------------------
# 4. Build background regions
# -----------------------------

bg_mouse <- reduce(c(mouse_specific, conserved_human_in_mouse))
bg_human <- reduce(c(human_specific, conserved_mouse_in_human))

# -----------------------------
# 5. Basic QC print
# -----------------------------
cat("=== Region counts after reduce() ===\n")
cat("mouse_specific:", length(mouse_specific), "\n")
cat("human_specific:", length(human_specific), "\n")
cat("conserved_human_in_mouse:", length(conserved_human_in_mouse), "\n")
cat("conserved_mouse_in_human:", length(conserved_mouse_in_human), "\n")
cat("bg_mouse:", length(bg_mouse), "\n")
cat("bg_human:", length(bg_human), "\n\n")

cat("=== Total widths ===\n")
cat("mouse_specific width:", sum(width(mouse_specific)), "\n")
cat("human_specific width:", sum(width(human_specific)), "\n")
cat("bg_mouse width:", sum(width(bg_mouse)), "\n")
cat("bg_human width:", sum(width(bg_human)), "\n\n")

# -----------------------------
# 6. Run rGREAT
# -----------------------------

mouse_job <- great(
  gr = mouse_specific,
  gene_sets = ontology_to_run,
  tss_source = mouse_tss_source,
  background = bg_mouse
)

human_job <- great(
  gr = human_specific,
  gene_sets = ontology_to_run,
  tss_source = human_tss_source,
  background = bg_human
)

# -----------------------------
# 7. Extract enrichment tables
# -----------------------------
mouse_tbl <- getEnrichmentTable(mouse_job)
human_tbl <- getEnrichmentTable(human_job)

# save
write.csv(mouse_tbl,
          file.path(outdir, "mouse_specific_rGREAT_GO_BP.csv"),
          row.names = FALSE)
write.csv(human_tbl,
          file.path(outdir, "human_specific_rGREAT_GO_BP.csv"),
          row.names = FALSE)

# -----------------------------
# 8. Check columns and simplify
# -----------------------------
cat("=== Mouse result columns ===\n")
print(colnames(mouse_tbl))
cat("\n=== Human result columns ===\n")
print(colnames(human_tbl))
cat("\n")


standardize_tbl <- function(tb, label) {
  tb2 <- tb
  
  term_col <- intersect(c("name", "term_name", "description"), colnames(tb2))
  if (length(term_col) == 0) stop("Cannot find term name column.")
  term_col <- term_col[1]
  
  padj_col <- intersect(c("p_adjust", "adj_p_value", "fdr", "q_value"), colnames(tb2))
  if (length(padj_col) == 0) stop("Cannot find adjusted p-value column.")
  padj_col <- padj_col[1]
  
  enrich_col <- intersect(c("fold_enrichment", "fold_enrichment_binom", "enrichment"), colnames(tb2))
  if (length(enrich_col) == 0) {
    tb2$fold_enrichment_final <- NA_real_
  } else {
    enrich_col <- enrich_col[1]
    tb2$fold_enrichment_final <- tb2[[enrich_col]]
  }
  
  tb2$term_name_final <- tb2[[term_col]]
  tb2$padj_final <- tb2[[padj_col]]
  tb2$neglog10_padj <- -log10(tb2$padj_final)
  tb2$dataset <- label
  
  tb2
}

mouse_tbl2 <- standardize_tbl(mouse_tbl, "mouse_specific")
human_tbl2 <- standardize_tbl(human_tbl, "human_specific")

# -----------------------------
# 9. Keep significant terms
# -----------------------------
mouse_sig <- mouse_tbl2 %>%
  filter(!is.na(padj_final), padj_final < 0.05) %>%
  arrange(padj_final)

human_sig <- human_tbl2 %>%
  filter(!is.na(padj_final), padj_final < 0.05) %>%
  arrange(padj_final)

write.csv(mouse_sig,
          file.path(outdir, "mouse_specific_rGREAT_GO_BP_sig.csv"),
          row.names = FALSE)
write.csv(human_sig,
          file.path(outdir, "human_specific_rGREAT_GO_BP_sig.csv"),
          row.names = FALSE)

# -----------------------------
# 10. Plot top terms
# -----------------------------

combined_sig <- bind_rows(mouse_sig, human_sig)

# top10 term
tb2 <- combined_sig %>%
  group_by(dataset) %>%
  arrange(padj_final, .by_group = TRUE) %>%
  slice_head(n = 10) %>%
  ungroup()

tb2 <- tb2 %>%
  mutate(term_name_final = str_wrap(term_name_final, width = 34))

tb2$dataset <- factor(tb2$dataset, levels = c("mouse_specific", "human_specific"))

if (!"fold_enrichment_final" %in% colnames(tb2)) {
  tb2$fold_enrichment_final <- 1
}


tb2 <- tb2 %>%
  group_by(dataset) %>%
  mutate(term_plot = factor(term_name_final, levels = rev(unique(term_name_final)))) %>%
  ungroup()

p <- ggplot(
  tb2,
  aes(x = neglog10_padj, y = term_plot)
) +
  geom_point(
    aes(size = fold_enrichment_final, fill = neglog10_padj),
    shape = 21,
    color = "black",
    stroke = 0.25,
    alpha = 0.95
  ) +
  facet_wrap(~dataset, scales = "free_y", ncol = 2) +
  scale_fill_gradient(
    low = "#DCE6F2",
    high = "#4C78A8",
    name = expression(-log[10]("adj. p"))
  ) +
  scale_size_continuous(
    range = c(2.5, 7),
    name = "Fold enrichment"
  ) +
  labs(
    x = expression(-log[10]("adjusted p-value")),
    y = NULL
  ) +
  theme_classic(base_size = 12) +
  theme(
    strip.background = element_blank(),
    strip.text = element_text(face = "bold", size = 12, color = "black"),
    axis.text.y = element_text(size = 10.5, color = "black"),
    axis.text.x = element_text(size = 10.5, color = "black"),
    axis.title.x = element_text(size = 11.5, color = "black"),
    axis.line.x = element_line(color = "black", linewidth = 0.4),
    axis.line.y = element_line(color = "black", linewidth = 0.4),
    axis.ticks = element_line(color = "black", linewidth = 0.35),
    panel.grid.major.x = element_line(color = "#E8E8E8", linewidth = 0.35),
    panel.grid.major.y = element_blank(),
    panel.grid.minor = element_blank(),
    legend.title = element_text(size = 10.5),
    legend.text = element_text(size = 9.5),
    legend.position = "right",
    plot.margin = margin(8, 18, 8, 8)
  )

print(p)

ggsave(
  file.path(outdir, "nature_dotplot_rgreat.png"),
  p,
  width = 11.5,
  height = 6.2,
  dpi = 300,
  bg = "white"
)
# -----------------------------
# 11. Optional: compare top terms side by side
# -----------------------------
combined_sig <- bind_rows(mouse_sig, human_sig)

top_compare <- combined_sig %>%
  group_by(dataset) %>%
  slice_head(n = 8) %>%
  ungroup() %>%
  mutate(term_name_final = paste(dataset, term_name_final, sep = " | "))

write.csv(combined_sig,
          file.path(outdir, "combined_mouse_human_sig_terms.csv"),
          row.names = FALSE)

cat("\nDone. Results saved in:", outdir, "\n")

