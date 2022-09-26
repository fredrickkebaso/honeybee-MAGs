---
title: "Medgenome India cross-species data"
author: Aiswarya Prasad
date: "`r format(Sys.time(), '%d %B, %Y')`"
output:
  prettydoc::html_pretty:
    theme: cayman
    <!-- other fun themes: architect leonids hpstr cayman -->
    highlight: github
    math: katex
    number_sections: true
    df_print: paged
    cold-folding: hide
    toc: true
  github_document: default
---
<!-- comment out for pdf compiling -->
<!-- some css for formatting html -->
<!-- <style>
    h1.title {
        font-size: 40px;
        font-family: Serif;
        text-align: center;
        font-weight: normal;
        /* color: DarkRed; */
    }
    h1 {
        font-size: 24px;
        font-family: Serif;
        font-weight: bold;
        /* font-weight: bold; */
        /* text-align: center; */
        /* color: DarkRed; */
    }
    h2 {
        font-size: 22px;
        font-family: Serif;
        font-weight: bold;
        /* text-align: center; */
        /* color: DarkRed; */
    }
    h3 {
        font-size: 20px;
        font-family: Serif;
        font-weight: bold;
        /* text-align: center; */
        /* color: DarkRed; */
    }
    body .main-container {
        /* max-width: 1000px; */
        font-size: 18px;
        font-family: Serif;
    }
</style> -->

```{css echo=FALSE, warning=FALSE}
/* To make hoverable links. (does not have to be called hint) Usage: */
/* [Message to show on hover]{.hint} */
.hint {
  visibility: hidden;
}

.hint::before {
  visibility: visible;
  content: "Hint";
  color: blue;
}

.hint:hover {
  visibility: visible;
  font-weight: bold;
}

.hint:hover::before {
  display: none;
}
```

```{r setup, include=FALSE}
knitr::opts_chunk$set(engine.opts = list(bash = "-l"))
knitr::opts_chunk$set(cache=FALSE)
knitr::opts_chunk$set(echo=FALSE, message=FALSE, error=FALSE, warning=FALSE, results='hide', fig.show='hide')
# load libraries
library(ggplot2)
library(kableExtra)
library(knitr)
library(tidyverse)
library(viridis)
library(hrbrthemes)
library(ggthemes)
library(RColorBrewer)
library(scales)
library(dplyr)
library(gridExtra)
library(ggVennDiagram)
library(vegan)
library(ape)
# useful function(s)
make_theme <- function(theme_name=theme_classic() ,max_colors=0, palettefill="Pastel1", palettecolor="Dark2",
                        setFill=TRUE, setCol=TRUE,
                        guide_nrow=2, guide_nrow_byrow=TRUE, leg_pos="top", leg_size=12,
                        x_angle=0 ,x_vj=0, x_hj=0, x_size=12,
                        y_angle=0 ,y_vj=0, y_hj=0, y_size=12){
  n_11 = c("BrBG", "PiYG", "PRGn", "PuOr", "RdBu", "RdGy", "RdYlBu", "RdYlGn", "Spectral")
  n_12 = c("Paired", "Set3")
  n_8 = c("Accent", "Dark2", "Pastel2", "Set2")
  if (palettefill %in% n_12) {
    n_f = 12
  } else {
    if (palettefill %in% n_11) {
      n_f = 11
    } else {
      if (palettefill %in% n_8) {
        n_f  = 8
      } else {
        n_f = 9
      }
    }
  }
  if (palettecolor %in% n_12) {
    n_c = 12
  } else {
    if (palettecolor %in% n_11) {
      n_c = 11
    } else {
      if (palettecolor %in% n_8) {
        n_c  = 8
      } else {
        n_c = 9
      }
    }
  }
  getFill = colorRampPalette(brewer.pal(n_f, palettefill))
  getColor = colorRampPalette(brewer.pal(n_c, palettecolor))
  theme_params <- theme(axis.text.x = element_text(angle = x_angle,
    vjust = x_vj, hjust=x_hj,
    size = x_size),
    axis.text.y = element_text(angle = y_angle,
      vjust = y_vj, hjust=y_hj,
      size = y_size),
      # axis.title.x = element_text(margin=margin(t=5)),
      # axis.title.y = element_text(margin=margin(r=10)),
      legend.position=leg_pos,
      legend.text = element_text(size=leg_size)
    )
  guide_params <- guides(fill = guide_legend(
                                  nrow=guide_nrow,
                                  byrow=guide_nrow_byrow
                                ),
                        col = guide_legend(
                                  nrow=guide_nrow,
                                  byrow=guide_nrow_byrow
                                )
                  )
  my_theme <- list(
                theme_name,
                theme_params,
                guide_params
              )

  if(setFill) {
    if (n_f < max_colors) {
      my_theme <- list(
                    my_theme,
                    scale_fill_manual(values = getFill(max_colors), na.value="grey")
                  )

    } else {
      my_theme <- list(
                    my_theme,
                    scale_fill_brewer(palette=palettefill, na.value="grey")
                  )
    }
  }
  if(setCol) {
    if (n_c < max_colors) {
      my_theme <- list(
                    my_theme,
                    scale_color_manual(values = getColor(max_colors), na.value="grey")
                  )

    } else {
      my_theme <- list(
                    my_theme,
                    scale_color_brewer(palette=palettecolor, na.value="grey")
                  )
    }
  }
  return(my_theme)
}

get_phylotype <- function(SDP){
  # only works if sdps are written in the right format
  # phylotype_x (eg. firm5_1)
  phy = strsplit(SDP, "_")[[1]][1]
  return(phy)
}
get_host_from_colony <- function(colony_name){
  # only works if sdps are written in the right format
  # phylotype_x (eg. Am_xx)
  host_name = strsplit(colony_name, "_")[[1]][1]
  if (host_name == "Am"){
    return("Apis mellifera")
  }
  if (host_name == "Ac"){
    return("Apis cerana")
  }
  if (host_name == "Ad"){
    return("Apis dorsata")
  }
  if (host_name == "Af"){
    return("Apis florea")
  }
  return(NA)
}

get_sample_name <- function(magname){
  if (startsWith(magname, "MAG_")){
    paste0(head(strsplit(strsplit(magname, "MAG_")[[1]][2], "_")[[1]], -1), collapse="_")
  } else {
    strsplit(magname, "_MAG")[[1]][1]
  }
}

get_host_name <- function(magname){
  if (startsWith(magname, "MAG_")){
    sample_name = strsplit(magname, "MAG_")[[1]][2]
    if (grepl("Dr|Gr", sample_name)) {
      return("Apis mellifera")
    }
    if (grepl("Am", sample_name)) {
      return("Apis mellifera")
    }
    if (grepl("Ac", sample_name)) {
      return("Apis cerana")
    }
    if (grepl("M1.|M2.|M3.", sample_name)) {
      return("Apis mellifera")
    }
    if (grepl("C1.|C2.|C3.", sample_name)) {
      return("Apis cerana")
    }
    if (grepl("D1.|D2.|D3.", sample_name)) {
      return("Apis dorsata")
    }
    if (grepl("F1.|F2.|F3.", sample_name)) {
      return("Apis florea")
    }
  }
  else {
    sample_name = strsplit(magname, "_MAG")[[1]][1]
    if (grepl("Dr|Gr", sample_name)) {
      return("Apis mellifera")
    }
    if (grepl("Am", sample_name)) {
      return("Apis mellifera")
    }
    if (grepl("Ac", sample_name)) {
      return("Apis cerana")
    }
    if (grepl("M1.|M2.|M3.", sample_name)) {
      return("Apis mellifera")
    }
    if (grepl("C1.|C2.|C3.", sample_name)) {
      return("Apis cerana")
    }
    if (grepl("D1.|D2.|D3.", sample_name)) {
      return("Apis dorsata")
    }
    if (grepl("F1.|F2.|F3.", sample_name)) {
      return("Apis florea")
    }
  }
}

get_origin_name <- function(magname){
  if (startsWith(magname, "MAG_")){
    sample_name = strsplit(magname, "MAG_")[[1]][2]
    if (grepl("Dr|Gr", sample_name)) {
      return("Switzerland, Engel apiary")
    }
    if (grepl("Am", sample_name)) {
      return("Japan")
    }
    if (grepl("Ac", sample_name)) {
      return("Japan")
    }
    if (grepl("M1.|M2.|M3.", sample_name)) {
      return("India")
    }
    if (grepl("C1.|C2.|C3.", sample_name)) {
      return("India")
    }
    if (grepl("D1.|D2.|D3.", sample_name)) {
      return("India")
    }
    if (grepl("F1.|F2.|F3.", sample_name)) {
      return("India")
    }
  }
  else {
    sample_name = strsplit(magname, "_MAG")[[1]][1]
    if (grepl("Dr|Gr", sample_name)) {
      return("Switzerland, Engel apiary")
    }
    if (grepl("Am", sample_name)) {
      return("Japan")
    }
    if (grepl("Ac", sample_name)) {
      return("Japan")
    }
    if (grepl("M1.|M2.|M3.", sample_name)) {
      return("India")
    }
    if (grepl("C1.|C2.|C3.", sample_name)) {
      return("India")
    }
    if (grepl("D1.|D2.|D3.", sample_name)) {
      return("India")
    }
    if (grepl("F1.|F2.|F3.", sample_name)) {
      return("India")
    }
  }
}
get_only_legend <- function(plot) {
  # get tabular interpretation of plot
  plot_table <- ggplot_gtable(ggplot_build(plot))
  #  Mark only legend in plot
  legend_plot <- which(sapply(plot_table$grobs, function(x) x$name) == "guide-box")
  # extract legend
  legend <- plot_table$grobs[[legend_plot]]
  # return legend
  return(legend)
}
```
# Introduction

The analysis is split into multiple parts.

1. A database-dependent mapping and community profiling at the SDP and Phylotype level.
2. An assembly-based approach which involes MAG binning per sample and dereplication.
Requires manual annotation of input for the next section
3. Core genome phylogeny construction of MAGs and isolate genomes.
  (a) All high-quality MAGs
  (b) One MAG per magOTU cluster
4. Mapping and SNV calling of reads to
  (a) Just MAGs
  (b) A combination of isolates and MAGs

The samples used in this analysis are mentioned below.

* "M1.1", "M1.2", "M1.3", "M1.4", "M1.5",
  * _Apis mellifera_ from India
* "DrY2_F1","DrY2_F2",
  * _Apis mellifera_ from Switzerland
* "AmAi02","AmIu02",
  * _Apis mellifera_ from Japan
* "C1.1", "C1.2", "C1.3", "C1.4", "C1.5",
  * _Apis cerana_ from India, colony number 1
* "C2.1", "C2.2", "C2.3", "C2.4", "C2.5",
  * _Apis cerana_ from India, colony number 2
* "C3.1", "C3.2", "C3.3", "C3.4", "C3.5",
  * _Apis cerana_ from India, colony number 1
* "AcCh05","AcKn01",
  * _Apis cerana_ from Japan
* "D1.1","D1.2","D1.3","D1.4","D1.5",
  * _Apis dorsata_ from India, colony number 1
* "D2.1","D2.2","D2.3","D2.4","D2.5",
  * _Apis dorsata_ from India, colony number 2
* "D3.1","D3.2","D3.3","D3.4","D3.5",
  * _Apis dorsata_ from India, colony number 3
* "F1.1","F1.2","F1.3","F1.4","F1.5",
  * _Apis florea_ from India, colony number 1
* "F2.1","F2.2","F2.3","F2.4","F2.5",
  * _Apis florea_ from India, colony number 2
* "F3.1","F3.2","F3.3","F3.4","F3.5"
  * _Apis florea_ from India, colony number 3

# Results

## Data summary

56 samples were first mapped to a host database and then the unmapped reads to a microbiome database.

The raw reads and trimmed reads were checked for quality using the tool [fastqc](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/). The report (html format) also summarises basic statistics including number of reads. The QC results can be found in their respective folders at `./fastqc/raw/{SAMPLE}_R*_fastqc.html` and `./fastqc/trim/{SAMPLE}_R*_trim_fastqc.html`.

```{r predefined_vectors}
samples <- c("M1.1", "M1.2", "M1.3", "M1.4", "M1.5",
              "C1.1", "C1.2", "C1.3", "C1.4", "C1.5",
              "C2.1", "C2.2", "C2.3", "C2.4", "C2.5",
              "C3.1", "C3.2", "C3.3", "C3.4", "C3.5",
              "D1.1","D1.2","D1.3","D1.4","D1.5",
              "D2.1","D2.2","D2.3","D2.4","D2.5",
              "D3.1","D3.2","D3.3","D3.4","D3.5",
              "F1.1","F1.2","F1.3","F1.4","F1.5",
              "F2.1","F2.2","F2.3","F2.4","F2.5",
              "F3.1","F3.2","F3.3","F3.4","F3.5"
            )
india_samples <- c("M1.1", "M1.2", "M1.3", "M1.4", "M1.5",
              "C1.1", "C1.2", "C1.3", "C1.4", "C1.5",
              "C2.1", "C2.2", "C2.3", "C2.4", "C2.5",
              "C3.1", "C3.2", "C3.3", "C3.4", "C3.5",
              "D1.1","D1.2","D1.3","D1.4","D1.5",
              "D2.1","D2.2","D2.3","D2.4","D2.5",
              "D3.1","D3.2","D3.3","D3.4","D3.5",
              "F1.1","F1.2","F1.3","F1.4","F1.5",
              "F2.1","F2.2","F2.3","F2.4","F2.5",
              "F3.1","F3.2","F3.3","F3.4","F3.5"
            )
colonies <- c("M_1", "M_1", "M_1", "M_1", "M_1",
             "M_DrY2_F","M_DrY2_F","M_Ai","M_Iu",
              "C_1", "C_1", "C_1", "C_1", "C_1",
              "C_2", "C_2", "C_2", "C_2", "C_2",
              "C_3", "C_3", "C_3", "C_3", "C_3",
              "C_Ch","C_Kn",
              "D_1","D_1","D_1","D_1","D_1",
              "D_2","D_2","D_2","D_2","D_2",
              "D_3","D_3","D_3","D_3","D_3",
              "F_1","F_1","F_1","F_1","F_1",
              "F_2","F_2","F_2","F_2","F_2",
              "F_3","F_3","F_3","F_3","F_3")
host_order <- c("Apis mellifera", "Apis cerana", "Apis dorsata", "Apis florea")
host_order_color <- c("Apis mellifera" = brewer.pal(9, "Set1")[2], "Apis cerana" = brewer.pal(9, "Set1")[1], "Apis dorsata" = brewer.pal(9, "Set1")[4], "Apis florea" = brewer.pal(9, "Set1")[3])
colony_order <- c("M_1", "M_Iu", "M_Ai", "M_DrY2_F", "C_1", "C_2", "C_3", "C_Kn", "C_Ch", "D_1", "D_2", "D_3", "F_1", "F_2", "F_3")
location_order <- c("AIST_Am", "UT_Am", "Bee park, GKVK_Am","Les Droites_Am",
                    "NCBS campus_Ac", "Bee park, GKVK_Ac", "Chiba_Ac", "Kanagawa_Ac",
                    "Biological sciences building, IISc_Ad","House near NCBS_Ad","Naideli hostel_Ad",
                    "Bangalore outskirts_Af")
phylotypes <- c("firm4", "firm5", "api", "bifido", "bom", "com", "bapis", "fper", "lkun", "snod", "gilli")
phylotypes_heatmap_order <- c("snod", "gilli", "firm4", "firm5", "bifido", "bapis", "fper", "api", "lkun", "bom", "com")
sdps <- c('firm4_1', 'firm4_2',
          'firm5_1', 'firm5_2', 'firm5_3', 'firm5_4', 'firm5_7', 'firm5_bombus',
          # 'bifido_1', 'bifido_2', 'bifido_bombus',
          'bifido_1.1', 'bifido_1.2', 'bifido_1.3', 'bifido_1.4', 'bifido_1.5', 'bifido_2', 'bifido_1_cerana', 'bifido_bombus',
          'api_1', 'api_apis_dorsa', 'api_bombus',
          'bom_1', 'bom_apis_melli', 'bom_bombus',
          'com_1', 'com_drosophila', 'com_monarch',
          'bapis',
          'fper_1',
          'lkun',
          'snod_1', 'snod_2', 'snod_bombus',
          'gilli_1', 'gilli_2', 'gilli_3', 'gilli_4', 'gilli_5', 'gilli_6',
          'gilli_apis_andre', 'gilli_apis_dorsa', 'gilli_bombus')
# Data_dir <- "04_CoreCov_211018_Medgenome_india_samples"

#########################################################
# Vector of colors for Phylotypes and SDPs and families
#########################################################
# Family colors
# species <- c('s__Bombilactobacillus mellis', 's__Lactobacillus panisapium', 's__', 's__Gilliamella apicola_E', 's__Bombilactobacillus mellifer', 's__Lactobacillus apis', 's__Snodgrassella alvi', 's__Lactobacillus melliventris', 's__Lactobacillus helsingborgensis', 's__Frischella perrara', 's__Enterobacter hormaechei_A', 's__Apibacter sp002964915', 's__Snodgrassella alvi_E', 's__Frischella japonica', 's__Gilliamella apicola_F', 's__Spiroplasma melliferum', 's__Bartonella apis', 's__Apibacter adventoris', 's__Apilactobacillus kunkeei_A', 's__Hafnia paralvei', 's__Pantoea vagans', 's__Gilliamella apicola_K', 's__Gilliamella apicola', 's__Snodgrassella alvi_G', 's__Bifidobacterium indicum', 's__Gilliamella apicola_N', 's__Klebsiella variicola', 's__Commensalibacter sp003202795', 's__Gilliamella apicola_Q')
# speciesColors
genera <- c("g__Bombilactobacillus", "g__Lactobacillus", "g__Bifidobacterium", "g__Gilliamella", "g__Snodgrassella", "g__Bartonella", "g__Frischella", "g__Enterobacter", "g__", "g__Pectinatus", "g__Apibacter", "g__Dysgonomonas", "g__Spiroplasma", "g__Zymobacter", "g__Entomomonas", "g__Saezia", "g__Parolsenella", "g__WRHT01", "g__Commensalibacter", "g__Apilactobacillus", "g__Bombella")
phy_group_dict = c("firm4" = "g__Bombilactobacillus",
            "g__Bombilactobacillus_outgroup" = "g__Bombilactobacillus",
            "firm5" = "g__Lactobacillus",
            "lacto" = "g__Lactobacillus",
            "g__Lactobacillus_outgroup" = "g__Lactobacillus",
            "bifido" = "g__Bifidobacterium",
            "g__Bifidobacterium_outgroup" = "g__Bifidobacterium",
            "gilli" = "g__Gilliamella",
            "entero" = "g__Gilliamella",
            "g__Gilliamella_outgroup" = "g__Gilliamella",
            "fper" = "g__Frischella",
            "g__Frischella_outgroup" = "g__Frischella",
            "snod" = "g__Snodgrassella",
            "g__Snodgrassella_outgroup" = "g__Snodgrassella",
            "bapis" = "g__Bartonella",
            "g__Bartonella_outgroup" = "g__Bartonella",
            # "" = "g__Enterobacter",
            "g__Enterobacter_outgroup" = "g__Enterobacter",
            # "" = "g__",
            # "" = "g__Pectinatus",
            "g__Pectinatus_outgroup" = "g__Pectinatus",
            "api" = "g__Apibacter",
            "g__Apibacter_outgroup" = "g__Apibacter",
            # "" = "g__Dysgonomonas",
            "g__Dysgonomonas_outgroup" = "g__Dysgonomonas",
            # "" = "g__Spiroplasma",
            "g__Spiroplasma_outgroup" = "g__Spiroplasma",
            # "" = "g__Zymobacter",
            "g__Zymobacter_outgroup" = "g__Zymobacter",
            # "" = "g__Entomomonas",
            "g__Entomomonas_outgroup" = "g__Entomomonas",
            # "" = "g__Saezia",
            "g__Saezia_outgroup" = "g__Saezia",
            # "" = "g__Parolsenella",
            "g__Parolsenella_outgroup" = "g__Parolsenella",
            # "" = "g__WRHT01",
            "g__WRHT01_outgroup" = "g__WRHT01",
            "com" = "g__Commensalibacter",
            "g__Commensalibacter_outgroup" = "g__Commensalibacter",
            "lkun" = "g__Apilactobacillus",
            "g__Apilactobacillus_outgroup" = "g__Apilactobacillus",
            "bom" = "g__Bombella",
            "g__Bombella_outgroup" = "g__Bombella"
          )
genusColors <- list("g__Bombilactobacillus" = head(colorRampPalette(c(brewer.pal(11, "Spectral")[1], "#FFFFFF"))(10), -1)[1],
                    "g__Lactobacillus" = head(colorRampPalette(c(brewer.pal(11, "Spectral")[1], "#FFFFFF"))(10), -1)[4],
                    "g__Bifidobacterium" = brewer.pal(11, "Spectral")[3],
                    "g__Gilliamella" = brewer.pal(11, "Spectral")[11],
                    "g__Frischella" = brewer.pal(11, "Spectral")[8],
                    "g__Bartonella" = brewer.pal(11, "Spectral")[7],
                    "g__Snodgrassella" = brewer.pal(11, "Spectral")[10],
                    "g__Apibacter" = brewer.pal(11, "Spectral")[4],
                    "g__Commensalibacter" = brewer.pal(11, "Spectral")[6],
                    "g__Bombella" = brewer.pal(11, "Spectral")[5],
                    "g__Apilactobacillus" = brewer.pal(11, "Spectral")[9],
                    "g__Dysgonomonas" = brewer.pal(11, "Spectral")[2],
                    "g__Spiroplasma" = brewer.pal(8, "Set1")[8],
                    "g__WRHT01" = brewer.pal(8, "Dark2")[3],
                    "g__Pectinatus" = brewer.pal(8, "Dark2")[1],
                    "g__Enterobacter" = head(colorRampPalette(c(brewer.pal(11, "BrBG")[2], "#FFFFFF"))(10), -1)[1],
                    "g__Zymobacter" = head(colorRampPalette(c(brewer.pal(11, "BrBG")[2], "#FFFFFF"))(10), -1)[2],
                    "g__Entomomonas"= head(colorRampPalette(c(brewer.pal(11, "BrBG")[2], "#FFFFFF"))(10), -1)[4],
                    "g__Saezia" = head(colorRampPalette(c(brewer.pal(11, "BrBG")[2], "#FFFFFF"))(10), -1)[6],
                    "g__Parolsenella" = head(colorRampPalette(c(brewer.pal(11, "BrBG")[2], "#FFFFFF"))(10), -1)[8],
                    "g__" = "#000000"
)

families <- c("f__Lactobacillaceae", "f__Bifidobacteriaceae", "f__Enterobacteriaceae", "f__Neisseriaceae", "f__Rhizobiaceae_A", "f__Selenomonadaceae", "f__Weeksellaceae", "f__Dysgonomonadaceae", "f__Mycoplasmataceae", "f__Halomonadaceae", "f__Pseudomonadaceae", "f__Burkholderiaceae", "f__Atopobiaceae", "f__Desulfovibrionaceae", "f__Acetobacteraceae", "f__", "f__Streptococcaceae")
familyColors <- list(
  "f__Lactobacillaceae" = brewer.pal(11, "Spectral")[1],
  "f__Bifidobacteriaceae" = brewer.pal(11, "Spectral")[3],
  "f__Enterobacteriaceae" = brewer.pal(11, "Spectral")[11],
  "f__Neisseriaceae" = brewer.pal(11, "Spectral")[10],
  "f__Rhizobiaceae_A" = brewer.pal(11, "Spectral")[7],
  "f__Weeksellaceae" = brewer.pal(11, "Spectral")[4],
  "f__Acetobacteraceae" = brewer.pal(11, "Spectral")[6],
  "f__Dysgonomonadaceae" = brewer.pal(11, "Spectral")[2],
  "f__Mycoplasmataceae" = brewer.pal(8, "Set1")[8],
  "f__Desulfovibrionaceae" = brewer.pal(8, "Dark2")[3],
  "f__Selenomonadaceae" = brewer.pal(8, "Dark2")[1],
  "f__Halomonadaceae" = head(colorRampPalette(c(brewer.pal(11, "BrBG")[2], "#FFFFFF"))(10), -1)[2],
  "f__Pseudomonadaceae" = head(colorRampPalette(c(brewer.pal(11, "BrBG")[2], "#FFFFFF"))(10), -1)[4],
  "f__Burkholderiaceae" = head(colorRampPalette(c(brewer.pal(11, "BrBG")[2], "#FFFFFF"))(10), -1)[6],
  "f__Atopobiaceae" = head(colorRampPalette(c(brewer.pal(11, "BrBG")[2], "#FFFFFF"))(10), -1)[8],
  "f__Streptococcaceae" = head(colorRampPalette(c(brewer.pal(11, "BrBG")[2], "#FFFFFF"))(10), -1)[9],
  "f__" = "#000000"
)
#
motus <- c("Lactobacillus", "Bifidobacterium", "Gilliamella", "Frischella", "Snodgrassella", "Bartonella", "Bombella", "Acetobacteraceae", "Dysgonomonadaceae", "Spiroplasma", "Flavobacteriaceae", "Fructobacillus", "unassigned")
motuColors <- list(
  "Lactobacillus" = brewer.pal(11, "Spectral")[1],
  "Bifidobacterium" = brewer.pal(11, "Spectral")[3],
  "Flavobacteriaceae" = brewer.pal(11, "Spectral")[4],
  "Bombella" = brewer.pal(11, "Spectral")[5],
  "Acetobacteraceae" = brewer.pal(11, "Spectral")[6],
  "Bartonella" = brewer.pal(11, "Spectral")[7],
  "Frischella" = brewer.pal(11, "Spectral")[8],
  "Gilliamella" = brewer.pal(11, "Spectral")[11],
  "Snodgrassella" = brewer.pal(11, "Spectral")[10],
  "Dysgonomonadaceae" = brewer.pal(11, "Spectral")[2],
  "Fructobacillus" = brewer.pal(11, "Spectral")[9],
  "Spiroplasma" = head(colorRampPalette(c(brewer.pal(11, "Spectral")[2], "#FFFFFF"))(10), -1)[8],
  "unassigned" = "black"
)
#
PhylotypeColors <- brewer.pal(11,"Spectral")
names(PhylotypeColors) <- phylotypes
# each color from the Spectral palatte corresponds to a phylotype
# each SDP of the phylotype gets a color made by colorRampPalette
# it falls in the sange from the color of the phylotype to #FFFFFF (white)
SDPColors <- c()
# 'firm4'
# 'firm4_1''firm4_2':2
SDPColors <- c(SDPColors, head(colorRampPalette(c(brewer.pal(11, "Spectral")[1], "#FFFFFF"))(3), -1))
# show_col(head(colorRampPalette(c(brewer.pal(11, "Spectral")[1], "#FFFFFF"))(3), -1))
# 'firm5'
# 'firm5_1''firm5_2''firm5_3''firm5_4''firm5_7''firm5_bombus':6
SDPColors <- c(SDPColors, head(colorRampPalette(c(brewer.pal(11, "Spectral")[2], "#FFFFFF"))(7), -1))
# show_col(head(colorRampPalette(c(brewer.pal(11, "Spectral")[2], "#FFFFFF"))(7), -1))
# 'bifido'
# # 'bifido_1''bifido_2''bifido_bombus':3 - no
# 'bifido_1.1', 'bifido_1.2', 'bifido_1.3', 'bifido_1.4', 'bifido_1.5', 'bifido_2', 'bifido_1_cerana' 'bifido_bombus': 8
SDPColors <- c(SDPColors, head(colorRampPalette(c(brewer.pal(11, "Spectral")[3], "#FFFFFF"))(9), -1))
# show_col(head(colorRampPalette(c(brewer.pal(11, "Spectral")[3], "#FFFFFF"))(4), -1))
# 'api'
# 'api_1''api_apis_dorsa''api_bombus':3
SDPColors <- c(SDPColors, head(colorRampPalette(c(brewer.pal(11, "Spectral")[4], "#FFFFFF"))(4), -1))
# show_col(head(colorRampPalette(c(brewer.pal(11, "Spectral")[4], "#FFFFFF"))(4), -1))
# 'bom''bom_apis_melli''bom_bombus':3
SDPColors <- c(SDPColors, head(colorRampPalette(c(brewer.pal(11, "Spectral")[5], "#FFFFFF"))(4), -1))
# show_col(head(colorRampPalette(c(brewer.pal(11, "Spectral")[5], "#FFFFFF"))(4), -1))
# 'com'
# 'com_1''com_drosophila''com_monarch':3
SDPColors <- c(SDPColors, head(colorRampPalette(c(brewer.pal(11, "Spectral")[6], "#FFFFFF"))(4), -1))
# show_col(head(colorRampPalette(c(brewer.pal(11, "Spectral")[6], "#FFFFFF"))(4), -1))
# 'bapis'
# 'bapis':1
SDPColors <- c(SDPColors, head(colorRampPalette(c(brewer.pal(11, "Spectral")[7], "#FFFFFF"))(2), -1))
# show_col(head(colorRampPalette(c(brewer.pal(11, "Spectral")[7], "#FFFFFF"))(2), -1))
# 'fper'
# 'fper_1':1
SDPColors <- c(SDPColors, head(colorRampPalette(c(brewer.pal(11, "Spectral")[8], "#FFFFFF"))(2), -1))
# show_col(head(colorRampPalette(c(brewer.pal(11, "Spectral")[8], "#FFFFFF"))(2), -1))
# 'lkun'
# 'lkun':1
SDPColors <- c(SDPColors, head(colorRampPalette(c(brewer.pal(11, "Spectral")[9], "#FFFFFF"))(2), -1))
# show_col(head(colorRampPalette(c(brewer.pal(11, "Spectral")[9], "#FFFFFF"))(2), -1))
# 'snod'
# 'snod_1''snod_2''snod_bombus':3
SDPColors <- c(SDPColors, head(colorRampPalette(c(brewer.pal(11, "Spectral")[10], "#FFFFFF"))(4), -1))
# show_col(head(colorRampPalette(c(brewer.pal(11, "Spectral")[10], "#FFFFFF"))(4), -1))
# 'gilli'
# 'gilli_1''gilli_2''gilli_3''gilli_4''gilli_5''gilli_6''gilli_apis_andre''gilli_apis_dorsa''gilli_bombus':9
SDPColors <- c(SDPColors, head(colorRampPalette(c(brewer.pal(11, "Spectral")[11], "#FFFFFF"))(10), -1))
# show_col(head(colorRampPalette(c(brewer.pal(11, "Spectral")[11], "#FFFFFF"))(10), -1))
names(SDPColors) <- sdps
```

```{r read_mapping_data, results='hold'}
# setwd("/Volumes/Storage/Work/Temp-from-NAS/cross-species-analysis-india")
df_reads <- data.frame()
for (sample in samples) {
  number_raw_R1 <- read.csv(unz(paste0("fastqc/raw/", sample, "_R1_fastqc.zip"), paste0(sample, "_R1_fastqc/fastqc_data.txt")), sep = "\t") %>%
                filter(.[[1]] == "Total Sequences") %>%
                  pull() %>%
                    as.integer()
  number_raw_R2 <- read.csv(unz(paste0("fastqc/raw/", sample, "_R2_fastqc.zip"), paste0(sample, "_R2_fastqc/fastqc_data.txt")), sep = "\t") %>%
                filter(.[[1]] == "Total Sequences") %>%
                  pull() %>%
                    as.integer()
  number_trimmed_R1 <- read.csv(unz(paste0("fastqc/trim/", sample, "_R1_trim_fastqc.zip"), paste0(sample, "_R1_trim_fastqc/fastqc_data.txt")), sep = "\t") %>%
                filter(.[[1]] == "Total Sequences") %>%
                  pull() %>%
                    as.integer()
  number_trimmed_R2 <- read.csv(unz(paste0("fastqc/trim/", sample, "_R2_trim_fastqc.zip"), paste0(sample, "_R2_trim_fastqc/fastqc_data.txt")), sep = "\t") %>%
                filter(.[[1]] == "Total Sequences") %>%
                  pull() %>%
                    as.integer()
  raw_reads <- number_raw_R1 + number_raw_R2
  trimmed <- number_trimmed_R1 + number_trimmed_R2
  mapped_host_db <- read.csv(paste0("02_HostMapping/", sample, "_flagstat.tsv"), sep = "\t") %>%
                      filter(.[[3]] == "with itself and mate mapped") %>%
                        pull(1) %>%
                          as.integer()
  unmapped_host_db <- trimmed - mapped_host_db
  mapped_mic_db <- read.csv(paste0("04_MicrobiomeMappingDirect/", sample, "_flagstat.tsv"), sep = "\t") %>%
                      filter(.[[3]] == "with itself and mate mapped") %>%
                        pull(1) %>%
                          as.integer()
  unmapped_mic_db <- trimmed - mapped_mic_db
  mapped_mic_db_host_filtered <- read.csv(paste0("03_MicrobiomeMapping/", sample, "_flagstat.tsv"), sep = "\t") %>%
                      filter(.[[3]] == "with itself and mate mapped") %>%
                        pull(1) %>%
                          as.integer()
  unmapped_sequential <- unmapped_host_db - mapped_mic_db_host_filtered
  values_to_bind <- c(sample, as.integer(c(raw_reads, trimmed, mapped_host_db, unmapped_host_db, mapped_mic_db, unmapped_mic_db, mapped_mic_db_host_filtered, unmapped_sequential)))
  df_reads <- rbind(df_reads, values_to_bind)
}
# parse this later
# read.csv(paste0("02_HostMapping/", sample, "_coverage.tsv"), sep = "\t")
df_colnames <- c("Sample", "Raw", "Trimmed", "Mapped_host", "Unmapped_host", "Mapped_microbiome", "Unmapped_microbiome", "Mapped_microbiome_filtered", "Unmapped_filtered")
colnames(df_reads) <- df_colnames
df_reads <- df_reads %>%
              mutate(across(!c("Sample"), as.integer))
df_meta <- read.csv("Metadata_211018_Medgenome_india_samples.csv", sep = ',')
colnames(df_meta)[which(colnames(df_meta) == "ID")] <- "Sample"
df_meta$SpeciesID <- recode(df_meta$SpeciesID, "Am" = "Apis mellifera", "Ac" = "Apis cerana", "Af" = "Apis florea", "Ad" = "Apis dorsata")
df_meta <- df_meta %>%
        arrange(match(Sample, samples))
df_meta %>% group_by(SpeciesID) %>% tally()
df_meta %>% group_by(SpeciesID, Country) %>% tally()
df_meta %>% group_by(SpeciesID, Country, Colony) %>% tally()
df_plot_reads <- pivot_longer(df_reads, !Sample, values_to = "Number", names_to = "Type") %>%
                  merge(select(df_meta, Sample, SpeciesID), by="Sample")
df_plot_reads$Number <- as.integer(df_plot_reads$Number)
```

## Total number of reads before and after trimming

```{r plots_total_species}
Total_reads <- ggplot(filter(df_plot_reads, Type %in% c("Raw", "Trimmed")), aes(y=factor(Sample, levels = samples), x=Number, fill = Type)) +
                        geom_bar(stat="identity", position = "dodge") +
                          # ggtitle("Total reads per sample") +
                            ylab("Sample") +
                            xlab("Number of reads (paired end)") +
                            geom_hline(yintercept = 5.5, linetype="solid") +
                            geom_hline(yintercept = 20.5, linetype="solid") +
                            geom_hline(yintercept = 35.5, linetype="solid") +
                            geom_vline(xintercept = 50e+6, linetype="dotted") +
                              make_theme(theme_name=theme_few(), leg_pos="right",
                                         x_angle=0 ,x_vj=0, x_hj=0, x_size=12,
                                         y_angle=0 ,y_vj=0, y_hj=0, y_size=7) +
                                scale_x_continuous(labels=unit_format(unit = "M", scale = 1e-6))
                                  ggsave("Figures/00a-Total_reads_trimming.pdf")
```

```{r show_plots_total_species, dev = 'pdf', results='hold', fig.show = 'hold', out.width = '100%', fig.align = 'center', fig.cap = 'Total reads by species'}
Total_reads
# knitr::include_graphics("Figures/Total_reads_species.pdf")
```

## Total number of reads per species after trimming

```{r plots_total_species}
Total_reads_species <- ggplot(filter(df_plot_reads, Type %in% c("Trimmed")), aes(y=factor(Sample, levels = samples), x=Number, fill = SpeciesID)) +
                        geom_bar(stat="identity", position = "dodge") +
                          # ggtitle("Total reads per sample") +
                            ylab("Sample") +
                            xlab("Number of reads (paired end)") +
                            geom_hline(yintercept = 5.5, linetype="solid") +
                            geom_hline(yintercept = 20.5, linetype="solid") +
                            geom_hline(yintercept = 35.5, linetype="solid") +
                              make_theme(theme_name=theme_few(), leg_pos="right",
                                         setFill = F,
                                         x_angle=0 ,x_vj=0, x_hj=0, x_size=12,
                                         y_angle=0 ,y_vj=0, y_hj=0, y_size=7) +
                                scale_x_continuous(labels=unit_format(unit = "M", scale = 1e-6)) +
                                scale_fill_manual(values=host_order_color)
                                  ggsave("Figures/00b-Total_reads_species_after_trimming.pdf")
```

```{r show_plots_total_species, dev = 'pdf', results='hold', fig.show = 'hold', out.width = '100%', fig.align = 'center', fig.cap = 'Total reads by species'}
Total_reads_species
# knitr::include_graphics("Figures/Total_reads_species.pdf")
```

## Proportion of reads mapping to host and microbiome database

```{r plots_num_mapped_mic}
df_plot_reads_prop <- select(df_reads, Sample, Trimmed, Mapped_host, Mapped_microbiome_filtered, Unmapped_filtered) %>%
  summarise(Sample, "None" = Unmapped_filtered/Trimmed*100,
            "Host" = Mapped_host/Trimmed*100,
            "Microbiome" = Mapped_microbiome_filtered/Trimmed*100) %>%
              pivot_longer(!Sample, names_to = "Type", values_to = "Number")
Mapped_Unmapped_reads_prop <- ggplot(df_plot_reads_prop, aes(y=factor(Sample, levels = samples),
                                                            x=Number,
                                                            fill=factor(Type, levels = c("None", "Host", "Microbiome")))) +
                        geom_bar(stat="identity", position = "stack") +
                          # ggtitle("Total reads per sample") +
                            labs(y = "Sample",
                                 x = "Percentage of reads (paired end)",
                                 fill = "Mapped to") +
                            geom_hline(yintercept = 5.5, linetype="solid") +
                            geom_hline(yintercept = 20.5, linetype="solid") +
                            geom_hline(yintercept = 35.5, linetype="solid") +
                              make_theme(theme_name=theme_few(), leg_pos="right",
                                         guide_nrow = 3,
                                         x_angle=0 ,x_vj=0, x_hj=0, x_size=12,
                                         y_angle=0 ,y_vj=0, y_hj=0, y_size=7)
                                      ggsave("Figures/00c-Mapped_Unmapped_reads_prop.pdf")
```

```{r show_plots_num_mapped_mic, dev = 'pdf', results='hold', fig.show = 'hold', out.width = '100%', fig.align = 'center', fig.cap = 'Proportion of reads mapped to the microbiome database and host database'}
Mapped_Unmapped_reads_prop
# knitr::include_graphics("Figures/Mapped_Unmapped_reads_prop.pdf")
```

## Micorbiome reads lost by non_specific mapping to host

```{r plots_prop_mapped_mic}
df_plot_reads_non_specific <- df_reads %>%
  mutate(Unmapped_microbiome_filtered = Mapped_host + Unmapped_filtered) %>%
    select(Sample, Mapped_microbiome, Unmapped_microbiome, Mapped_microbiome_filtered, Unmapped_microbiome_filtered) %>%
              pivot_longer(!Sample, names_to = "Type", values_to = "Number") %>%
                mutate(Host_filtered = ifelse(Type %in% c("Mapped_microbiome", "Unmapped_microbiome"), "Direct mapping", "Host filtered")) %>%
                  mutate(Type = ifelse(Type %in% c("Mapped_microbiome", "Mapped_microbiome_filtered"), "Mapped", "Unmapped"))


Non_specific_reads <- ggplot(df_plot_reads_non_specific, aes(y=interaction(Host_filtered, factor(Sample, levels = samples)),
                                                            x=Number,
                                                            fill=factor(Type))) +
                        geom_bar(stat="identity", position = "stack") +
                          # ggtitle("Total reads per sample") +
                            labs(y = "Sample",
                                 x = "Percentage of reads (paired end)",
                                 fill = "Mapped to") +
                            geom_hline(yintercept = 11, linetype="solid") +
                            geom_hline(yintercept = 41, linetype="solid") +
                            geom_hline(yintercept = 71, linetype="solid") +
                              # facet_wrap(~Host_filtered) +
                              scale_x_continuous(labels=unit_format(unit = "M", scale = 1e-6)) +
                              make_theme(theme_name=theme_few(), leg_pos="right",
                                         x_angle=0 ,x_vj=0, x_hj=0, x_size=12,
                                         y_angle=0 ,y_vj=0, y_hj=1, y_size=5)
                                      ggsave("Figures/00d-Mapping_non_specific.pdf")
```

```{r show_plots_prop_mapped_mic, dev = 'pdf', results='hold', fig.show = 'hold', out.width = '100%', fig.align = 'center', fig.cap = 'Proportion of reads mapped to the microbiome database and host database'}
Non_specific_reads
# knitr::include_graphics("Figures/Mapped_Unmapped_reads_prop.pdf")
```

## Community profiling with mOTUs

```{r motus_summary}
df_motus_raw <- read.csv("08_motus_profile/samples_merged.motus", sep = "\t", skip = 2, stringsAsFactors=FALSE)
colnames(df_motus_raw)[1] <- "taxonomy"
df_motus_raw <- df_motus_raw %>%
              mutate(across(!c("taxonomy"), as.numeric)) %>%
              mutate(sum_ab = rowSums(across(where(is.numeric)))) %>%
                filter(sum_ab > 0) %>%
                  select(!sum_ab) %>%
                    column_to_rownames("taxonomy")

df_motus <- as.data.frame(t(df_motus_raw)) %>%
              rownames_to_column("Sample") %>%
              pivot_longer(!Sample, names_to = "motu", values_to = "rel_ab") %>%
                group_by(Sample, motu) %>%
                  mutate(Present = ifelse(rel_ab > 0, 1, 0)) %>%
                    group_by(motu) %>%
                     mutate(Prevalence_num = sum(Present)) %>%
                      mutate(Prevalence = mean(Present))

condense_motu <- function(motu){
  motu_condensed = strsplit(motu, " ")[[1]][1]
  return(motu_condensed)
}

df_motus_combined <- left_join(df_motus, df_meta)  %>%
                      group_by(SpeciesID, motu) %>%
                        mutate(Present_host = ifelse(rel_ab > 0, 1, 0)) %>%
                          group_by(SpeciesID, motu) %>%
                            mutate(Prevalence_num_host = sum(Present_host)) %>%
                            mutate(Prevalence_host = mean(Present_host)) %>%
                              mutate(mean_rel_ab_host = mean(rel_ab)) %>%
                              group_by(Sample) %>%
                              mutate(mean_rel_ab = mean(rel_ab)) %>%
                                mutate(motu_condensed = Vectorize(condense_motu)(motu))

motu_list <- df_motus_combined %>%
              pull(motu) %>% unique

high_motu_list <- df_motus_combined %>%
                        filter(Prevalence_host >= 0.5) %>%
                          pull(motu_condensed) %>% unique

df_assigned_plot <- df_motus_combined %>%
                      group_by(Sample) %>%
                        mutate(sum = sum(rel_ab)) %>%
                          mutate(unassigned = rel_ab[motu == "unassigned"]) %>%
                            mutate("assigned" = sum - unassigned) %>%
                              select(Sample, assigned, unassigned) %>%
                                pivot_longer(!Sample, values_to = "proportion", names_to = "Type")

assigned_plot <- ggplot(df_assigned_plot, aes(y = factor(Sample, samples), x = proportion, fill = factor(Type, levels = c("unassigned", "assigned")))) +
                  geom_bar(position = "stack", stat = "identity") +
                  labs(fill = "Type", x = "Proportion", y = "Sample") +
                    make_theme(leg_pos = "right", guide_nrow = 20, leg_size = 7,
                               y_size = 8, y_hj = 1, y_vj = 0.5
                    )
                    # ggsave("Figures/04-motus_unassigned.pdf")

extend_colors_motus <- function(names_vec){
  final_list <- list()
  for (a_name in names_vec) {
    if (a_name %in% names(motuColors)) {
      final_list[a_name] = motuColors[a_name]
    } else {
      final_list[a_name] = "grey"
    }
  }
  return(final_list)
}

plot_motus_high_prev <- ggplot(df_motus_combined, aes(y = factor(Sample, samples), x = rel_ab, fill = factor(motu_condensed, motus))) +
                geom_bar(position = "stack", stat = "identity") +
                labs(fill = "mOTU", x = "mOTUs2 Relative abundance", y = "Sample") +
                  make_theme(max_colors = length(unique(motus)),
                             setFill = F,
                             leg_pos = "right",
                             guide_nrow = 16,
                             leg_size = 7,
                             y_size = 8, y_hj = 1
                  ) +
                  scale_fill_manual(values=motuColors)

df_motus_filt <- filter(df_motus_combined, Prevalence_num >= 1 & rel_ab > 0.01)
plot_motus_filt <- ggplot(df_motus_filt, aes(y = factor(Sample, samples), x = rel_ab, fill = factor(motu_condensed))) +
                geom_bar(position = "stack", stat = "identity") +
                labs(fill = "mOTU", x = "mOTUs2 Relative abundance", y = "Sample") +
                  make_theme(max_colors = length(unique(df_motus_filt$motu_condensed)),
                             palettefill = "Set1",
                             leg_pos = "right",
                             guide_nrow = 20,
                             leg_size = 7,
                             y_size = 8, y_hj = 1,
                  )
                  ggsave("Figures/04b-motus_filt.pdf")
```

```{r motus_summary_plots,  dev = 'pdf', results='hold', fig.show = 'hold', out.width = '100%', fig.align = 'center', fig.cap = 'mOTUs Summary'}
g <- grid.arrange(arrangeGrob(assigned_plot, ncol = 2, widths = c(4, 2)), plot_motus_high_prev, nrow = 2, heights = c(1.2, 2))
  ggsave("Figures/04a-motus.pdf", g)
g
plot_motus_filt
```

# MAG analysis

```{r more_imports}
# setwd("/Volumes/Storage/Work/Temp-From-NAS/cross-species-analysis-india")
df_evaluate <- read.csv("06_MAG_binning/all_genomes.csv", sep = "\t")
df_gtdbk_bac <- read.csv("06_MAG_binning/gtdbtk_out_dir/classify/gtdbtk.bac120.summary.tsv", sep = "\t")
drep_Bdb <- read.csv("06_MAG_binning/drep_results/data_tables/Bdb.csv", sep = ",")
drep_Cdb <- read.csv("06_MAG_binning/drep_results/data_tables/Cdb.csv", sep = ",")
# drep_Mdb <- read.csv("06_MAG_binning/drep_results/data_tables/Mdb.csv", sep = ",")
# drep_Ndb <- read.csv("06_MAG_binning/drep_results/data_tables/Ndb.csv", sep = ",")
# drep_Sdb <- read.csv("06_MAG_binning/drep_results/data_tables/Sdb.csv", sep = ",")
# drep_Wdb <- read.csv("06_MAG_binning/drep_results/data_tables/Wdb.csv", sep = ",")
# drep_Widb <- read.csv("06_MAG_binning/drep_results/data_tables/Widb.csv", sep = ",")
drep_gInfo <- read.csv("06_MAG_binning/drep_results/data_tables/genomeInfo.csv", sep = ",")
drep_gInformation <- read.csv("06_MAG_binning/drep_results/data_tables/genomeInformation.csv", sep = ",")
df_assembly <- read.csv("05_Assembly/host_unmapped/check_assembly/Assembly_mapping_summary.csv", sep = ',')
df_assembly <- merge(df_assembly, df_meta, by="Sample")
df_assembly$SpeciesID <- recode(df_assembly$SpeciesID, "Am" = "Apis mellifera", "Ac" = "Apis cerana", "Af" = "Apis florea", "Ad" = "Apis dorsata", .default = "Apis")
```

```{r mag_summary_stats}
phy_group_dict = c("firm4" = 'g__Bombilactobacillus',
            "g__Bombilactobacillus_outgroup" = 'g__Bombilactobacillus',
            "firm5" = 'g__Lactobacillus',
            "lacto" = 'g__Lactobacillus',
            "g__Lactobacillus_outgroup" = 'g__Lactobacillus',
            "bifido" = 'g__Bifidobacterium',
            "g__Bifidobacterium_outgroup" = 'g__Bifidobacterium',
            "gilli" = 'g__Gilliamella',
            "entero" = 'g__Gilliamella',
            "g__Gilliamella_outgroup" = 'g__Gilliamella',
            "fper" = 'g__Frischella',
            "g__Frischella_outgroup" = 'g__Frischella',
            "snod" = 'g__Snodgrassella',
            "g__Snodgrassella_outgroup" = 'g__Snodgrassella',
            "bapis" = 'g__Bartonella',
            "g__Bartonella_outgroup" = 'g__Bartonella',
            # "" = 'g__Enterobacter',
            "g__Enterobacter_outgroup" = 'g__Enterobacter',
            # "" = 'g__',
            # "" = 'g__Pectinatus',
            "g__Pectinatus_outgroup" = 'g__Pectinatus',
            "api" = 'g__Apibacter',
            "g__Apibacter_outgroup" = 'g__Apibacter',
            # "" = 'g__Dysgonomonas',
            "g__Dysgonomonas_outgroup" = 'g__Dysgonomonas',
            # "" = 'g__Spiroplasma',
            "g__Spiroplasma_outgroup" = 'g__Spiroplasma',
            # "" = 'g__Zymobacter',
            "g__Zymobacter_outgroup" = 'g__Zymobacter',
            # "" = 'g__Entomomonas',
            "g__Entomomonas_outgroup" = 'g__Entomomonas',
            # "" = 'g__Saezia',
            "g__Saezia_outgroup" = 'g__Saezia',
            # "" = 'g__Parolsenella',
            "g__Parolsenella_outgroup" = 'g__Parolsenella',
            # "" = 'g__WRHT01',
            "g__WRHT01_outgroup" = 'g__WRHT01',
            "com" = 'g__Commensalibacter',
            "g__Commensalibacter_outgroup" = 'g__Commensalibacter',
            "lkun" = 'g__Apilactobacillus',
            "g__Apilactobacillus_outgroup" = 'g__Apilactobacillus',
            "bom" = 'g__Bombella',
            "g__Bombella_outgroup" = 'g__Bombella'
          )
get_group_phy <- function(phy){
  return(c(phy_group_dict[phy][[1]]))
}

MAG_taxonomy_info <- read.csv("06_MAG_binning/gtdbtk_out_dir/classify/gtdbtk.bac120.summary.tsv", sep = "\t")
MAG_info <- read.csv("06_MAG_binning/all_genomes.csv", sep = "\t")
representative_MAGs <- read.csv("06_MAG_binning/all_cluster_rep_genomes.csv", sep = ",", header = F)[ ,1]
# includes outgroups now and updated SDP values -
# check directory /Volumes/Storage/Work/Temp-From-NAS/220518-GenomesForPhylogenies
isolates <- read.csv("IsolateGenomeInfo.csv")
# isolates <- read.csv("all_combined.csv")
# isolates <- isolates %>%
#               filter(DB == "KE_2021_expandedGBR")
MAG_clusters_info <- read.csv("06_MAG_binning/drep_results/data_tables/Cdb.csv")
format_name <- function(genome){
  MAG = strsplit(genome, ".fa")[[1]]
  return(MAG)
}
MAG_clusters_info <- MAG_clusters_info %>% mutate(genome = Vectorize(format_name)(genome))
clusters <- MAG_clusters_info %>%
              select(genome, secondary_cluster)
genomes_info <- MAG_info %>%
                  select(Bin.Id, Completeness, Contamination)
colnames(genomes_info) = c("Genome", "Completeness", "Contamination")
taxonomy <- MAG_taxonomy_info %>%
              select(user_genome, classification) %>%
                separate(classification, c("domain","phylum","class","order","family","genus","species"), sep = ";")

MAGs_collated <- left_join(clusters, taxonomy, by = c("genome"="user_genome"))
MAGs_collated <- left_join(genomes_info, MAGs_collated, by = c("Genome"="genome"))

MAGs_collated_high <- MAGs_collated %>%
                        filter(Completeness > 95, Contamination < 5)

final_genome_info <- data.frame("ID" = isolates$Locus_tag,
                                 "Accession" = isolates$Accession,
                                 "Locus_tag" = isolates$Locus_tag,
                                 "Strain_name" = isolates$Strain_name,
                                 "Phylotype" = isolates$Phylotype,
                                 "SDP" = isolates$SDP,
                                 "Species" = isolates$Species,
                                 "Host" = isolates$Host,
                                 "Study" = isolates$Study,
                                 "Origin" = isolates$Origin,
                                 "Source_database" = isolates$Source_database,
                                 "Cluster" = isolates$SDP,
                                 "Group" = isolates$Group,
                                 "Genus" = rep(NA, length(isolates$Locus_tag)),
                                 "Family" = rep(NA, length(isolates$Locus_tag)),
                                 "Order" = rep(NA, length(isolates$Locus_tag)),
                                 "Class" = rep(NA, length(isolates$Locus_tag)),
                                 "Sample" = rep(NA, length(isolates$Locus_tag)),
                                 "Group_auto" = rep("EMPTY", length(isolates$Locus_tag)))


final_genome_info <- final_genome_info %>%
                      mutate("Group_auto" = Vectorize(get_group_phy)(Phylotype))
final_genome_info$Group_auto <- as.character(final_genome_info$Group_auto)

MAGs_collated_high <- data.frame("ID" = MAGs_collated_high$Genome,
                                 "Accession" = rep(NA, length(MAGs_collated_high$Genome)),
                                 "Locus_tag" = rep(NA, length(MAGs_collated_high$Genome)),
                                 "Strain_name" = MAGs_collated_high$Genome,
                                 "Phylotype" = rep(NA, length(MAGs_collated_high$Genome)),
                                 "SDP" = rep(NA, length(MAGs_collated_high$Genome)),
                                 "Species" = MAGs_collated_high$species,
                                 "Host" = rep("EMPTY", length(MAGs_collated_high$Genome)),
                                 "Study" = rep(NA, length(MAGs_collated_high$Genome)),
                                 "Origin" = rep("EMPTY", length(MAGs_collated_high$Genome)),
                                 "Source_database" = rep("MAGs", length(MAGs_collated_high$Genome)),
                                 "Cluster" = MAGs_collated_high$secondary_cluster,
                                 "Group" = rep("EMPTY", length(MAGs_collated_high$Genome)),
                                 "Genus" = MAGs_collated_high$genus,
                                 "Family" = MAGs_collated_high$family,
                                 "Order" = MAGs_collated_high$order,
                                 "Class" = MAGs_collated_high$class,
                                 "Sample" = rep("EMPTY", length(MAGs_collated_high$Genome)))
MAGs_collated <- data.frame("ID" = MAGs_collated$Genome,
                                 "Accession" = rep(NA, length(MAGs_collated$Genome)),
                                 "Locus_tag" = rep(NA, length(MAGs_collated$Genome)),
                                 "Strain_name" = MAGs_collated$Genome,
                                 "Phylotype" = rep(NA, length(MAGs_collated$Genome)),
                                 "SDP" = rep(NA, length(MAGs_collated$Genome)),
                                 "Species" = MAGs_collated$species,
                                 "Host" = rep("EMPTY", length(MAGs_collated$Genome)),
                                 "Study" = rep(NA, length(MAGs_collated$Genome)),
                                 "Origin" = rep("EMPTY", length(MAGs_collated$Genome)),
                                 "Source_database" = rep("MAGs", length(MAGs_collated$Genome)),
                                 "Cluster" = MAGs_collated$secondary_cluster,
                                 "Group" = rep("EMPTY", length(MAGs_collated$Genome)),
                                 "Genus" = MAGs_collated$genus,
                                 "Family" = MAGs_collated$family,
                                 "Order" = MAGs_collated$order,
                                 "Class" = MAGs_collated$class,
                                 "Sample" = rep("EMPTY", length(MAGs_collated$Genome)))

MAGs_collated <- MAGs_collated %>%
  mutate(Group_auto = Family) %>%
    mutate(Host = Vectorize(get_host_name)(ID)) %>%
      mutate(Origin = Vectorize(get_origin_name)(ID)) %>%
        mutate(Sample = Vectorize(get_sample_name)(ID))

MAGs_collated_high <- MAGs_collated_high %>%
  mutate("Group_auto" = Family) %>%
    mutate("Host" = Vectorize(get_host_name)(ID)) %>%
      mutate(Origin = Vectorize(get_origin_name)(ID)) %>%
        mutate(Sample = Vectorize(get_sample_name)(ID))

MAGs_representative <- MAGs_collated %>%
                        filter(ID %in% representative_MAGs)

# make sure that number per cluster is 1 for all
MAGs_collated_info <- left_join(MAGs_collated, mutate(drep_gInformation, genome = Vectorize(format_name)(genome)), by = c("ID"="genome"))
# Number of MAGs coming from each host species
MAGs_collated_high %>%
  mutate(host = Vectorize(get_host_name)(ID)) %>%
    pull(host) %>%
      table()
# Number of MAGs coming from each sample
MAGs_collated_high %>%
  mutate(sample = Vectorize(get_sample_name)(ID)) %>%
    pull(sample) %>%
      table()


get_sdp <- function(cluster){
  if (is.na(clusters_sdp[cluster])) {
    return(cluster)
  } else{
    return(clusters_sdp[cluster])
  }
}

vis_magOTUs_df_all <- MAGs_collated_info %>%
                        group_by(Sample) %>%
                            mutate(all_quality = ifelse(completeness > 70 & contamination < 5 & N50 > 10000, "Pass", "Fail")) %>%
                            mutate(Completeness_quality = cut(completeness ,breaks=c(-1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100, 110),
                                                            labels = c("<10", "10-20", "20-30", "30-40", "40-50", "50-60", "60-70", "70-80", "80-90", "90-95", "95-100", "100"))
                                                          ) %>%
                              mutate(Contamination_quality = cut(contamination ,breaks=c(-1, 0, 5, 10, 100),
                                                              labels = c("0", "0-5", "5-10", ">10"))
                                                          ) %>%
                              mutate(N50_quality = cut(N50 ,breaks=c(0, 10000, 50000, 100000, 200000, 500000, 1000000, 2000000, Inf), labels = c("<10Kb", "10-50Kb", "50-100Kb", "100-200Kb", "200-500Kb", "0.5-1Mb", "1-2Mb", ">2Mb"))) %>%
                                mutate(sample = Vectorize(get_sample_name)(ID)) %>%
                                  mutate(Host = Vectorize(get_host_name)(ID)) # %>%
                                    # mutate(num_contigs = Vectorize(get_num_contigs_per_bin)(ID))

samples_am <- c(vis_magOTUs_df_all %>% filter(Host == "Apis mellifera") %>% pull(Sample) %>% unique %>% as.vector)
samples_ac <- c(vis_magOTUs_df_all %>% filter(Host == "Apis cerana") %>% pull(Sample) %>% unique %>% as.vector)
samples_ad <-c(vis_magOTUs_df_all %>% filter(Host == "Apis dorsata") %>% pull(Sample) %>% unique %>% as.vector)
samples_af <-c(vis_magOTUs_df_all %>% filter(Host == "Apis florea") %>% pull(Sample) %>% unique %>% as.vector)
contig_fates_df_am <- data.frame()
for (sample in samples_am) {
  contig_fates_df_am <- rbind(contig_fates_df_am, read.csv(paste0("06_MAG_binning/contig_fates/",sample,"_contig_fates.csv"), sep = ","))
}
contig_fates_df_am <- cbind(contig_fates_df_am, host = rep("Apis mellifera", dim(contig_fates_df_am)[[1]]))
contig_fates_df_am_pf <- contig_fates_df_am %>%
                              group_by(sample, passed_filter) %>%
                                summarise(pass_fail_length = sum(length), pf_num = n(), .groups = "keep")
contig_fates_df_am_bin <- contig_fates_df_am %>%
                              group_by(sample, binned) %>%
                                summarise(binned_length = sum(length), binned_num = n(), .groups = "keep")


contig_fates_df_ac <- data.frame()
for (sample in samples_ac) {
  contig_fates_df_ac <- rbind(contig_fates_df_ac, read.csv(paste0("06_MAG_binning/contig_fates/",sample,"_contig_fates.csv"), sep = ","))
}
contig_fates_df_ac <- cbind(contig_fates_df_ac, host = rep("Apis cerana", dim(contig_fates_df_ac)[[1]]))
contig_fates_df_ac_pf <- contig_fates_df_ac %>%
                              group_by(sample, passed_filter) %>%
                                summarise(pass_fail_length = sum(length), pf_num = n(), .groups = "keep")
contig_fates_df_ac_bin <- contig_fates_df_ac %>%
                              group_by(sample, binned) %>%
                                summarise(binned_length = sum(length), binned_num = n(), .groups = "keep")

contig_fates_df_ad <- data.frame()
for (sample in samples_ad) {
  contig_fates_df_ad <- rbind(contig_fates_df_ad, read.csv(paste0("06_MAG_binning/contig_fates/",sample,"_contig_fates.csv"), sep = ","))
}
contig_fates_df_ad <- cbind(contig_fates_df_ad, host = rep("Apis dorsata", dim(contig_fates_df_ad)[[1]]))
contig_fates_df_ad_pf <- contig_fates_df_ad %>%
                              group_by(sample, passed_filter) %>%
                                summarise(pass_fail_length = sum(length), pf_num = n(), .groups = "keep")
contig_fates_df_ad_bin <- contig_fates_df_ad %>%
                              group_by(sample, binned) %>%
                                summarise(binned_length = sum(length), binned_num = n(), .groups = "keep")

contig_fates_df_af <- data.frame()
for (sample in samples_af) {
  contig_fates_df_af <- rbind(contig_fates_df_af, read.csv(paste0("06_MAG_binning/contig_fates/",sample,"_contig_fates.csv"), sep = ","))
}
contig_fates_df_af <- cbind(contig_fates_df_af, host = rep("Apis florea", dim(contig_fates_df_af)[[1]]))
contig_fates_df_af_pf <- contig_fates_df_af %>%
                              group_by(sample, passed_filter) %>%
                                summarise(pass_fail_length = sum(length), pf_num = n(), .groups = "keep")
contig_fates_df_af_bin <- contig_fates_df_af %>%
                              group_by(sample, binned) %>%
                                summarise(binned_length = sum(length), binned_num = n(), .groups = "keep")

contigs_length_df <- rbind(
                        summarise(group_by(contig_fates_df_am, sample), contig = contig_name, length = length, binned = binned, bin = bin_name, passed = passed_filter, .groups = "drop"),
                        summarise(group_by(contig_fates_df_ac, sample), contig = contig_name, length = length, binned = binned, bin = bin_name, passed = passed_filter, .groups = "drop"),
                        summarise(group_by(contig_fates_df_ad, sample), contig = contig_name, length = length, binned = binned, bin = bin_name, passed = passed_filter, .groups = "drop"),
                        summarise(group_by(contig_fates_df_af, sample), contig = contig_name, length = length, binned = binned, bin = bin_name, passed = passed_filter, .groups = "drop")
                  )

length_bin_sum_df <- contigs_length_df %>%
                    mutate(length_bin = cut(length ,breaks=c(0, 500, 1000, 10000, 50000, 100000, 200000, 500000, 1000000, Inf), labels = c("500", "0.5-1kb", "1-10Kb", "10-50Kb", "50-100Kb", "100-200Kb", "200-500Kb", "0.5-1Mb", ">1Mb"))) %>%
                      group_by(sample, binned, length_bin) %>%
                        summarise(length_bin_sum = sum(length), num_contigs = n())
length_bin_sum_df_passed <- contigs_length_df %>%
                    filter(passed == "P") %>%
                    mutate(length_bin = cut(length ,breaks=c(0, 500, 1000, 10000, 50000, 100000, 200000, 500000, 1000000, Inf), labels = c("500", "0.5-1kb", "1-10Kb", "10-50Kb", "50-100Kb", "100-200Kb", "200-500Kb", "0.5-1Mb", ">1Mb"))) %>%
                      group_by(sample, binned, length_bin) %>%
                        summarise(length_bin_sum = sum(length), num_contigs = n())

all_depths <- data.frame()
for (sample in samples) {
  sample_contig_depths <- read.csv(paste0("06_MAG_binning/backmapping/",sample,"/",sample,"_mapped_to_",sample,".depth"), sep = "\t")
  depth_column <- paste0(sample,"_mapped_to_",sample,".bam")
  all_depths <- rbind(all_depths, rename(select(sample_contig_depths, contigName, all_of(depth_column)), depth = depth_column))
}
contigs_depths_df <- left_join(filter(contigs_length_df, passed == "P"), all_depths, by = c("contig" = "contigName"))

vis_magOTUs_df_all <- vis_magOTUs_df_all %>%
                          group_by(Cluster) %>%
                            mutate(Num_mags = n()) %>%
                              mutate(Prevalence_overall = Num_mags/length(samples))

vis_magOTUs_df_all <- vis_magOTUs_df_all %>%
                          group_by(Cluster, Host) %>%
                            mutate(Present = n()) %>%
                            mutate(Prevalence = ifelse(Host=="Apis mellifera", Present/9, NA)) %>%
                            mutate(Prevalence = ifelse(Host=="Apis cerana", Present/17, Prevalence)) %>%
                            mutate(Prevalence = ifelse(Host=="Apis florea", Present/15, Prevalence)) %>%
                            mutate(Prevalence = ifelse(Host=="Apis dorsata", Present/15, Prevalence)) %>%
                              left_join(summarise(group_by(contigs_depths_df, bin), mean_coverage = mean(depth), .groups = "drop"), by = c("ID" = "bin")) %>%
                                arrange(Genus)

vis_magOTUs_df <- vis_magOTUs_df_all %>%
                    filter(all_quality == "Pass")


vis_magOTUs_df$Host <- as.factor(recode(vis_magOTUs_df$Host, Am="Apis mellifera", Ac="Apis cerana", Ad="Apis dorsata", Af="Apis florea"))
vis_magOTUs_df$Cluster <- as.factor(vis_magOTUs_df$Cluster)
vis_magOTUs_df$sample <- as.factor(vis_magOTUs_df$sample)
vis_magOTUs_df$Family <- as.factor(vis_magOTUs_df$Family)
vis_magOTUs_df$Genus <- as.factor(vis_magOTUs_df$Genus)
vis_magOTUs_df <- vis_magOTUs_df[order(vis_magOTUs_df$Genus), ]
MAGs_collated_info_plot
vis_magOTUs_df_all
```

## Mapping to Assembly

The host-filtered reads were assembled. The proportion of reads that mapped back to the assembly and some information about the assemblies such as assembly size, and information about contigs are shown below.

```{r Assembly_mapping_summary}
assembly_sizes <- ggplot(df_assembly, aes(y = factor(Sample, levels=samples), x = Assembly.size, fill = factor(SpeciesID, host_order))) +
                    geom_bar(stat = "identity") +
                    geom_vline(xintercept = 2000000) +
                      labs(x = "Total Assembly Size", y = "Sample", fill = "Host Species") +
                        scale_x_continuous(labels=unit_format(unit = "M", scale = 1e-6)) +
                          make_theme(setFill = F, y_angle = 0, y_hj = 1, y_vj = 0, max_colors = length(unique(df_assembly$SpeciesID)), y_size = 7, guide_nrow = 1) +
                            scale_fill_manual(values=host_order_color)
                          # ggsave("Figures/03-AssemblySizes.pdf")

df_assembly_plot <- df_assembly %>%
  select(Sample, Number.of.reads, Number.mapped) %>%
    mutate(Number.unmapped = Number.of.reads - Number.mapped) %>%
    rename(Unmapped = Number.unmapped, Mapped = Number.mapped) %>%
     pivot_longer(cols = 3:4, names_to ="Type", values_to = "Number")

number_mapped_assembly <- ggplot(df_assembly, aes(y = factor(Sample, levels=samples), x = Number.mapped, fill = factor(SpeciesID, host_order))) +
                            geom_bar(stat = "identity") +
                            labs(x = "Number of reads mapped to assembly", y = "Sample", fill = "Type") +
                            scale_x_continuous(labels=unit_format(unit = "M", scale = 1e-6)) +
                              make_theme(setFill = F, x_angle = 60, x_hj = 1, x_vj = 1, max_colors = length(unique(df_assembly_plot$Type)), x_size = 7, guide_nrow = 1) +
                                scale_fill_manual(values=host_order_color)
                              # ggsave("Figures/03-NumberAssembled.pdf")

df_assembly_plot <- df_assembly %>%
  select(Sample, Number.of.reads, Number.mapped) %>%
    mutate(Number.unmapped = Number.of.reads - Number.mapped) %>%
    mutate(percent_mapped = Number.mapped/Number.of.reads*100) %>%
    mutate(percent_unmapped = Number.unmapped/Number.of.reads*100) %>%
    rename(Unmapped = percent_unmapped, Mapped = percent_mapped, Unmapped_number = Number.unmapped, Mapped_number = Number.mapped) %>%
    select(Sample, Mapped, Unmapped) %>%
     pivot_longer(cols = 2:3, names_to ="Type", values_to = "Percent")

df_assembly_plot_number <- df_assembly %>%
  select(Sample, Number.of.reads, Number.mapped) %>%
    mutate(Number.unmapped = Number.of.reads - Number.mapped) %>%
    mutate(percent_mapped = Number.mapped/Number.of.reads*100) %>%
    mutate(percent_unmapped = Number.unmapped/Number.of.reads*100) %>%
    rename(Unmapped = Number.unmapped, Mapped = Number.mapped) %>%
    select(Sample, Mapped, Unmapped) %>%
     pivot_longer(cols = 2:3, names_to ="Type", values_to = "Number")

number_mapped_assembly <- ggplot(df_assembly_plot_number, aes(y = factor(Sample, levels=samples), x = Number, fill = factor(Type, levels = c("Unmapped", "Mapped")))) +
                            geom_bar(stat = "identity") +
                            labs(y = "Percentage of reads", x = "Sample", fill = "Type") +
                            scale_x_continuous(labels=unit_format(unit = "M", scale = 1e-6)) +
                              make_theme(x_angle = 60, x_hj = 1, x_vj = 1, max_colors = length(unique(df_assembly_plot$Type)), x_size = 7, guide_nrow = 1)
                              # ggsave("Figures/03-NumberMappedtoAssembly.pdf")

Number_contig_plot <- ggplot(df_assembly, aes(y = factor(Sample, levels=samples), x = Number.of.filtered.contigs, fill = factor(SpeciesID, levels = rev(host_order)))) +
                            geom_bar(stat = "identity") +
                            labs(y = "Sample", x = "Number of contigs", fill = "Host") +
                            scale_x_continuous(labels=unit_format(unit = "K", scale = 1e-4)) +
                            scale_fill_manual(values=host_order_color) +
                              make_theme(setFill = F, x_angle = 60, x_hj = 1, x_vj = 1, x_size = 10, guide_nrow = 1)
                              ggsave("Figures/03a-NumberOfFilteredcontigs.pdf")

percent_mapped_assembly <- ggplot(df_assembly_plot, aes(y = factor(Sample, levels=samples), x = Percent, fill = factor(Type, levels = c("Unmapped", "Mapped")))) +
                            geom_bar(stat = "identity") +
                            labs(y = "Percentage of reads", x = "Sample", fill = "Type") +
                              make_theme(x_angle = 60, x_hj = 1, x_vj = 1, max_colors = length(unique(df_assembly_plot$Type)), x_size = 7, guide_nrow = 1)
                              # ggsave("Figures/03-ProportionMappedtoAssembly.pdf")
Total_data_species <- ggplot(mutate(df, amount_data = Total..PE.reads.*2*150), aes(y=factor(Sample, levels = samples),
                                      x=amount_data,
                                      fill = SpeciesID)) +
                        geom_bar(stat="identity") +
                            ylab("Sample") +
                            xlab("Number of reads (paired end)") +
                              make_theme(setFill=F, leg_pos = "none") +
                                scale_x_continuous(labels=unit_format(unit = "G", scale = 1e-9)) +
                                scale_fill_manual(values=host_order_color)
```

```{r Assembly_plots,  dev = 'pdf', results='hold', fig.show = 'hold', out.width = '100%', fig.align = 'center'}
Total_reads_species_temp <- ggplot(df, aes(y=factor(Sample, levels = samples),
                                      x=Total..PE.reads.,
                                      fill = SpeciesID)) +
                        geom_bar(stat="identity") +
                          # ggtitle("Total reads per sample") +
                            ylab("Sample") +
                            xlab("Number of reads (paired end)") +
                              make_theme(setFill=F) +
                                scale_x_continuous(labels=unit_format(unit = "M", scale = 1e-6)) +
                                scale_fill_manual(values=host_order_color)
g <- grid.arrange(
      arrangeGrob(
        assembly_sizes + make_theme(setFill = F, setCol = F, leg_size = 7, y_size = 5, y_hj = 1, y_vj = 1, x_size = 8, guide_nrow = 1, leg_pos = "none"),
        number_mapped_assembly + make_theme(setFill = F, setCol = F, leg_size = 7, y_size = 5, y_hj = 1, y_vj = 1, x_size = 8, guide_nrow = 1, leg_pos = "none"),
        nrow = 1
      ),
      get_only_legend(assembly_sizes),
      arrangeGrob(
        Total_data_species + make_theme(setFill = F, setCol = F, leg_size = 7, y_size = 5, y_hj = 1, y_vj = 1, x_size = 8, guide_nrow = 2, leg_pos = "none"),
        Total_reads_species_temp + make_theme(setFill = F, setCol = F, leg_size = 7, y_size = 5, y_hj = 1, y_vj = 1, x_size = 8, guide_nrow = 1, leg_pos = "none"),
        nrow = 1
      ),
      nrow = 3, heights = c(8,1,8)
 )
 g
 ggsave("Figures/03b-Assembly_summary.pdf", g)
Number_contig_plot
```

## contig length and fate (binning outcome)

```{r contig_binning_summary}
contig_fates_df_pf <- rbind(contig_fates_df_am_pf,
                            contig_fates_df_ac_pf,
                            contig_fates_df_ad_pf,
                            contig_fates_df_af_pf
                      )
amount_pass_fail <- ggplot(contig_fates_df_pf, aes(y = factor(sample, samples), x = pass_fail_length, fill = passed_filter)) +
  geom_bar(stat = "identity") +
  labs(y= "Sample", x = "Amount of data passed or failed") +
  # scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6), limits = c(0, 6e+8)) +
  scale_x_continuous(labels=unit_format(unit = "M", scale = 1e-6)) +
  make_theme(palettefill = "Set1", leg_pos = "bottom", guide_nrow = 1)

contig_fates_df_bin <- rbind(contig_fates_df_am_bin,
                            contig_fates_df_ac_bin,
                            contig_fates_df_ad_bin,
                            contig_fates_df_af_bin
                      )
contigs_binned_length_plot <- ggplot(contig_fates_df_bin, aes(y = sample, x = binned_length, fill = binned)) +
  geom_bar(stat = "identity") +
    labs(x = "Sample", y = "Amount of data binned or unbinned") +
    scale_x_continuous(labels=unit_format(unit = "M", scale = 1e-6)) +
      make_theme(palettefill = "Set1", guide_nrow = 1)


contig_fates_df_am_mag <- contig_fates_df_am %>%
                            # filter(binned == "Y") %>%
                            group_by(sample, bin_name) %>%
                              summarise(num_contigs = n(), len_contigs = sum(length), .groups = "keep") %>%
                                left_join(select(vis_magOTUs_df_all, ID, Host, Sample, Cluster, Family, Genus, N50, Prevalence), by = c("bin_name" = "ID"))
contig_fates_df_ac_mag <- contig_fates_df_ac %>%
                            # filter(binned == "Y") %>%
                            group_by(sample, bin_name) %>%
                              summarise(num_contigs = n(), len_contigs = sum(length), .groups = "keep") %>%
                                left_join(select(vis_magOTUs_df_all, ID, Host, Sample, Cluster, Family, Genus, N50, Prevalence), by = c("bin_name" = "ID"))
contig_fates_df_ad_mag <- contig_fates_df_ad %>%
                            # filter(binned == "Y") %>%
                            group_by(sample, bin_name) %>%
                              summarise(num_contigs = n(), len_contigs = sum(length), .groups = "keep") %>%
                                left_join(select(vis_magOTUs_df_all, ID, Host, Sample, Cluster, Family, Genus, N50, Prevalence), by = c("bin_name" = "ID"))
contig_fates_df_af_mag <- contig_fates_df_af %>%
                            # filter(binned == "Y") %>%
                            group_by(sample, bin_name) %>%
                              summarise(num_contigs = n(), len_contigs = sum(length), .groups = "keep") %>%
                                left_join(select(vis_magOTUs_df_all, ID, Host, Sample, Cluster, Family, Genus, N50, Prevalence), by = c("bin_name" = "ID"))

contigs_binned_length_am_plot_genus <- ggplot(contig_fates_df_am_mag, aes(x = sample, y = len_contigs, fill = factor(Genus, genera))) +
                                  geom_bar(stat = "identity") +
                                    labs(x = "Sample", y = "Sum of length of contigs in bin", fill = "Genus") +
                                    # scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6), limits = c(0, 6e+8)) +
                                    scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6)) +
                                      make_theme(setFill = F,
                                          leg_pos = "right", guide_nrow = 22,
                                          x_angle = 30, x_hj = 1, x_vj = 1
                                        ) +
                                      scale_fill_manual(values=genusColors)
                                      # ggsave("Figures/05-contigs_binned_unbinned_by_genus_am.pdf")

contigs_binned_length_ac_plot_genus <- ggplot(contig_fates_df_ac_mag, aes(x = sample, y = len_contigs, fill = factor(Genus, genera))) +
                                  geom_bar(stat = "identity") +
                                    labs(x = "Sample", y = "Sum of length of contigs in bin", fill = "Genus") +
                                    # scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6), limits = c(0, 6e+8)) +
                                    scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6)) +
                                      make_theme(setFill = F,
                                          leg_pos = "right", guide_nrow = 22,
                                          x_angle = 30, x_hj = 1, x_vj = 1
                                        ) +
                                      scale_fill_manual(values=genusColors)
                                      # ggsave("Figures/05-contigs_binned_unbinned_by_genus_ac.pdf")

contigs_binned_length_ad_plot_genus <- ggplot(contig_fates_df_ad_mag, aes(x = sample, y = len_contigs, fill = factor(Genus, genera))) +
                                  geom_bar(stat = "identity") +
                                    labs(x = "Sample", y = "Sum of length of contigs in bin", fill = "Genus") +
                                    # scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6), limits = c(0, 6e+8)) +
                                    scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6)) +
                                      make_theme(setFill = F,
                                          leg_pos = "right", guide_nrow = 22,
                                          x_angle = 30, x_hj = 1, x_vj = 1
                                        ) +
                                      scale_fill_manual(values=genusColors)
                                      # ggsave("Figures/05-contigs_binned_unbinned_by_genus_ad.pdf")

contigs_binned_length_af_plot_genus <- ggplot(contig_fates_df_af_mag, aes(x = sample, y = len_contigs, fill = factor(Genus, genera))) +
                                  geom_bar(stat = "identity") +
                                    labs(x = "Sample", y = "Sum of length of contigs in bin", fill = "Genus") +
                                    # scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6), limits = c(0, 6e+8)) +
                                    scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6)) +
                                      make_theme(setFill = F,
                                          leg_pos = "right", guide_nrow = 22,
                                          x_angle = 30, x_hj = 1, x_vj = 1
                                        ) +
                                      scale_fill_manual(values=genusColors)
                                      # ggsave("Figures/05-contigs_binned_unbinned_by_genus_af.pdf")

contig_fates_df_am_mag_binned <- contig_fates_df_am %>%
                            filter(binned == "Y") %>%
                            group_by(sample, bin_name) %>%
                              summarise(num_contigs = n(), len_contigs = sum(length), .groups = "keep") %>%
                                left_join(select(vis_magOTUs_df_all, ID, Host, Sample, Cluster, Family, Genus, N50, Prevalence), by = c("bin_name" = "ID"))
contig_fates_df_ac_mag_binned <- contig_fates_df_ac %>%
                            filter(binned == "Y") %>%
                            group_by(sample, bin_name) %>%
                              summarise(num_contigs = n(), len_contigs = sum(length), .groups = "keep") %>%
                                left_join(select(vis_magOTUs_df_all, ID, Host, Sample, Cluster, Family, Genus, N50, Prevalence), by = c("bin_name" = "ID"))
contig_fates_df_ad_mag_binned <- contig_fates_df_ad %>%
                            filter(binned == "Y") %>%
                            group_by(sample, bin_name) %>%
                              summarise(num_contigs = n(), len_contigs = sum(length), .groups = "keep") %>%
                                left_join(select(vis_magOTUs_df_all, ID, Host, Sample, Cluster, Family, Genus, N50, Prevalence), by = c("bin_name" = "ID"))
contig_fates_df_af_mag_binned <- contig_fates_df_af %>%
                            filter(binned == "Y") %>%
                            group_by(sample, bin_name) %>%
                              summarise(num_contigs = n(), len_contigs = sum(length), .groups = "keep") %>%
                                left_join(select(vis_magOTUs_df_all, ID, Host, Sample, Cluster, Family, Genus, N50, Prevalence), by = c("bin_name" = "ID"))

contigs_binned_length_am_plot_genus_binned <- ggplot(contig_fates_df_am_mag_binned, aes(x = sample, y = len_contigs, fill = factor(Genus, genera))) +
                                  geom_bar(stat = "identity") +
                                    labs(x = "Sample", y = "Sum of length of contigs in bin", fill = "Genus") +
                                    # scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6), limits = c(0, 6e+8)) +
                                    scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6)) +
                                      make_theme(setFill = F,
                                          leg_pos = "right", guide_nrow = 22,
                                          x_angle = 30, x_hj = 1, x_vj = 1
                                        ) +
                                      scale_fill_manual(values=genusColors)
                                      # ggsave("Figures/05-contigs_binned_unbinned_by_genus_am.pdf")

contigs_binned_length_ac_plot_genus_binned <- ggplot(contig_fates_df_ac_mag_binned, aes(x = sample, y = len_contigs, fill = factor(Genus, genera))) +
                                  geom_bar(stat = "identity") +
                                    labs(x = "Sample", y = "Sum of length of contigs in bin", fill = "Genus") +
                                    # scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6), limits = c(0, 6e+8)) +
                                    scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6)) +
                                      make_theme(setFill = F,
                                          leg_pos = "right", guide_nrow = 22,
                                          x_angle = 30, x_hj = 1, x_vj = 1
                                        ) +
                                      scale_fill_manual(values=genusColors)
                                      # ggsave("Figures/05-contigs_binned_unbinned_by_genus_ac.pdf")

contigs_binned_length_ad_plot_genus_binned <- ggplot(contig_fates_df_ad_mag_binned, aes(x = sample, y = len_contigs, fill = factor(Genus, genera))) +
                                  geom_bar(stat = "identity") +
                                    labs(x = "Sample", y = "Sum of length of contigs in bin", fill = "Genus") +
                                    # scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6), limits = c(0, 6e+8)) +
                                    scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6)) +
                                      make_theme(setFill = F,
                                          leg_pos = "right", guide_nrow = 22,
                                          x_angle = 30, x_hj = 1, x_vj = 1
                                        ) +
                                      scale_fill_manual(values=genusColors)
                                      # ggsave("Figures/05-contigs_binned_unbinned_by_genus_ad.pdf")

contigs_binned_length_af_plot_genus_binned <- ggplot(contig_fates_df_af_mag_binned, aes(x = sample, y = len_contigs, fill = factor(Genus, genera))) +
                                  geom_bar(stat = "identity") +
                                    labs(x = "Sample", y = "Sum of length of contigs in bin", fill = "Genus") +
                                    # scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6), limits = c(0, 6e+8)) +
                                    scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6)) +
                                      make_theme(setFill = F,
                                          leg_pos = "right", guide_nrow = 22,
                                          x_angle = 30, x_hj = 1, x_vj = 1
                                        ) +
                                      scale_fill_manual(values=genusColors)
                                      # ggsave("Figures/05-contigs_binned_unbinned_by_genus_af.pdf")

contig_length_host_plot_am <- ggplot(filter(length_bin_sum_df, sample %in% samples_am), aes(x = length_bin, y = length_bin_sum, fill = binned)) +
                      geom_bar(stat = "identity") +
                        geom_text(aes(label = num_contigs), angle = 0, size = 1, vjust = 1) +
                        # geom_text(aes(label = num_contigs), angle = 90, size = 2) +
                          labs(x = "length of contig", y = "Total bases from contigs in bin", fill = "binned") +
                            scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6)) +
                              facet_wrap(~ sample, scales = "free") +
                                make_theme(x_angle = 40, x_size = 7, x_hj = 1, x_vj = 1, leg_pos = "none")
                                  ggsave("Figures/05c-contig_length_histogram_am.pdf")
contig_length_host_plot_am_passed <- ggplot(filter(length_bin_sum_df_passed, sample %in% samples_am), aes(x = length_bin, y = length_bin_sum, fill = binned)) +
                      geom_bar(stat = "identity") +
                        geom_text(aes(label = num_contigs), angle = 0, size = 1, vjust = 1) +
                        # geom_text(aes(label = num_contigs), angle = 90, size = 2) +
                          labs(x = "length of contig", y = "Total bases from contigs in bin", fill = "binned") +
                            scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6)) +
                              facet_wrap(~ sample, scales = "free") +
                                make_theme(x_angle = 40, x_size = 7, x_hj = 1, x_vj = 1, leg_pos = "none")
                                  ggsave("Figures/05d-contig_length_histogram_am_passed.pdf")
contig_length_host_plot_ac <- ggplot(filter(length_bin_sum_df, sample %in% samples_ac), aes(x = length_bin, y = length_bin_sum, fill = binned)) +
                      geom_bar(stat = "identity") +
                        geom_text(aes(label = num_contigs), angle = 0, size = 1, vjust = 1) +
                        # geom_text(aes(label = num_contigs), angle = 90, size = 2) +
                          labs(x = "length of contig", y = "Total bases from contigs in bin", fill = "binned") +
                            scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6)) +
                              facet_wrap(~ sample, scales = "free") +
                                make_theme(x_angle = 40, x_size = 7, x_hj = 1, x_vj = 1, leg_pos = "none")
                                  ggsave("Figures/05c-contig_length_histogram_ac.pdf")
contig_length_host_plot_ac_passed <- ggplot(filter(length_bin_sum_df_passed, sample %in% samples_ac), aes(x = length_bin, y = length_bin_sum, fill = binned)) +
                      geom_bar(stat = "identity") +
                        geom_text(aes(label = num_contigs), angle = 0, size = 1, vjust = 1) +
                        # geom_text(aes(label = num_contigs), angle = 90, size = 2) +
                          labs(x = "length of contig", y = "Total bases from contigs in bin", fill = "binned") +
                            scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6)) +
                              facet_wrap(~ sample, scales = "free") +
                                make_theme(x_angle = 40, x_size = 7, x_hj = 1, x_vj = 1, leg_pos = "none")
                                  ggsave("Figures/05d-contig_length_histogram_ac_passed.pdf")
contig_length_host_plot_ad <- ggplot(filter(length_bin_sum_df, sample %in% samples_ad), aes(x = length_bin, y = length_bin_sum, fill = binned)) +
                      geom_bar(stat = "identity") +
                        geom_text(aes(label = num_contigs), angle = 0, size = 1, vjust = 1) +
                        # geom_text(aes(label = num_contigs), angle = 90, size = 2) +
                          labs(x = "length of contig", y = "Total bases from contigs in bin", fill = "binned") +
                            scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6)) +
                              facet_wrap(~ sample, scales = "free") +
                                make_theme(x_angle = 40, x_size = 7, x_hj = 1, x_vj = 1, leg_pos = "none")
                                  ggsave("Figures/05c-contig_length_histogram_ad.pdf")
contig_length_host_plot_ad_passed <- ggplot(filter(length_bin_sum_df_passed, sample %in% samples_ad), aes(x = length_bin, y = length_bin_sum, fill = binned)) +
                      geom_bar(stat = "identity") +
                        geom_text(aes(label = num_contigs), angle = 0, size = 1, vjust = 1) +
                        # geom_text(aes(label = num_contigs), angle = 90, size = 2) +
                          labs(x = "length of contig", y = "Total bases from contigs in bin", fill = "binned") +
                            scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6)) +
                              facet_wrap(~ sample, scales = "free") +
                                make_theme(x_angle = 40, x_size = 7, x_hj = 1, x_vj = 1, leg_pos = "none")
                                  ggsave("Figures/05d-contig_length_histogram_ad_passed.pdf")
contig_length_host_plot_af <- ggplot(filter(length_bin_sum_df, sample %in% samples_af), aes(x = length_bin, y = length_bin_sum, fill = binned)) +
                      geom_bar(stat = "identity") +
                        geom_text(aes(label = num_contigs), angle = 0, size = 1, vjust = 1) +
                        # geom_text(aes(label = num_contigs), angle = 90, size = 2) +
                          labs(x = "length of contig", y = "Total bases from contigs in bin", fill = "binned") +
                            scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6)) +
                              facet_wrap(~ sample, scales = "free") +
                                make_theme(x_angle = 40, x_size = 7, x_hj = 1, x_vj = 1, leg_pos = "none")
                                  ggsave("Figures/05c-contig_length_histogram_af.pdf")
contig_length_host_plot_af_passed <- ggplot(filter(length_bin_sum_df_passed, sample %in% samples_af), aes(x = length_bin, y = length_bin_sum, fill = binned)) +
                      geom_bar(stat = "identity") +
                        geom_text(aes(label = num_contigs), angle = 0, size = 1, vjust = 1) +
                        # geom_text(aes(label = num_contigs), angle = 90, size = 2) +
                          labs(x = "length of contig", y = "Total bases from contigs in bin", fill = "binned") +
                            scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6)) +
                              facet_wrap(~ sample, scales = "free") +
                                make_theme(x_angle = 40, x_size = 7, x_hj = 1, x_vj = 1, leg_pos = "none")
                                  ggsave("Figures/05d-contig_length_histogram_af_passed.pdf")

contigs_depths_df_genus <- left_join(contigs_depths_df, select(vis_magOTUs_df_all, ID, Genus, Cluster), by = c("bin" = "ID")) %>%
  select(!Host) %>%
  left_join(rename(select(df, Sample, SpeciesID), Host = SpeciesID), by = c("sample" = "Sample"))


temp <- ggplot(filter(contigs_depths_df_genus, Host == "Apis mellifera"), aes(x = bin, y = depth, color = Genus, size = length, alpha = 0.5)) +
                          geom_point() +
                            make_theme(setFill = F, setCol = F,
                              leg_pos = "bottom",
                              guide_nrow = 7, leg_size = 12,
                              x_size = 5, x_angle = 30, x_hj = 1, x_vj = 1
                            ) +
                            scale_color_manual(values=genusColors)+
                              guides(size = "none", alpha = "none")
genus_legend <- get_only_legend(temp)
remove(temp)

contig_len_vs_depth_am <- ggplot(filter(contigs_depths_df_genus, Host == "Apis mellifera"), aes(x = bin, y = depth, color = Genus, size = length, alpha = 0.5)) +
                          geom_point() +
                            make_theme(setFill = F, setCol = F,
                              leg_pos = "bottom",
                              x_size = 5, x_angle = 50, x_hj = 1, x_vj = 1
                            ) +
                            scale_size_continuous(labels=unit_format(unit = "K", scale = 1e-4)) +
                            theme(legend.margin=margin(-1,-1,-1,-1), legend.box="vertical") +
                            scale_color_manual(values=genusColors) +
                            facet_wrap(~ factor(sample, samples_am), scales="free") +
                              guides(color = "none", alpha = "none")
                              ggsave("Figures/05g-length_vs_depth_contigs_all_am.pdf")
contig_len_vs_depth_am_binned <- ggplot(filter(contigs_depths_df_genus, Host == "Apis mellifera" & binned != "N"), aes(x = bin, y = depth, color = Genus, size = length, alpha = 0.5)) +
                          geom_point() +
                            make_theme(setFill = F, setCol = F,
                              leg_pos = "bottom",
                              x_size = 5, x_angle = 50, x_hj = 1, x_vj = 1
                            ) +
                            scale_size_continuous(labels=unit_format(unit = "K", scale = 1e-4)) +
                            theme(legend.margin=margin(-1,-1,-1,-1), legend.box="vertical") +
                            scale_color_manual(values=genusColors) +
                            facet_wrap(~ factor(sample, samples_am), scales="free") +
                              guides(color = "none", alpha = "none")
                              ggsave("Figures/05h-length_vs_depth_contigs_binned_am.pdf")
contig_len_vs_depth_ac <- ggplot(filter(contigs_depths_df_genus, Host == "Apis cerana"), aes(x = bin, y = depth, color = Genus, size = length, alpha = 0.5)) +
                          geom_point() +
                            make_theme(setFill = F, setCol = F,
                              leg_pos = "bottom",
                              x_size = 5, x_angle = 50, x_hj = 1, x_vj = 1
                            ) +
                            scale_size_continuous(labels=unit_format(unit = "K", scale = 1e-4)) +
                            theme(legend.margin=margin(-1,-1,-1,-1), legend.box="vertical") +
                            scale_color_manual(values=genusColors) +
                            facet_wrap(~ factor(sample, samples_ac), scales="free") +
                              guides(color = "none", alpha = "none")
                              ggsave("Figures/05g-length_vs_depth_contigs_all_ac.pdf")
contig_len_vs_depth_ac_binned <- ggplot(filter(contigs_depths_df_genus, Host == "Apis cerana" & binned != "N"), aes(x = bin, y = depth, color = Genus, size = length, alpha = 0.5)) +
                          geom_point() +
                            make_theme(setFill = F, setCol = F,
                              leg_pos = "bottom",
                              x_size = 5, x_angle = 50, x_hj = 1, x_vj = 1
                            ) +
                            scale_size_continuous(labels=unit_format(unit = "K", scale = 1e-4)) +
                            theme(legend.margin=margin(-1,-1,-1,-1), legend.box="vertical") +
                            scale_color_manual(values=genusColors) +
                            facet_wrap(~ factor(sample, samples_ac), scales="free") +
                              guides(color = "none", alpha = "none")
                              ggsave("Figures/05h-length_vs_depth_contigs_binned_ac.pdf")
contig_len_vs_depth_ad <- ggplot(filter(contigs_depths_df_genus, Host == "Apis dorsata"), aes(x = bin, y = depth, color = Genus, size = length, alpha = 0.5)) +
                          geom_point() +
                            make_theme(setFill = F, setCol = F,
                              leg_pos = "bottom",
                              x_size = 5, x_angle = 50, x_hj = 1, x_vj = 1
                            ) +
                            scale_size_continuous(labels=unit_format(unit = "K", scale = 1e-4)) +
                            theme(legend.margin=margin(-1,-1,-1,-1), legend.box="vertical") +
                            scale_color_manual(values=genusColors) +
                            facet_wrap(~ factor(sample, samples_ad), scales="free") +
                              guides(color = "none", alpha = "none")
                              ggsave("Figures/05g-length_vs_depth_contigs_all_ad.pdf")
contig_len_vs_depth_ad_binned <- ggplot(filter(contigs_depths_df_genus, Host == "Apis dorsata" & binned != "N"), aes(x = bin, y = depth, color = Genus, size = length, alpha = 0.5)) +
                          geom_point() +
                            make_theme(setFill = F, setCol = F,
                              leg_pos = "bottom",
                              x_size = 5, x_angle = 50, x_hj = 1, x_vj = 1
                            ) +
                            scale_size_continuous(labels=unit_format(unit = "K", scale = 1e-4)) +
                            theme(legend.margin=margin(-1,-1,-1,-1), legend.box="vertical") +
                            scale_color_manual(values=genusColors) +
                            facet_wrap(~ factor(sample, samples_ad), scales="free") +
                              guides(color = "none", alpha = "none")
                              ggsave("Figures/05h-length_vs_depth_contigs_binned_ad.pdf")
contig_len_vs_depth_af <- ggplot(filter(contigs_depths_df_genus, Host == "Apis florea"), aes(x = bin, y = depth, color = Genus, size = length, alpha = 0.5)) +
                          geom_point() +
                            make_theme(setFill = F, setCol = F,
                              leg_pos = "bottom",
                              x_size = 5, x_angle = 50, x_hj = 1, x_vj = 1
                            ) +
                            scale_size_continuous(labels=unit_format(unit = "K", scale = 1e-4)) +
                            theme(legend.margin=margin(-1,-1,-1,-1), legend.box="vertical") +
                            scale_color_manual(values=genusColors) +
                            facet_wrap(~ factor(sample, samples_af), scales="free") +
                              guides(color = "none", alpha = "none")
                              ggsave("Figures/05g-length_vs_depth_contigs_all_af.pdf")
contig_len_vs_depth_af_binned <- ggplot(filter(contigs_depths_df_genus, Host == "Apis florea" & binned != "N"), aes(x = bin, y = depth, color = Genus, size = length, alpha = 0.5)) +
                          geom_point() +
                            make_theme(setFill = F, setCol = F,
                              leg_pos = "bottom",
                              x_size = 5, x_angle = 50, x_hj = 1, x_vj = 1
                            ) +
                            scale_size_continuous(labels=unit_format(unit = "K", scale = 1e-4)) +
                            theme(legend.margin=margin(-1,-1,-1,-1), legend.box="vertical") +
                            scale_color_manual(values=genusColors) +
                            facet_wrap(~ factor(sample, samples_af), scales="free") +
                              guides(color = "none", alpha = "none")
                              ggsave("Figures/05h-length_vs_depth_contigs_binned_af.pdf")
```

```{r contig_binning_summary_plots,  dev = 'pdf', results='hold', fig.show = 'hold', out.width = '100%', fig.align = 'center'}
amount_pass_fail
  ggsave("Figures/05a-data-contigs_passed_failed.pdf", amount_pass_fail)
contigs_binned_length_plot
  ggsave("Figures/05b-contigs_binned_unbinned.pdf", contigs_binned_length_plot)
binned_unbinned_contigs_length_genus <- grid.arrange(
  arrangeGrob(
    contigs_binned_length_am_plot_genus + make_theme(setFill = F, setCol = F, leg_pos = "none", x_size = 7, x_angle = 30, x_hj = 1, x_vj = 1) + scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6)),
    contigs_binned_length_ac_plot_genus + make_theme(setFill = F, setCol = F, leg_pos = "none", x_size = 7, x_angle = 30, x_hj = 1, x_vj = 1) + scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6)),
    nrow = 1
  ),
  arrangeGrob(
    contigs_binned_length_ad_plot_genus + make_theme(setFill = F, setCol = F, leg_pos = "none", x_size = 7, x_angle = 30, x_hj = 1, x_vj = 1) + scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6)),
    contigs_binned_length_af_plot_genus + make_theme(setFill = F, setCol = F, leg_pos = "none", x_size = 7, x_angle = 30, x_hj = 1, x_vj = 1) + scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6)),
    nrow = 1
  ),
  get_only_legend(contigs_binned_length_am_plot_genus + make_theme(setFill = F, setCol = F, leg_pos = "bottom", guide_nrow = 6, leg_size = 7)),
  nrow = 3, heights = c(2,2,1)
)
  ggsave("Figures/05e-contigs_binned_unbinned_by_genus.pdf", binned_unbinned_contigs_length_genus)

binned_unbinned_contigs_length_genus_scaled <- grid.arrange(
  arrangeGrob(
    contigs_binned_length_am_plot_genus + make_theme(setFill = F, setCol = F, leg_pos = "none", x_size = 7, x_angle = 30, x_hj = 1, x_vj = 1) + scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6), limits = c(0, 6e+8)),
    contigs_binned_length_ac_plot_genus + make_theme(setFill = F, setCol = F, leg_pos = "none", x_size = 7, x_angle = 30, x_hj = 1, x_vj = 1) + scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6), limits = c(0, 6e+8)),
    nrow = 1
  ),
  arrangeGrob(
    contigs_binned_length_ad_plot_genus + make_theme(setFill = F, setCol = F, leg_pos = "none", x_size = 7, x_angle = 30, x_hj = 1, x_vj = 1) + scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6), limits = c(0, 6e+8)),
    contigs_binned_length_af_plot_genus + make_theme(setFill = F, setCol = F, leg_pos = "none", x_size = 7, x_angle = 30, x_hj = 1, x_vj = 1) + scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6), limits = c(0, 6e+8)),
    nrow = 1
  ),
  get_only_legend(contigs_binned_length_am_plot_genus + make_theme(setFill = F, setCol = F, leg_pos = "bottom", guide_nrow = 6, leg_size = 7)),
  nrow = 3, heights = c(2,2,1)
)
  ggsave("Figures/05e-contigs_binned_unbinned_by_genus_scaled.pdf", binned_unbinned_contigs_length_genus_scaled)
binned_unbinned_contigs_length_genus_binned <- grid.arrange(
  arrangeGrob(
    contigs_binned_length_am_plot_genus_binned + make_theme(setFill = F, setCol = F, leg_pos = "none", x_size = 7, x_angle = 30, x_hj = 1, x_vj = 1) + scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6)),
    contigs_binned_length_ac_plot_genus_binned + make_theme(setFill = F, setCol = F, leg_pos = "none", x_size = 7, x_angle = 30, x_hj = 1, x_vj = 1) + scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6)),
    nrow = 1
  ),
  arrangeGrob(
    contigs_binned_length_ad_plot_genus_binned + make_theme(setFill = F, setCol = F, leg_pos = "none", x_size = 7, x_angle = 30, x_hj = 1, x_vj = 1) + scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6)),
    contigs_binned_length_af_plot_genus_binned + make_theme(setFill = F, setCol = F, leg_pos = "none", x_size = 7, x_angle = 30, x_hj = 1, x_vj = 1) + scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6)),
    nrow = 1
  ),
  get_only_legend(contigs_binned_length_am_plot_genus_binned + make_theme(setFill = F, setCol = F, leg_pos = "bottom", guide_nrow = 6, leg_size = 7)),
  nrow = 3, heights = c(2,2,1)
)
  ggsave("Figures/05f-contigs_by_genus_binned.pdf", binned_unbinned_contigs_length_genus_binned)

binned_unbinned_contigs_length_genus_scaled_binned <- grid.arrange(
  arrangeGrob(
    contigs_binned_length_am_plot_genus_binned + make_theme(setFill = F, setCol = F, leg_pos = "none", x_size = 7, x_angle = 30, x_hj = 1, x_vj = 1) + scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6), limits = c(0, 1.5e+8)),
    contigs_binned_length_ac_plot_genus_binned + make_theme(setFill = F, setCol = F, leg_pos = "none", x_size = 7, x_angle = 30, x_hj = 1, x_vj = 1) + scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6), limits = c(0, 1.5e+8)),
    nrow = 1
  ),
  arrangeGrob(
    contigs_binned_length_ad_plot_genus_binned + make_theme(setFill = F, setCol = F, leg_pos = "none", x_size = 7, x_angle = 30, x_hj = 1, x_vj = 1) + scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6), limits = c(0, 1.5e+8)),
    contigs_binned_length_af_plot_genus_binned + make_theme(setFill = F, setCol = F, leg_pos = "none", x_size = 7, x_angle = 30, x_hj = 1, x_vj = 1) + scale_y_continuous(labels=unit_format(unit = "M", scale = 1e-6), limits = c(0, 1.5e+8)),
    nrow = 1
  ),
  get_only_legend(contigs_binned_length_am_plot_genus_binned + make_theme(setFill = F, setCol = F, leg_pos = "bottom", guide_nrow = 6, leg_size = 7)),
  nrow = 3, heights = c(2,2,1)
)
  ggsave("Figures/05f-contigs_by_genus_binned_scaled.pdf", binned_unbinned_contigs_length_genus_scaled_binned)
contig_length_host_plot_am
contig_length_host_plot_am_passed
contig_length_host_plot_ac
contig_length_host_plot_ac_passed
contig_length_host_plot_ad
contig_length_host_plot_ad_passed
contig_length_host_plot_af
contig_length_host_plot_af_passed
contig_len_vs_depth_am
contig_len_vs_depth_am_binned
contig_len_vs_depth_ac
contig_len_vs_depth_ac_binned
contig_len_vs_depth_ad
contig_len_vs_depth_ad_binned
contig_len_vs_depth_af
contig_len_vs_depth_af_binned
```

## MAGs prevalence and abundance

Mean of mean contig coverage (calculated for metabat2) as a proxy for abundance of MAG in it's own sample.

Total MAGs recovered - distribution of quality / total + per sample

```{r visualize_coverage}
MAGs_collated_info_plot_means <- vis_magOTUs_df_all %>%
                        group_by(Sample) %>%
                          summarise(Sample, completeness, contamination, N50, Host) %>%
                            mutate(Completeness_mean = mean(completeness)) %>%
                              mutate(Contamination_mean = mean(contamination)) %>%
                              mutate(N50_mean = mean(N50))
Completeness_hist <- ggplot(MAGs_collated_info_plot, aes(x = completeness, fill = Host)) +
    geom_histogram(binwidth=2) +
    geom_vline(xintercept = 70-1) +
      make_theme(palettefill="Spectral")
N50_hist <- ggplot(MAGs_collated_info_plot, aes(x = N50, fill = Host)) +
    geom_histogram(bins = 150) +
      scale_x_continuous(labels=unit_format(unit = "M", scale = 1e-6)) +
      geom_vline(xintercept = 10000) +
      make_theme(palettefill="Spectral")
Contamination_hist <- ggplot(MAGs_collated_info_plot, aes(x = contamination, fill = Host)) +
    geom_histogram(binwidth=2) +
    geom_vline(xintercept = 5) +
      make_theme(palettefill="Spectral")
completeness_per_sample <- ggplot(MAGs_collated_info_plot, aes(y = factor(Sample, levels = samples), fill = Completeness_quality)) +
    geom_bar(position = "stack") +
    labs(fill = "Quality", y = "Sample") +
      make_theme(palettefill="RdYlGn", max_colors = length(levels(MAGs_collated_info_plot$Completeness_quality)))
N50_per_sample <- ggplot(MAGs_collated_info_plot, aes(y = factor(Sample, levels = samples), fill = N50_quality)) +
        geom_bar(position = "stack") +
        labs(fill = "Quality", y = "Sample") +
        make_theme(palettefill="RdYlBu", max_colors = length(levels(MAGs_collated_info_plot$N50_quality)))
contamination_per_sample <- ggplot(MAGs_collated_info_plot, aes(y = factor(Sample, levels = samples), fill = Contamination_quality)) +
    geom_bar(position = "stack") +
    labs(fill = "Quality", y = "Sample") +
      make_theme(palettefill="RdYlBu", max_colors = length(levels(MAGs_collated_info_plot$Contamination_quality)))
MAG_quality_per_sample <- ggplot(MAGs_collated_info_plot, aes(y = factor(Sample, levels = samples), fill = all_quality)) +
    geom_bar(position = "stack") +
    labs(fill = "Quality", y = "Sample") +
      make_theme(palettefill="Set1",)

prev_vs_abud_all <- ggplot(vis_magOTUs_df_all, aes(x = mean_coverage, y = Prevalence, size = completeness, color = Genus, alpha = 0.5)) +
                    geom_point(position = position_jitter(w = 0, h = 0.05)) +
                      make_theme(setFill = F, setCol = F,
                        leg_pos = "bottom",
                        guide_nrow = 8,
                        leg_size = 12
                      ) +
                      theme(legend.margin=margin(-1,-1,-1,-1), legend.box="vertical") +
                      scale_color_manual(values=genusColors) +
                      scale_x_continuous(trans = "log10") +
                        scale_alpha(guide = "none")

prev_vs_abud <- ggplot(vis_magOTUs_df, aes(x = mean_coverage, y = Prevalence, size = completeness, color = Genus, alpha = 0.5)) +
  geom_point(position = position_jitter(w = 0, h = 0.05)) +
    make_theme(setFill = F, setCol = F,
      leg_pos = "bottom",
      guide_nrow = 8,
      leg_size = 12
    ) +
    theme(legend.margin=margin(-1,-1,-1,-1), legend.box="vertical") +
    scale_color_manual(values=genusColors) +
    scale_x_continuous(trans = "log10") +
    # facet_wrap(~ factor(Host, host_order)) +
      scale_alpha(guide = "none")

prev_overall_vs_abud_all <- ggplot(vis_magOTUs_df_all, aes(x = mean_coverage, y = Prevalence_overall, size = completeness, color = Genus, alpha = 0.5)) +
                    geom_point(position = position_jitter(w = 0, h = 0.05)) +
                      make_theme(setFill = F, setCol = F,
                        leg_pos = "bottom",
                        guide_nrow = 8,
                        leg_size = 12
                      ) +
                      theme(legend.margin=margin(-1,-1,-1,-1), legend.box="vertical") +
                      scale_color_manual(values=genusColors) +
                      scale_x_continuous(trans = "log10") +
                        scale_alpha(guide = "none")

prev_overall_vs_abud <- ggplot(vis_magOTUs_df, aes(x = mean_coverage, y = Prevalence_overall, size = completeness, color = Genus, alpha = 0.5)) +
  geom_point(position = position_jitter(w = 0, h = 0.05)) +
    make_theme(setFill = F, setCol = F,
      leg_pos = "bottom",
      guide_nrow = 8,
      leg_size = 12
    ) +
    theme(legend.margin=margin(-1,-1,-1,-1), legend.box="vertical") +
    scale_color_manual(values=genusColors) +
    scale_x_continuous(trans = "log10") +
    # facet_wrap(~ factor(Host, host_order)) +
      scale_alpha(guide = "none")

prev_vs_abud_all_host <- ggplot(vis_magOTUs_df_all, aes(x = mean_coverage, y = Prevalence, size = completeness, color = Genus, alpha = 0.5)) +
  geom_point(position = position_jitter(w = 0, h = 0.05)) +
    make_theme(setFill = F, setCol = F,
      leg_pos = "none",
      guide_nrow = 8,
      leg_size = 12
    ) +
    ggtitle("MAGs with > 70% completeness and < 5% contamination") +
    theme(legend.margin=margin(-1,-1,-1,-1), legend.box="vertical") +
    scale_color_manual(values=genusColors) +
    scale_x_continuous(trans = "log10") +
    facet_wrap(~ factor(Host, host_order)) +
      scale_alpha(guide = "none")
      ggsave("Figures/07a-prev_vs_coverage_all_MAGs_genus_by_host.pdf")

prev_vs_abud_host <- ggplot(vis_magOTUs_df, aes(x = mean_coverage, y = Prevalence, size = completeness, color = Genus, alpha = 0.5)) +
  geom_point(position = position_jitter(w = 0, h = 0.05)) +
    make_theme(setFill = F, setCol = F,
      leg_pos = "none",
      guide_nrow = 8,
      leg_size = 12
    ) +
    ggtitle("MAGs with > 70% completeness and < 5% contamination") +
    theme(legend.margin=margin(-1,-1,-1,-1), legend.box="vertical") +
    scale_color_manual(values=genusColors) +
    scale_x_continuous(trans = "log10") +
    facet_wrap(~ factor(Host, host_order)) +
      scale_alpha(guide = "none")
      ggsave("Figures/07a-prev_vs_coverage_filtered_MAGs_genus_by_host.pdf")

prev_vs_abud_all_host <- ggplot(vis_magOTUs_df_all, aes(x = mean_coverage, y = Prevalence, color = Genus)) +
  geom_point(position = position_jitter(w = 0, h = 0.05)) +
    make_theme(setFill = F, setCol = F,
      leg_pos = "none",
      guide_nrow = 8,
      leg_size = 12
    ) +
    ggtitle("MAGs with > 70% completeness and < 5% contamination") +
    theme(legend.margin=margin(-1,-1,-1,-1), legend.box="vertical") +
    scale_color_manual(values=genusColors) +
    scale_x_continuous(trans = "log10") +
    facet_wrap(~ factor(Host, host_order)) +
      scale_alpha(guide = "none")
      ggsave("Figures/07a-prev_vs_coverage_all_MAGs_genus_by_host_no_size.pdf")

prev_vs_abud_host <- ggplot(vis_magOTUs_df, aes(x = mean_coverage, y = Prevalence, color = Genus)) +
  geom_point(position = position_jitter(w = 0, h = 0.05)) +
    make_theme(setFill = F, setCol = F,
      leg_pos = "none",
      guide_nrow = 8,
      leg_size = 12
    ) +
    ggtitle("MAGs with > 70% completeness and < 5% contamination") +
    theme(legend.margin=margin(-1,-1,-1,-1), legend.box="vertical") +
    scale_color_manual(values=genusColors) +
    scale_x_continuous(trans = "log10") +
    facet_wrap(~ factor(Host, host_order)) +
      scale_alpha(guide = "none")
      ggsave("Figures/07a-prev_vs_coverage_filtered_MAGs_genus_by_host_no_size.pdf")
```

```{r visualize_coverage_plots,  dev = 'pdf', results='hold', fig.show = 'hold', out.width = '100%', fig.align = 'center'}
legend_hist_host <- get_only_legend(Completeness_hist)
g  <- arrangeGrob(
  arrangeGrob(
      Completeness_hist + make_theme(setFill = F, setCol = F, leg_pos = "none"),
      Contamination_hist + make_theme(setFill = F, setCol = F, leg_pos = "none"),
      N50_hist + make_theme(setFill = F, setCol = F, leg_pos = "none"),
      nrow = 2,
      layout_matrix = rbind(c(1,2), c(3,3))
    ),
    legend_hist_host,
    heights = c(10, 1)
  )
  ggsave("Figures/06a-QC_MAG_histogram.pdf", g)
g <- grid.arrange(
    MAG_quality_per_sample + make_theme(setFill = F, setCol = F, leg_size = 7, y_size = 5, leg_pos = "right", guide_nrow = 2),
    N50_per_sample + make_theme(setFill = F, setCol = F, leg_size = 7, y_size = 5, leg_pos = "right", guide_nrow = 7),
    contamination_per_sample + make_theme(setFill = F, setCol = F, leg_size = 7, y_size = 5, leg_pos = "right", guide_nrow = 4),
    completeness_per_sample + make_theme(setFill = F, setCol = F, leg_size = 7, y_size = 5, leg_pos = "right", guide_nrow = 10)
  )
  ggsave("Figures/06b-QC_MAG_per_sample.pdf", g)
g <- grid.arrange(prev_vs_abud_all + make_theme(setFill = F, setCol = F, leg_pos = "none"),
             prev_vs_abud + make_theme(setFill = F, setCol = F, leg_pos = "none") + ggtitle("MAGs with > 70% completeness and < 5% contamination"),
             genus_legend,
             heights = c(3,3,2)
           )
    ggsave("Figures/07a-prev_vs_coverage_MAGs_genus.pdf", g)
g <- grid.arrange(prev_overall_vs_abud_all + make_theme(setFill = F, setCol = F, leg_pos = "none"),
             prev_overall_vs_abud + make_theme(setFill = F, setCol = F, leg_pos = "none") + ggtitle("MAGs with > 70% completeness and < 5% contamination"),
             genus_legend,
             heights = c(3,3,2)
           )
    ggsave("Figures/07a-prev_overall_vs_coverage_MAGs_genus.pdf", g)
```

```{r mag_summary_stat_make_plots}
extend_colors_family <- function(names_vec){
  final_list <- list()
  for (a_name in names_vec) {
    if (a_name %in% names(familyColors)) {
      final_list[a_name] = familyColors[a_name]
    } else {
      final_list[a_name] = "grey"
    }
  }
  return(final_list)
}

extend_colors_genera <- function(names_vec){
  final_list <- list()
  for (a_name in names_vec) {
    if (a_name %in% names(genusColors)) {
      final_list[a_name] = genusColors[a_name]
    } else {
      final_list[a_name] = "grey"
    }
  }
  return(final_list)
}
```

There are a total of `r dim(MAGs_collated)[[1]]` MAGs present. There were `r dim(filter(MAGs_collated_info_plot, completeness > 95 & contamination < 5))[[1]]` high quality MAGs (> 95% complete and < 5% redundant) and `r dim(filter(MAGs_collated_info_plot, completeness > 50 & contamination < 10))[[1]]` with > 50% completion and < 10% redundancy.

## MAG taxonomy affiliation per sample


```{r mag_genus_summary}
genus_MAG_quality_host_all <- ggplot(vis_magOTUs_df_all, aes(y = Genus, fill = Host)) +
        geom_bar(position = "stack") +
        labs(fill = "Host", y = "Genus", x = "Number of MAGs") +
        make_theme(palettefill = "Spectral")
      ggsave("Figures/07-QC_per_Genus_per_host_all.pdf")

genus_MAG_quality_host <- ggplot(filter(vis_magOTUs_df_all, all_quality=="Pass"), aes(y = Genus, fill = Host)) +
        geom_bar(position = "stack") +
        labs(fill = "Host", y = "Genus", x = "Number of MAGs") +
        make_theme(palettefill = "Spectral")
      ggsave("Figures/07-QC_per_Genus_per_host_passed.pdf")
```

```{r mags_genus_plot,  dev = 'pdf', results='hold', fig.show = 'hold', out.width = '100%', fig.align = 'center', fig.cap = 'MAG quality summarised'}
genus_MAG_quality_host_all
genus_MAG_quality_host
```

The common threshold (thumb-rule) of >70% completeness and contamination <5% along with N50 >10Kb (N50 threshold does not exclude any genomes) seems appropriate as it does not exclude too many MAGs. Completeness is currently the most powerful criterion.

There are a total of `r MAGs_collated_info_plot %>% pull(Cluster) %>% unique %>% length` clusters. They represent `r MAGs_collated_info_plot %>% pull(Family) %>% unique %>% length` families. Only `r MAGs_collated_info_plot %>% filter(all_quality == "Pass") %>% pull(Cluster) %>% unique %>% length` of them are represented by MAGs that cross the threshold comprising `r MAGs_collated_info_plot %>% filter(all_quality == "Pass") %>% pull(Family) %>% unique %>% length` families. The following families are not represented by MAGs crossing the threshold `r fail_families`.

The families represented by passable MAGs will be considered for further analysis. These include:
`r pass_families`
including 80 clusters.

The passed MAGs include `r filter(MAGs_collated_info_plot, all_quality=="Pass") %>% pull(Genus) %>% unique %>% length` <!-- 26  --> out of `r MAGs_collated_info_plot %>% pull(Genus) %>% unique %>% length` <!-- 34 --> genera.
I exclude the following because they only contain 1 MAG: `r filter(MAGs_collated_info_plot, all_quality=="Pass") %>% group_by(Genus) %>% summarise(number = n()) %>% filter(number <2)`
<!-- g__Pantoea, g__JAATFO01, g__Hafnia, g__Floricoccus, g__Klebsiella -->
`r filter(MAGs_collated_info_plot, all_quality=="Pass") %>% pull(Species) %>% unique %>% length` <!-- 29 --> out of `r MAGs_collated_info_plot %>% pull(Species) %>% unique %>% length` <!-- 51 --> species.

```{r magOTU_summary}
line_list <- c()
for (num in 1:94){
  add_line <- geom_vline(xintercept=num+0.5, size=0.1, color="black")
  # add_line <- geom_vline(xintercept=num+0.5, size=0.1, alpha=0.5, color="grey")
  line_list <- c(line_list, add_line)
}

magOTUs_per_sample <- ggplot(vis_magOTUs_df_all, aes(y = factor(Cluster), x = factor(sample, samples), fill = Host)) +
                            geom_tile() +
                              labs(x = "Sample", y = "Cluster")+
                              make_theme(setFill=F,
                              # make_theme(palettefill="Spectral", max_colors = length(unique(vis_magOTUs_df$Cluster)),
                              leg_pos="none", guide_nrow=6,
                              y_hj=1, y_size=7, leg_size=8, y_vj=0.5,
                              x_vj=0, x_hj=1, x_size=6, x_angle=90) +
                              scale_fill_manual(values=host_order_color) +
                              line_list
                                    ggsave("Figures/08a-magOTUs_per_sample.pdf")

magOTUs_per_sample_genus <- ggplot(vis_magOTUs_df_all, aes(y = factor(Cluster), x = factor(sample, samples), fill = factor(Genus, genera))) +
                            geom_tile() +
                              labs(x = "Sample", y = "Cluster")+
                              make_theme(setFill=F,
                              # make_theme(palettefill="Spectral", max_colors = length(unique(vis_magOTUs_df$Cluster)),
                              leg_pos="none", guide_nrow=6,
                              y_hj=1, y_size=7, leg_size=8, y_vj=0.5,
                              x_vj=0, x_hj=1, x_size=6, x_angle=90) +
                              scale_fill_manual(values=genusColors, guide = F) +
                              line_list
                                    ggsave("Figures/08b-magOTU_per_sample_genus.pdf")

magOTUs_per_sample_by_host_genus <- ggplot(vis_magOTUs_df_all, aes(y = Cluster, x = sample, fill = factor(Genus, genera))) +
        geom_tile() +
        labs(y = "Cluster", x = "Prevalence", fill = "Genus") +
        make_theme(setFill = F, setCol = F,
                   y_size = 2, y_hj = 1.5, y_vj = 0.5,
                   x_size = 7, x_angle = 40, x_hj = 1, x_vj = 1,
                   leg_size = 5, leg_pos = "none") +
        scale_fill_manual(values=genusColors) +
          facet_wrap(~ factor(Host, host_order), scales = "free")
      ggsave("Figures/08c-magOTU_by_host_genus.pdf")
# contigs_depths_df %>%
#   filter(bin == "MAG_C2.4_8")
#
# vis_magOTUs_df_all %>%
#   filter(Cluster == "116_1") %>%
#     select(Class, Genus, ID, completeness, length)

magOTUs_per_sample_by_host_coverage <- ggplot(vis_magOTUs_df_all, aes(y = Cluster, x = sample, fill = mean_coverage)) +
        geom_tile() +
        labs(y = "Cluster", x = "Prevalence", fill = "Log of mean of contig mean coverage") +
        make_theme(setFill = F, setCol = F,
                   y_size = 7, y_hj = 1, y_vj = 0.5,
                   x_size = 7, x_angle = 40, x_hj = 1, x_vj = 1,
                   guide_nrow = 1,
                   leg_pos = "bottom"
                 ) +
          guides(fill = guide_colorbar(barhwight = 1, barwidth = 10)) +
          scale_fill_gradientn(colors=brewer.pal(5, "RdYlGn"), na.value = "transparent",
                              trans = "log10") +
          facet_wrap(~ factor(Host, host_order), scales = "free")
          ggsave("Figures/08c-magOTU_by_host_MAGs_coverage.pdf")

magOTUs_per_sample_by_host_prevalence <- ggplot(vis_magOTUs_df_all, aes(y = Cluster, x = sample, fill = Prevalence)) +
        geom_tile() +
        labs(y = "Cluster", x = "Prevalence", fill = "Prevalence within host") +
        make_theme(setFill = F, setCol = F,
                   y_size = 7, y_hj = 1, y_vj = 0.5,
                   x_size = 7, x_angle = 40, x_hj = 1, x_vj = 1,
                   guide_nrow = 1,
                   leg_pos = "bottom"
                 ) +
          guides(fill = guide_colorbar(barhwight = 1, barwidth = 10)) +
          scale_fill_gradientn(colors=brewer.pal(5, "RdYlGn"), na.value = "transparent") +
          facet_wrap(~ factor(Host, host_order), scales = "free")
          ggsave("Figures/08c-magOTU_by_host_MAGs_prevalence.pdf")

vis_magOTUs_df_all_shared_cluster <- vis_magOTUs_df_all %>%
                              group_by(Cluster) %>%
                                mutate(Num_hosts = n_distinct(Host)) %>%
                                  filter(Num_hosts > 1)

magOTUs_shared_per_sample_genus <- ggplot(vis_magOTUs_df_all_shared_cluster, aes(y = factor(Cluster), x = factor(sample, samples), fill = factor(Genus, genera))) +
                            geom_tile() +
                              labs(x = "Sample", y = "Cluster")+
                              make_theme(setFill=F,
                              leg_pos="none", guide_nrow=6,
                              y_hj=1, y_size=7, leg_size=8, y_vj=0.5,
                              x_vj=0, x_hj=1, x_size=6, x_angle=90) +
                              scale_fill_manual(values=genusColors) +
                              line_list
                                    ggsave("Figures/08d-magOTU_shared_per_sample_genus.pdf")

magOTUs_shared_per_sample_prev_abund <- ggplot(vis_magOTUs_df_all_shared_cluster, aes(y = factor(Cluster), x = factor(sample, samples), fill = Prevalence)) +
                            geom_tile() +
                            geom_text(aes(label = round(mean_coverage, 2)), size = 1) +
                              labs(x = "Sample", y = "Cluster", fill = "Prevalence within host")+
                              make_theme(setFill=F,
                              y_hj=1, y_size=7, leg_size=8, y_vj=0.5,
                              x_vj=0, x_hj=1, x_size=6, x_angle=90) +
                              guides(fill = guide_colorbar(barhwight = 1, barwidth = 10)) +
                              scale_fill_gradientn(colors=brewer.pal(5, "RdYlGn"), na.value = "transparent", trans = "log10") +
                              line_list
                                    ggsave("Figures/08d-magOTUs_shared_per_sample_prev_abund.pdf")

magOTUs_per_sample_by_host_completeness_genus <- ggplot(vis_magOTUs_df_all, aes(y = Cluster, x = Num_mags, size = factor(Completeness_quality), color = Genus, alpha = 0.5)) +
        geom_point() +
        labs(y = "Cluster", x = "Number of MAGs", size = "Completeness") +
        make_theme(setFill = F, setCol = F,
                   y_size = 3, y_hj = 1, y_vj = 0.5,
                   leg_size = 5, leg_pos = "right") +
        scale_color_manual(values=genusColors) +
          facet_wrap(~ factor(Host, host_order)) +
            guides(color = "none", alpha = "none")
      ggsave("Figures/08e-magOTUs_by_host_completeness.pdf")

prev_abd_by_genus_completeness <- ggplot(vis_magOTUs_df_all, aes(y = Prevalence, x = mean_coverage, color = factor(Completeness_quality), alpha = 0.5)) +
        geom_point(position = position_jitter(w = 0, h = 0.05)) +
        labs(y = "Prevalence within host", x = "Mean of mean contig coverage", color = "Completeness") +
        make_theme(setFill = F, setCol = T,
                   palettecolor = "RdYlGn",
                   # y_size = 3, y_hj = 1, y_vj = 0.5,
                   x_angle = 30, x_hj = 1, x_vj = 1,
                   leg_size = 8, leg_pos = "right",
                   guide_nrow = 11
                 ) +
        scale_x_continuous(trans="log10") +
          facet_wrap(~ Genus) +
            guides(alpha = "none", color = "none")
            ggsave("Figures/08f-mags_prev_vs_abd_by_genus_completeness.pdf")

prev_abd_by_genus_host <- ggplot(vis_magOTUs_df_all, aes(y = Prevalence, x = mean_coverage, color = Host, alpha = 0.5)) +
        geom_point(position = position_jitter(w = 0, h = 0.05)) +
        labs(y = "Cluster", x = "Mean of mean contig coverage", size = "Completeness") +
        make_theme(setFill = F, setCol = F,
                   # y_size = 3, y_hj = 1, y_vj = 0.5,
                   x_angle = 30, x_hj = 1, x_vj = 1,
                   leg_size = 5, leg_pos = "right") +
        scale_color_manual(values=host_order_color) +
        scale_x_continuous(trans="log10") +
          facet_wrap(~ Genus) +
            guides(color = "none", alpha = "none")
            ggsave("Figures/08f-mags_prev_vs_abd_by_genus_host.pdf")
```

```{r magOTU_summary_plots,  dev = 'pdf', results='hold', fig.show = 'hold', out.width = '100%', fig.align = 'center'}
magOTUs_per_sample
magOTUs_per_sample_genus
magOTUs_per_sample_by_host_genus
magOTUs_per_sample_by_host_coverage
magOTUs_per_sample_by_host_prevalence
magOTUs_shared_per_sample_genus
magOTUs_shared_per_sample_prev_abund
magOTUs_per_sample_by_host_completeness_genus
prev_abd_by_genus_completeness
prev_abd_by_genus_host
```


```{r magOTU_numbers_compare}
vis_magOTUs_df_numClusters_all <- vis_magOTUs_df_all %>%
                        group_by(sample) %>%
                          summarise(sample, Host, number_of_clusters = n_distinct(Cluster), .groups="keep") %>%
                            unique()

                            test_all <- pairwise.wilcox.test(vis_magOTUs_df_numClusters_all$number_of_clusters, vis_magOTUs_df_numClusters_all$Host, p.adjust = "fdr")
                            glm_all <- summary(glm(data = vis_magOTUs_df_numClusters_all, number_of_clusters ~ Host, family = "poisson"))



vis_magOTUs_df_numClusters_all_plot <- ggplot(vis_magOTUs_df_numClusters_all, aes(x = factor(Host, levels = c("Apis florea", "Apis cerana", "Apis mellifera", "Apis dorsata")), y = number_of_clusters, fill = Host)) +
                                        geom_boxplot(outlier.shape = NA) +
                                        geom_jitter() +
                                        labs(y = "Number of magOTUs per individual", x = "Host species") +
                                          make_theme(leg_pos = "none", x_angle = 30, setFill = F, x_vj = 1, x_hj = 1, ) +
                                          scale_fill_manual(values=host_order_color)
                                          ggsave("Figures/09a-magOTU_number_per_sample_all.pdf")

vis_magOTUs_df_numClusters <- vis_magOTUs_df %>%
                        group_by(sample) %>%
                          summarise(sample, Host, number_of_clusters = n_distinct(Cluster)) %>%
                            unique

                        test_passed <- pairwise.wilcox.test(vis_magOTUs_df_numClusters$number_of_clusters, vis_magOTUs_df_numClusters$Host, p.adjust = "fdr")
                        glm_passed <- summary(glm(data = vis_magOTUs_df_numClusters, number_of_clusters ~ Host, family = "poisson"))


vis_magOTUs_df_numClusters_passed_plot <- ggplot(vis_magOTUs_df_numClusters, aes(x = factor(Host, levels = c("Apis florea", "Apis cerana", "Apis mellifera", "Apis dorsata")), y = number_of_clusters, fill = Host)) +
                                        geom_boxplot(outlier.shape = NA) +
                                        geom_jitter() +
                                        labs(y = "Number of magOTUs per individual", x = "Host species") +
                                          make_theme(leg_pos = "none", x_angle = 30, setFill = F, x_hj = 1, x_vj = 1) +
                                          scale_fill_manual(values=host_order_color)
                                          ggsave("Figures/09a-magOTU_number_per_sample_passed.pdf")
```

```{r magOTU_numbers_compare_plots,  dev = 'pdf', results='hold', fig.show = 'hold', out.width = '100%', fig.align = 'center'}
grid.arrange(vis_magOTUs_df_numClusters_all_plot, vis_magOTUs_df_numClusters_passed_plot, nrow = 1)
glm_all
test_all
glm_passed
test_passed
```

```{r magOTU_clustering,  dev = 'pdf', results='hold', fig.show = 'hold', out.width = '100%', fig.align = 'center'}
observations_host <- list(
   `Apis mellifera` = c(pivot_wider(summarise(group_by(vis_magOTUs_df, Host), Cluster, .groups = "keep"), names_from = Host, values_from = Cluster, values_fn = list) %>% pull(`Apis mellifera`) %>% unlist),
   `Apis cerana` = c(pivot_wider(summarise(group_by(vis_magOTUs_df, Host), Cluster, .groups = "keep"), names_from = Host, values_from = Cluster, values_fn = list) %>% pull(`Apis cerana`) %>% unlist),
   `Apis dorsata` = c(pivot_wider(summarise(group_by(vis_magOTUs_df, Host), Cluster, .groups = "keep"), names_from = Host, values_from = Cluster, values_fn = list) %>% pull(`Apis dorsata`) %>% unlist),
   `Apis florea` = c(pivot_wider(summarise(group_by(vis_magOTUs_df, Host), Cluster, .groups = "keep"), names_from = Host, values_from = Cluster, values_fn = list) %>% pull(`Apis florea`) %>% unlist)
)

magOTU_passed_venn <- ggVennDiagram(observations_host) +
                        scale_color_manual(values=host_order_color) +
                            scale_fill_gradient(low = brewer.pal(8, "Blues")[1], high = brewer.pal(8, "Blues")[6]) +
                              scale_color_manual(values=host_order_color) +
                                make_theme(theme_name = theme_void(), setFill = F, setCol = F, guide_nrow = 1) +
                                theme(axis.text.x=element_blank(), axis.text.y=element_blank())
                                ggsave("Figures/09b-magOTUs_venn_passed_MAGs.pdf")

observations_host_all <- list(
   `Apis mellifera` = c(pivot_wider(summarise(group_by(vis_magOTUs_df_all, Host), Cluster, .groups = "keep"), names_from = Host, values_from = Cluster, values_fn = list) %>% pull(`Apis mellifera`) %>% unlist),
   `Apis cerana` = c(pivot_wider(summarise(group_by(vis_magOTUs_df_all, Host), Cluster, .groups = "keep"), names_from = Host, values_from = Cluster, values_fn = list) %>% pull(`Apis cerana`) %>% unlist),
   `Apis dorsata` = c(pivot_wider(summarise(group_by(vis_magOTUs_df_all, Host), Cluster, .groups = "keep"), names_from = Host, values_from = Cluster, values_fn = list) %>% pull(`Apis dorsata`) %>% unlist),
   `Apis florea` = c(pivot_wider(summarise(group_by(vis_magOTUs_df_all, Host), Cluster, .groups = "keep"), names_from = Host, values_from = Cluster, values_fn = list) %>% pull(`Apis florea`) %>% unlist)
)

magOTU_all_venn <- ggVennDiagram(observations_host_all) +
                    scale_fill_gradient(low = brewer.pal(8, "Blues")[1], high = brewer.pal(8, "Blues")[6]) +
                      scale_color_manual(values=host_order_color) +
                        make_theme(theme_name = theme_void(), setFill = F, setCol = F, guide_nrow = 1) +
                          theme(axis.text.x=element_blank(), axis.text.y=element_blank())
                          ggsave("Figures/09b-magOTUs_venn_all_MAGs.pdf")

observations <- vis_magOTUs_df_all %>%
                  group_by(sample) %>%
                    summarise(Cluster, .groups="keep") %>%
                      pivot_wider(names_from = sample, values_from = Cluster, values_fn = list)
df_magOTUs_vegan <- data.frame(matrix(nrow = length(samples), ncol = length(unique(vis_magOTUs_df_all$Cluster))))
rownames(df_magOTUs_vegan) <- samples
colnames(df_magOTUs_vegan) <- unique(vis_magOTUs_df_all$Cluster)

for (sample in rownames(df_magOTUs_vegan)) {
  for (cluster in colnames(df_magOTUs_vegan)) {
    if (cluster %in% observations[sample][[1]][[1]]) {
      df_magOTUs_vegan[sample, cluster] = 1
    } else {
      df_magOTUs_vegan[sample, cluster] = 0
    }
  }
}


samples_am <- c(vis_magOTUs_df_all %>% filter(Host == "Apis mellifera") %>% pull(Sample) %>% unique %>% as.vector)
samples_ac <- c(vis_magOTUs_df_all %>% filter(Host == "Apis cerana") %>% pull(Sample) %>% unique %>% as.vector)
samples_ad <-c(vis_magOTUs_df_all %>% filter(Host == "Apis dorsata") %>% pull(Sample) %>% unique %>% as.vector)
samples_af <-c(vis_magOTUs_df_all %>% filter(Host == "Apis florea") %>% pull(Sample) %>% unique %>% as.vector)


make_cum_curve <- function(samples_vector, pa_df, iterations, name = NA) {
  num_clusters_matrix <- matrix(nrow = length(samples_vector), ncol = iterations)
  for (iter in 1:iterations) {
    clusters_found_cumulative <- c()
    for (num_samples in 1:length(samples_vector)) {
      num_new_clusters = 0
      selected_samples <- sample(samples_vector, num_samples)
      clusters_found <- colnames(pa_df[selected_samples, which(colSums(pa_df[selected_samples, ]) > 1)])
      for (cluster in clusters_found) {
        if (cluster %in% clusters_found_cumulative) {
          invisible()
        } else {
          num_new_clusters <- num_new_clusters + 1
          clusters_found_cumulative <- c(clusters_found_cumulative, cluster)
        }
      }
      num_clusters_matrix[num_samples, iter] = length(clusters_found_cumulative)
    }
  }
  num_clusters_df <- as.data.frame(num_clusters_matrix)
  colnames(num_clusters_df) <- do.call(function(x) paste0("curve_", x), list(c(1:iterations)))
  num_clusters_df <- cbind(sample_size = c(1:length(samples_vector)), num_clusters_df)
  plot_cum_curve_df <- pivot_longer(num_clusters_df, !sample_size, values_to = "number_of_clusters", names_to = "curve")
  plot_cum_curve_df <- cbind("name" = name, plot_cum_curve_df)
  return(plot_cum_curve_df)
}

df_plot_cum_curve <- rbind(
                        make_cum_curve(samples_am, df_magOTUs_vegan, 50, "Apis mellifera"),
                        make_cum_curve(samples_ac, df_magOTUs_vegan, 50, "Apis cerana"),
                        make_cum_curve(samples_ad, df_magOTUs_vegan, 50, "Apis dorsata"),
                        make_cum_curve(samples_af, df_magOTUs_vegan, 50, "Apis florea")
                      )

magotu_accumulation_curve <- ggplot(data = df_plot_cum_curve, aes(x = sample_size, y = number_of_clusters, color = factor(name, host_order))) +
                      geom_jitter(position = position_dodge(width=0.7)) +
                        geom_smooth(se = FALSE) +
                          labs(color = "Host species", x = "# Bees", y = "Number of magOTUs") +
                          scale_color_manual(values=host_order_color) +
                            make_theme(leg_pos = "bottom", setCol = F, guide_nrow = 1)
                            ggsave("Figures/09c-magOTUs_accumulation_curve.pdf")

pcoa_plot_by_host <- function(df_pcoa) {
          matrix <- as.matrix(df_pcoa)
          dist <- as.dist(matrix)
          res_pcoa <- pcoa(dist)
          ev1 <- res_pcoa$vectors[,1]
          ev2 <- res_pcoa$vectors[,2]
          df_pcoa_new <- data.frame(cbind(ev1,ev2))
          df_pcoa_new$Sample <- rownames(df_pcoa_new)
          rownames(df_pcoa_new) <- NULL
          df_pcoa_new <- left_join(df_pcoa_new, select(df, Sample, SpeciesID), by = "Sample")
          perc_axis <- round(((res_pcoa$values$Relative_eig[c(1,2)])*100), digits=1)
          axis_x_title <- paste0("PCo1 (",perc_axis[1],"%)")
          axis_y_title <- paste0("PCo2 (",perc_axis[2],"%)")
          p <- ggplot(df_pcoa_new, aes(x = ev1,
                                       y = ev2,
                                       colour = factor(SpeciesID, levels = host_order)))+
                geom_point(stat="identity", size=2, shape=19) +
                  labs(x=axis_x_title, y = axis_y_title, color = "Host") +
                    make_theme(setCol = F, guide_nrow = 1) +
                      scale_color_manual(values=host_order_color)
          return(p)
}

pcoa_plot <- function(df_pcoa, variable=SpeciesID) {
          matrix <- as.matrix(df_pcoa)
          dist <- as.dist(matrix)
          res_pcoa <- pcoa(dist)
          ev1 <- res_pcoa$vectors[,1]
          ev2 <- res_pcoa$vectors[,2]
          df_pcoa_new <- data.frame(cbind(ev1,ev2))
          df_pcoa_new$Sample <- rownames(df_pcoa_new)
          rownames(df_pcoa_new) <- NULL
          df_pcoa_new <- left_join(df_pcoa_new, select(df, Sample, SpeciesID, matches(variable)), by = "Sample")
          perc_axis <- round(((res_pcoa$values$Relative_eig[c(1,2)])*100), digits=1)
          axis_x_title <- paste0("PCo1 (",perc_axis[1],"%)")
          axis_y_title <- paste0("PCo2 (",perc_axis[2],"%)")
          p <- ggplot(df_pcoa_new, aes(x = ev1,
                                       y = ev2,
                                       colour = get(variable)))+
                geom_point(stat="identity", size=2, shape=19) +
                  labs(x=axis_x_title, y = axis_y_title, color = variable) +
                    make_theme( max_colors = length(unique(df_pcoa_new[, variable])), guide_nrow = 4 )
          return(p)
}

dist_matrix <- as.matrix(vegdist(df_magOTUs_vegan, "jaccard"))

pcoa_magotus <- pcoa_plot_by_host(dist_matrix)
          ggsave("Figures/09d-magOTUs_pcoa.pdf")
```

```{r magOTU_clustering_plots,  dev = 'pdf', results='hold', fig.show = 'hold', out.width = '100%', fig.align = 'center'}
magOTU_all_venn
magOTU_passed_venn
magotu_accumulation_curve
pcoa_plot(dist_matrix, "Location_name")
  ggsave("Figures/09d-magOTUs_pcoa_location.pdf")
pcoa_plot(dist_matrix, "Colony")
  ggsave("Figures/09d-magOTUs_pcoa_colony.pdf")
pcoa_plot(dist_matrix, "Country")
  ggsave("Figures/09d-magOTUs_pcoa_country.pdf")
pcoa_plot(dist_matrix, "Run_ID")
  ggsave("Figures/09d-magOTUs_pcoa_run_id.pdf")
pcoa_magotus
anosim(df_magOTUs_vegan, df$SpeciesID, distance = "jaccard", permutations = 9999)
adonis2(dist_matrix ~ SpeciesID, data = df, permutations = 9999, method="jaccard")
plot(betadisper(vegdist(df_magOTUs_vegan, "jaccard"), group=df$SpeciesID),hull=FALSE, ellipse=TRUE)
# ggsave("Figures/09d-magOTUs_pcoa_betadisp.pdf")
```

# Next steps

It is clear that the database is not best suited for some SDPs found especially in host species other than _Apis mellifera_. So, the next step would be to implement a MAG based analysis to compare these samples. However, as the database was already shown to be well-suited for _Apis mellifera_ and _Apis cerana_, another set of analysis would compare these samples from the [publication](https://www.sciencedirect.com/science/article/pii/S0960982220305868) ([zenodo](https://zenodo.org/record/3747314#.YcGkvRPMK3I)) with the samples from India.

## Supplementary plots

# Data description

The dataset comprises samples from 4 species of honey bees sampled in India.

+ _Apis mellifera_ (5 individuals from 1 colony)
+ _Apis cerana_ (5 individuals from 3 colonies)
+ _Apis dorsata_ (5 individuals from 3 colonies)
+ _Apis florea_ (5 individuals from 3 colonies)

Some samples from older publications of the lab are also included for _Apis mellifera_ and _Apis cerana_

The data is stored in various locations as described below and backed up on the NAS.

+ **Raw data**:

	- NAS recerche:
	`/nas/FAC/FBM/DMF/pengel/spirit/D2c/aprasad/211102_Medgenome_india_samples_resequenced`
	`/nas/FAC/FBM/DMF/pengel/spirit/D2c/aprasad/211018_Medgenome_india_samples`
	(cluster - aprasad@curnagl.dcsr.unil.ch)

  -	NAS:
	`/home/aiswarya/mnt/aprasad/SPIRIT_Project/Data/RawData/211018_Medgenome_india_samples.tar.gz`
	`/home/aiswarya/mnt/aprasad/SPIRIT_Project/Data/RawData/211102_Medgenome_india_samples_resequenced.tar.gz`
	`/home/aiswarya/mnt/lab_resources/NGS_data/20211018_A01223-105-HC32VDSX2/`
	`/home/aiswarya/mnt/lab_resources/NGS_data/20211102_A01223-105-HC32VDSX2/`
	(workstation - aiswarya@130.223.110.124)

+ **Trimmed data**:

	`/work/FAC/FBM/DMF/pengel/spirit/aprasad/211018_Medgenome_india_samples/01_Trimmed/`
	`/work/FAC/FBM/DMF/pengel/spirit/aprasad/211102_Medgenome_india_samples_resequenced/01_Trimmed/`
	(cluster - aprasad@curnagl.dcsr.unil.ch)

+ **Working directory backup**:
  (need to keep up-to-date using script on the cluster `bash ~/backup_workdir.sh` and logs are writted to ~/yymmdd_backup_log on the cluster)

	`/home/aiswarya/mnt/aprasad/Backups/working_dir_backup/Cluster/211102_Medgenome_india_samples_resequenced`
	`/home/aiswarya/mnt/aprasad/Backups/working_dir_backup/Cluster/211018_Medgenome_india_samples`
  (workstation - aiswarya@130.223.110.124)

+ **Results and important intermediate files**:

	`/home/aiswarya/mnt/aprasad/SPIRIT_Project/Data/211018_Medgenome_india_analysis`
  (workstation - aiswarya@130.223.110.124)


+ **Conda installation (cluster)**:

	`/work/FAC/FBM/DMF/pengel/spirit/aprasad/Miniconda3`
  (cluster - aprasad@curnagl.dcsr.unil.ch)

### Nomenclature

There are 56 samples at the moment.

+ M1.1 - M1.5 are 5 individuals of _Apis mellifera_ from colony 1
+ Cx.1 - Cx.5 are 5 individuals of _Apis cerana_ from colony x for 3 colonies (1 - 3)
+ Dx.1 - Dx.5 are 5 individuals of _Apis dorsata_ from colony x for 3 colonies (1 - 3)
+ Fx.1 - Fx.5 are 5 individuals of _Apis florea_ from colony x for 3 colonies (1 - 3)
+ DrY2_F1 and DrY2_F2 are samples from KE's 2015 paper. _Apis mellifera_ from switzerland (Les Droites)
+ AcCh05, AcKn01 and AmAi02, AmIu02 are two samples of _Apis cerana_ and _Apis mellifera_ from different apiaries in Japan

These samples were from earlier runs:

  + **20151119_WINDU89**	20151119	Kirsten_Ellegaard	6	GTF	Illumina	100	PE	HiSeq 2500	Genomic diversity landscape of the honey bee gut microbiota (2019, NatCom)	Nurses, Year 1, Les Droites
  20160415_OBIWAN225	20160415	Kirsten_Ellegaard	12	GTF	Illumina	100	PE	HiSeq 2500	Genomic diversity landscape of the honey bee gut microbiota (2019, NatCom)	Foragers/Winterbees, Year 1, Les Droites \
  + **20161216_OBIWAN275**	20161216	Kirsten_Ellegaard	6	GTF	Illumina	100	PE	HiSeq 2500	Genomic diversity landscape of the honey bee gut microbiota (2019, NatCom)	Nurses, Year 2, Les Droites \
  + **20170310_WINDU179**	20170310	Kirsten_Ellegaard	12	GTF	Illumina	100	PE	HiSeq 2500	Genomic diversity landscape of the honey bee gut microbiota (2019, NatCom)	Foragers/Winterbees, Year 2, Les Droites (**INCLUDED FOR NOW**) \
  + **20170426_OBIWAN300**	20170426	Kirsten_Ellegaard	6	GTF	Illumina	100	PE	HiSeq 2500	Genomic diversity landscape of the honey bee gut microbiota (2019, NatCom)	Nurses, Year 2, Grammont \
  + **20170428_WINDU191**	20170428	Kirsten_Ellegaard	12	GTF	Illumina	100	PE	HiSeq 2500	Genomic diversity landscape of the honey bee gut microbiota (2019, NatCom)	Foragers/Winterbees, Year 2, Grammont \
  + **20180118_OBIWAN338-339**	20180118	Kirsten_Ellegaard	30	GTF	Illumina	100	PE	HiSeq 2500	Metagenomes of individual honey bees, subjected to dietary manipulation and kept in the lab \
  + **20180612_KE_japan_metagenomes**	20180612	Ryo_Miyasaki	40	Japan	Illumina	100	PE	HiSeq 2500	Vast differences in strain-level diversity in two closely related species of honey bees (2020, CurBiol)	Sampling and sequencing done in Japan (**INCLUDED FOR NOW**)

## Databases

### Host database

The database is named **4_host_db**.

A [paper](https://academic.oup.com/gbe/article/12/1/3677/5682415) published in Dec. 2019 a high quality [_Apis dorsata_ genome](https://www.ncbi.nlm.nih.gov/assembly/GCA_009792835.1/) as an improvement over a previous submission in 2013. The paper also mentioned studies that had previously sequenced the [_Apis florea_ genome](https://www.ncbi.nlm.nih.gov/assembly/GCA_000184785.2) in 2012, [_Apis cerana_ genome](https://www.ncbi.nlm.nih.gov/assembly/GCF_001442555.1) in 2015 (other assemblies submitted found [here](https://www.ncbi.nlm.nih.gov/assembly/organism/7460/latest/)) and [_Apis mellifera_ genome](https://www.ncbi.nlm.nih.gov/assembly/GCF_003254395.2) in 2018 (other assemblies submitted listed here). So far I have not found any whole genome assemblies of _Apis adreniformis_.

These assemblies were downloaded and concatenated to make the **4_host_db**. It contains,

+ `>apis_mellifera_2018 PRJNA471592 version Amel_Hac3.1`
+ `>Apis_cerana  PRJNA235974`
+ `>Apis_cerana_mitochondrion PRJNA235974`
+ `>Apis_florea PRJNA45871`
+ `>Apis_dorsata PRJNA174631`


### Microbiome database

The database is named **genome_db_210402**.

This database was set up by Dr Kirsten Ellegard (KE) and is described on zenodo. It uses NCBI and IMG genome assemblies. It is non-redundant and contains concatenated genomes. Located at in lab NAS directory at lab_resources/Genome_databse. In this pipeline so far, the version of the pipeline set up by KE’s community profiling pipeline.

It was downloaded by the script `download.py --genome_db` from [zenodo](https://zenodo.org/record/4661061#.YcGlSxPMK3I). This dowloads multiple directories. The Orthofider directory can be deleted as this is generated for the pipeline as needed. The bed files can be generated from gff files if desired but this was already done for the genomes of that database so was not repeated. The other files (ffn, gff) are found in the public repository from where the genome was downloaded. The faa files were reorganised in directories corresponding to their respective SDPs in order to allow the Orthofinder scripts to assign orthogroups per SDP.

These repositories follow their own annotation pipeline to generate these files. The database can also be found at `<NAS>/lab_resources/Genome_database/database_construction`. It contains 198 genomes identified by their locus tags and described in `<NAS>/lab_resources/Genome_database/database_construction/database_construction` in metadata sheets.

<!-- 2.0.5.2 honeybee_gut_microbiota_db_red
Generated by subsetting genomes and Orthofiles from genome_db_210402 for the sake of SNV analysis. So there is only one genome per SDP. The choice of which genome is made by Kirsten’s pipeline. later, review to see if it is the best choice for this pipleine as well. -->

<!-- 2.0.5.4 Orthofinder files
In preparation,
In the last step, all the database files will be generated, based on the database metadata-file (i.e. "Locustag_Phylotype_SDP_final.txt"). The following three steps must be performed:

1. Use the bash-script "get_selected_genome_files.sh" will copy the relevant genome data-files into four database dirs "faa_files", "ffn_files", "fna_files", "gff_files").
2. Generate concatenate versions of the each genome assembly fasta-file will be generated, and bed-files detailing the gene positions on these concatenate genomes are generated ("generate_bed_concat.py")
3. Infer single-copy core gene families

Make Orthofinder files from genomes in database grouped by phylotypes. There is a metafile in the database directory which was made by Gilles and was copied from his NAS directory. This is first used to rename genomes. The genomes in the database are named using locus tags. Make a script to rename them (and modify related files accordingly later).

First, get a list of all phylotypes using the output of cat all_genomes_metafile.tsv | cut -f7 | uniq. The output contains some SDP names. Replace this by the corresponding phylotype (choose more appropriate way to handle this later). The resulting list is declared as CorePhylos in the Snakefile (Not core phylotypes but rather list for core coverage calculation for all phylos!). This information is also mostly available in the metafile that comes with the database but the one copied from Gilles includes more information and also some other genomes (added by German and mentioned in all_genomes_metafile.tsv).

CorePhylos = ["Apibacter", "Bartonella", "Bifido", "Bombella", "Commensalibacter", "Firm4", "Firm5", "Frischella", "Gilliamella", "Lkunkeei", "Snodgrassella"]



Run orthofinder on the genomes grouped by phylotype. The -og flag says to stop after inferring orthogroups and avoids further unecessary computation. -f specifies to start analysis from directory containing FASTA files. Then get the single-copy core genes using the script get_single_copy.py

Next, filter and continue to re run core cov and then proceed to snv calling and filtering! -->

# Description of pipeline methods

Run entire snakemake pipeline using:

`snakemake -p --use-conda --conda-prefix /work/FAC/FBM/DMF/pengel/spirit/aprasad/Miniconda3/spirit_envs --conda-frontend conda --profile slurm --restart-times 0 --keep-going`

and if resuming a failed or stopped run, use:

`snakemake -p --use-conda --conda-prefix /work/FAC/FBM/DMF/pengel/spirit/aprasad/Miniconda3/spirit_envs --conda-frontend conda --profile slurm --restart-times 0 --keep-going --rerun-incomplete`

conda environments are all specified in `envs/` and built by snakemake under various names in `/work/FAC/FBM/DMF/pengel/spirit/aprasad/Miniconda3/spirit_envs`

Run the pipeline in the conda environment called `snakmake_with_samtools` in the cluster. It is a clone of the snakemake environment made as recommended by Snakemake [docs](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html#installation-via-conda-mamba) followed by `conda install biopython` and later `conda install samtools` in it. This is so that Kirsten's core_cov script works (specific conda environments can only be specified for rules using bash).

## Description of directory structure

Directory names are largely self-explanatory.

>`./00_rawdata`, `./01_Trimmed`, `./02_HostMapping`, `./03_MicrobiomeMapping`
>`database` contains databases to be used for mapping. It also contains `./Orthofinder` files. These are described later in the sections describing associated rules.
>`./envs` contains all yaml files required for this pipeline. They contain a list of packages needed to specify the conda environment for various rules to work within.
>`./logs` contains log files
>`./scripts` contains all scripts needed for the snakemake pipeline. Many of these scripts are adapted from Kirsten's scripts from the zenodo directories, github or from the lab_resources directories.
The **results** of the core coverage estimation are stored in,
> `./04_CoreCov_211018_Medgenome_india_samples`
> `./07_SNVProfiling` is not fully implemented (yet) for these samples as it is not relevant at this time.
>`./fastqc` contains fastqc **results** for trimmed and raw files
+ bamfile_list_red.txt - required by KE's core coverage pipeline
+ bamfile_list.txt - required by KE's core coverage pipeline
+ Adapters-PE.fa - is generated based on index sequences by the script `./scripts/write_adapters.py` (was deleted earlier as it was on scratch. Needs to be re-written.)
+ config.yaml - comprises information including list of samples
+ index_table.csv - used by the script `./scripts/write_adapters.py` to make indexed adapters
+ Mapping_summary.csv - result from the rule summarize_mapping
+ rulegraph.pdf - summary DAG of rules in the pipeline (made using `snakemake --forceall --rulegraph | dot -Tpdf > Figuers/rulegraph.pdf`)
+ Report.Rmd - this report !
+ Report.html - this report compiled !
+ Snakefile - the pipipeline !!!

## Rules

![DAG of all rules in the pipeline](Figures/rulegraph.pdf){width=65%}

+ `rule raw_qc`
  - This rule runs [fastqc](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/) on raw files and saves the output in `./fastqc/raw`.
+ `rule make_adapters`
  - This rule uses the script `_./scripts/write_adapters.py`_ which was deleted earlier.
  - It uses the index_table.csv files to make the Adapters-PE.fa file containing indexed adapters.
+ `rule trim`
  - This rules trims reads using [trimmomatic](http://www.usadellab.org/cms/uploads/supplementary/Trimmomatic/TrimmomaticManual_V0.32.pdf).
  - The _Adapters-PE.fa_ files is used.
  - The trimming parameters are.
+ `rule trim_qc`
  - This rule runs [fastqc](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/) on trimmed files and saves the output in `./fastqc/trim`.
+ `rule index_bwa`
  - Indexes genomes in `./database` for use by [bwa](http://bio-bwa.sourceforge.net/) using [bwa index](http://bio-bwa.sourceforge.net/bwa.shtml#3).
+ `rule index_samtools`
  - Indexes genomes in `./database` for use by [samtools](http://www.htslib.org/doc/#manual-pages).
+ `rule make_genome_list`
  - Creats a text file corresponding to each set of genomes in `./database` to be used when we need to know which genomes are present in given genome database.
+ `rule host_mapping`
  - Uses [bwa mem](http://bio-bwa.sourceforge.net/bwa.shtml#:~:text=BWA%20is%20a%20software%20package,such%20as%20the%20human%20genome.&text=BWA%2DMEM%20also%20has%20better,genome%20(the%20index%20command)) to map reads for each sample to a database containing host genomes, `./database/4_host_db`.
  - Unmapped reads identified by samtools with the option `-f4` are stored in a seperate bam file.
  - The bam file with all alignments is used later by the counting rule and then deleted after counting.
+ `rule host_mapping_extract_reads`
  - Reads that did not map to the host database are extracted and then mapped to the microbiome database.
  - They are extracted using [picard](https://broadinstitute.github.io/picard/).
  - The option `-Xmx8g` ensures that java is given 8 GB memory. If suffecient memory is not allocated, the job will fail.
+ `rule host_mapping_count`
  - Counts the number of mapped, properly and unmapped reads from host mapping.
  - It uses the following flags to identify each kind of read:
    - **count number of properly mapped reads: `-f 67 -F 2304`**
        - 67 (include -f) flags
            + read paired (0x1)
            + read mapped in proper pair (0x2)
            + first in pair (0x40)
        - 2308 (exclude -F) flags
            + read unmapped (0x4)
            + supplementary alignment (0x800)
            + not primary (0x100)
    - **count number of mapped reads: `-f 67 -F 2304`**
        - 65 (include -f) flags
            + read paired (0x1)
            + first in pair (0x40)
        - 2308 (exclude -F) flags
            + read unmapped (0x4)
            + supplementary alignment (0x800)
            + not primary (0x100)
    - **count number of unmapped reads: `-f 67 -F 2304`**
        - 69 (include -f) flags
            + read paired (0x1)
            + read unmapped (0x4)
            + first in pair (0x40)
        - 2304 (exclude -F) flags
            + supplementary alignment (0x800)
            + not primary (0x100)
  - After counting, the bam file is deleted and an empty file is touched to mark that counting is complete for said file.
+ `rule microbiomedb_mapping`
  - The host unmapped reads extracted earlier are mapped to the microbiome database.
  - Mapped reads are extracted using a perls script as follows. First, unmapped reads are excluded using `-F4` and then supplementary reads are excluded `-F 0x800`. Finally, the remaining reads are sent through `./scripts/filter_sam_aln_length.pl`. The script filters away reads that have less than 50bps matching in the alignment.
+ `rule microbiomedb_extract_reads`
  - Extracts mapped reads identified as mentioned in the previous rule and saves them as fastq files.
+ `rule microbiome_mapping_count`
  - Counts reads as explained in the other counting rule, _host_mapping_count_.
+ `rule cat_and_clean_counts`
  - Compiles all the counts into 1 file for easier parsing by the summarize rule.
+ `rule summarize_mapping`
  - Summarizes counts in a csv file using the results of earlier rules and by counting fastq files.
+ `rule run_orthofinder`
  - Runs [Orthofinder](https://github.com/davidemms/OrthoFinder) for each phylotype.
  - **Before** running this, group genomes by phylotype in directories for Orthofinder to be able to get which groups to consider together. When the genomes for the database are downloaded at `./database/faa_files/{genome}`, they are all in one directory. Grouping was done using `./scripts/rearange_faa.py`. As written, it is to be run from the scripts directory in which it resides (!! it uses relative paths !!).
  - faa files for each genome comes from the respective databese (NCBI for example)
  - When orthofinder finishes, the following file will be generated and used for the following steps, `./database/faa_files/{phylotype}/OrthoFinder/Results_dir/Orthogroups/Orthogroups.txt`.
  - The file _Orthogroups.txt_ contains a list of orthogroups. Eg, each line would look like
    - **OG0000003**: C4S76_01365 C4S76_01370 C4S76_01375 C4S77_06100 C4S77_06130 C4S77_06135 C4S77_06775 C4S77_06780 C4S77_06785 C4S77_06790 C4S77_06795 C4S77_06800 C4S77_06805 C4S77_06810 C4S77_09595 C4S77_09600 C4S77_09605 C4S77_09610 **C4S77_09615 C4S77_09620 C4S77_10540 Ga0307799_111506**
    - where, **OG0000003** is an orthogroup for this group of genomes (phylotype) and **C4S77**, **Ga0307799** etc. are genomes that belong to that group. **09615, 09620, 10540** are genes from **C4S77** and **111506** from **Ga0307799** that belong to orthogroup OG0000003.
+ `rule get_single_ortho`
  - The files _Orthogroups.txt_ is parsed by `./scripts/get_single_ortho.py` and single-copy orthologs are written to `./database/Orthofinder/{phylotype}_single_ortho.txt`
  - The script reads each orthogroup and counts the number of genomes present in genes of that orthogroup. If the number of genes in the orthogroup and the number of genomes in the orthogroup are the same as the total number of genomes in the database for said phylotype, the genes in the group are considered single-copy core genes and included for core coverage estimation.
+ `rule extract_orthologs`
  - This rule prepares files with sequences of orthologs in order to calculate percentage identity (perc_id).
  - First, it reads the file `./database/Orthofinder/{phylotype}_single_ortho.txt` and gets all the genome-ids present in the ortholog-file, and all the gene-ids associated with each gene-family. Using this list it extracts and stores the sequences of each of the genes of an orthogroup in an faa file and ffn file corresponding to each group in the directory`./database/Orthofinder/{phylotype}_ortho_sequences/`.
  EXAMPLE:
  - `cat ./database/Orthofinder/firm5_ortho_sequences/OG0001034.faa` \
    **\>Ga0061073_1479** \
    MTKYQTLIFVPEGSLLNEKTAEQVALRQTLKELGHDFGPAERLKYSSLQGQVKMMGFSER \
    IALTLQNFCTDDLAEAEKIFKTKLGGQRQLVKDAIPFLDQITNQVKLILLAKEERELISA \
    RLSDSELLNYFSASYFKEDFADPLPNKNVLFQIIKEQELDPDNCLVIGTDLVEEIQGAEN \
    AGLQSLWIAPKKVKMPISPRPTLHLTKLNDLLFYLELN \
    **\>Ga0070887_12184** \
    MKGKVHLAKYETLIFILEGSLLNEKVAEQNALRQTLKLTGREYGPAERIQYNSLQEKIKL \
    LGFDERIKLTLQEFFKNDWISAKGTFYNQLQKQDQLNKDVVPFLDEVKNKVNLVLLTKEK \
    KDVASYRMQNTELINYFSAVYFKDDFACKFPNKKVLITILQQQNLTPATCLVIGTNLVDE \
    IQGAENANLDSLWLAPKKVKMPISPRPTLHLNKLTDLLFYLELS \
    **\>Ga0072400_11133** \
    LAKFQTLIFILEGSLLDEKIAEQSALKQTLKSTGRDFGPSERLKYNSVRENNKLLGFEDR \
    IQLILQTFFHENWQDAGQIFIKELQKQNRLNKEVLPFLNKVNCKVKLILLAKENKKVALQ \
    RMKNTELVNYFPFAYFKDDFTEKLPHKKVLTTILQKQNLAFATSLVIGTDLADEIQAAEN \
    AKIQSLWLAPKKVKMPISPHPTLHLNKLNDLLFYLELS
  - `cat ./database/Orthofinder/firm5_ortho_sequences/OG0001034.ffa` \
    **\>Ga0061073_1479** \
    GTGACTAAATATCAAACGTTAATTTTTGTTCCTGAAGGTAGTTTATTAAATGAAAAAACG \
    GCTGAACAAGTCGCACTCAGGCAAACTTTAAAAGAACTCGGACATGATTTTGGACCAGCT \
    GAACGCCTAAAATATTCTAGCTTACAAGGACAAGTTAAAATGATGGGTTTCAGCGAGCGC \
    ATTGCACTAACCCTGCAAAATTTTTGTACCGACGATTTGGCTGAGGCCGAAAAAATTTTC \
    AAAACAAAATTAGGAGGTCAGCGACAACTAGTCAAAGATGCTATTCCATTTCTTGACCAA \
    ATAACAAACCAAGTTAAGCTAATTCTCCTTGCCAAAGAAGAACGTGAACTAATCTCAGCT \
    CGCCTATCTGATAGCGAACTACTTAACTATTTTTCTGCTTCCTATTTTAAAGAAGATTTT \
    GCTGATCCTTTGCCAAATAAAAATGTCCTGTTTCAAATTATAAAAGAGCAAGAATTAGAT \
    CCAGATAATTGCCTAGTTATCGGCACAGATTTAGTTGAAGAAATTCAAGGAGCAGAAAAC \
    GCTGGCTTGCAATCATTATGGATTGCACCAAAAAAGGTTAAAATGCCAATTAGTCCTCGA \
    CCTACTCTGCATTTAACTAAACTCAATGACTTGCTTTTTTATCTTGAATTAAACTAG \
    **\>Ga0070887_12184** \
    ATGAAAGGAAAAGTACACTTGGCAAAATATGAAACTTTAATTTTTATTCTTGAAGGAAGC \
    TTATTAAACGAAAAAGTTGCAGAACAAAATGCACTTAGGCAAACTTTGAAATTAACTGGC \
    AGAGAATATGGTCCAGCTGAGCGCATACAATATAATTCATTACAAGAAAAGATTAAATTA \
    CTAGGATTTGATGAGCGCATTAAATTAACTTTGCAGGAATTCTTTAAAAATGACTGGATT \
    TCTGCGAAAGGCACTTTTTATAACCAGTTGCAAAAACAAGATCAGTTAAATAAAGATGTA \
    GTGCCCTTTTTAGATGAGGTGAAAAACAAAGTTAACTTGGTTTTGCTGACGAAAGAGAAA \
    AAAGATGTGGCTTCATACCGCATGCAAAATACAGAGCTAATAAATTATTTTTCCGCAGTT \
    TATTTTAAAGACGATTTTGCATGTAAGTTTCCAAATAAGAAGGTTTTGATAACAATATTG \
    CAGCAGCAGAATCTGACGCCAGCCACTTGTCTTGTAATTGGGACAAACTTAGTCGATGAA \
    ATTCAGGGTGCCGAAAATGCTAACCTGGATTCTCTTTGGCTAGCGCCCAAGAAAGTAAAA \
    ATGCCAATTAGTCCACGTCCAACTTTACATTTAAATAAATTAACTGATTTATTATTTTAC \
    CTAGAATTAAGCTAG \
    **\>Ga0072400_11133** \
    TTGGCAAAATTTCAAACATTAATTTTTATTCTTGAGGGCAGTTTATTAGATGAAAAGATT \
    GCTGAACAAAGTGCATTAAAGCAAACTTTAAAGTCAACTGGCAGAGATTTTGGTCCCAGT \
    GAACGTTTAAAATATAATTCTGTACGAGAAAATAATAAGTTGCTTGGCTTTGAAGACCGC \
    ATACAATTAATTTTACAAACATTTTTTCATGAAAATTGGCAAGATGCAGGGCAGATTTTT \
    ATCAAAGAATTACAAAAGCAAAATCGCTTGAATAAAGAAGTATTGCCATTTTTAAACAAA \
    GTTAACTGCAAGGTTAAACTAATTCTGCTGGCAAAAGAGAACAAAAAAGTAGCATTACAG \
    CGCATGAAGAACACAGAGTTGGTAAATTATTTTCCGTTTGCTTATTTTAAAGATGACTTT \
    ACGGAAAAATTGCCACATAAAAAAGTTTTGACCACCATTTTGCAGAAACAAAACTTGGCG \
    TTCGCAACTAGTTTAGTAATCGGAACTGACTTAGCAGATGAAATTCAGGCTGCAGAGAAT \
    GCCAAAATACAGTCACTCTGGCTAGCGCCTAAGAAAGTAAAAATGCCGATTAGCCCGCAC \
    CCAACTTTACATTTAAATAAATTAAACGATTTATTATTTTACCTAGAATTAAGCTAG
+ `rule calc_perc_id`
  - this rule relies on various tools and scripts tied together by `./scripts/aln_calc.sh`. The scripts are:
    + [mafft](https://mafft.cbrc.jp/alignment/software/manual/manual.html#index) for alignment
      + The aligned result is in a multi-fasta file called {OrthogroupID}_aln.fasta.
      EXAMPLE:
      + `cat ./database/Orthofinder/firm5_ortho_sequences/OG0001034_aln.fasta` \
        **\>Ga0061073_1479** \
        -------MTKYQTLIFVPEGSLLNEKTAEQVALRQTLKELGHDFGPAERLKYSSLQGQVK \
        MMGFSERIALTLQNFCTDDLAEAEKIFKTKLGGQRQLVKDAIPFLDQIT---NQVKLILL \
        AKEERELISARLSDSELLNYFSASYFKEDFADPLPNKNVLFQIIKEQELDPDNCLVIGTD \
        LVEEIQGAENAGLQSLWIAPKKVKMPISPRPTLHLTKLNDLLFYLELN \
        **\>Ga0070887_12184** \
        M-KGKVHLAKYETLIFILEGSLLNEKVAEQNALRQTLKLTGREYGPAERIQYNSLQEKIK \
        LLGFDERIKLTLQEFFKNDWISAKGTFYNQLQKQDQLNKDVVPFLDEVK---NKVNLVLL \
        TKEKKDVASYRMQNTELINYFSAVYFKDDFACKFPNKKVLITILQQQNLTPATCLVIGTN \
        LVDEIQGAENANLDSLWLAPKKVKMPISPRPTLHLNKLTDLLFYLELS \
        **\>Ga0072400_11133** \
        -------LAKFQTLIFILEGSLLDEKIAEQSALKQTLKSTGRDFGPSERLKYNSVRENNK \
        LLGFEDRIQLILQTFFHENWQDAGQIFIKELQKQNRLNKEVLPFLNKVN---CKVKLILL \
        AKENKKVALQRMKNTELVNYFPFAYFKDDFTEKLPHKKVLTTILQKQNLAFATSLVIGTD \
        LADEIQAAENAKIQSLWLAPKKVKMPISPHPTLHLNKLNDLLFYLELS
    + **aln_aa_to_dna.py**
      + This scripts converts the alignments into nucleotide sequences rather than amino acid sequences
      EXAMPLE:
      + `cat ./database/Orthofinder/firm5_ortho_sequences/OG0001034_aln.fasta`
      **\>Ga0061073_1479** \
      ---------------------GTGACTAAATATCAAACGTTAATTTTTGTTCCTGAAGGT \
      AGTTTATTAAATGAAAAAACGGCTGAACAAGTCGCACTCAGGCAAACTTTAAAAGAACTC \
      GGACATGATTTTGGACCAGCTGAACGCCTAAAATATTCTAGCTTACAAGGACAAGTTAAA \
      ATGATGGGTTTCAGCGAGCGCATTGCACTAACCCTGCAAAATTTTTGTACCGACGATTTG \
      GCTGAGGCCGAAAAAATTTTCAAAACAAAATTAGGAGGTCAGCGACAACTAGTCAAAGAT \
      GCTATTCCATTTCTTGACCAAATAACA---------AACCAAGTTAAGCTAATTCTCCTT \
      GCCAAAGAAGAACGTGAACTAATCTCAGCTCGCCTATCTGATAGCGAACTACTTAACTAT \
      TTTTCTGCTTCCTATTTTAAAGAAGATTTTGCTGATCCTTTGCCAAATAAAAATGTCCTG \
      TTTCAAATTATAAAAGAGCAAGAATTAGATCCAGATAATTGCCTAGTTATCGGCACAGAT \
      TTAGTTGAAGAAATTCAAGGAGCAGAAAACGCTGGCTTGCAATCATTATGGATTGCACCA \
      AAAAAGGTTAAAATGCCAATTAGTCCTCGACCTACTCTGCATTTAACTAAACTCAATGAC \
      TTGCTTTTTTATCTTGAATTAAAC \
      **\>Ga0070887_12184** \
      ATG---AAAGGAAAAGTACACTTGGCAAAATATGAAACTTTAATTTTTATTCTTGAAGGA \
      AGCTTATTAAACGAAAAAGTTGCAGAACAAAATGCACTTAGGCAAACTTTGAAATTAACT \
      GGCAGAGAATATGGTCCAGCTGAGCGCATACAATATAATTCATTACAAGAAAAGATTAAA \
      TTACTAGGATTTGATGAGCGCATTAAATTAACTTTGCAGGAATTCTTTAAAAATGACTGG \
      ATTTCTGCGAAAGGCACTTTTTATAACCAGTTGCAAAAACAAGATCAGTTAAATAAAGAT \
      GTAGTGCCCTTTTTAGATGAGGTGAAA---------AACAAAGTTAACTTGGTTTTGCTG \
      ACGAAAGAGAAAAAAGATGTGGCTTCATACCGCATGCAAAATACAGAGCTAATAAATTAT \
      TTTTCCGCAGTTTATTTTAAAGACGATTTTGCATGTAAGTTTCCAAATAAGAAGGTTTTG \
      ATAACAATATTGCAGCAGCAGAATCTGACGCCAGCCACTTGTCTTGTAATTGGGACAAAC \
      TTAGTCGATGAAATTCAGGGTGCCGAAAATGCTAACCTGGATTCTCTTTGGCTAGCGCCC \
      AAGAAAGTAAAAATGCCAATTAGTCCACGTCCAACTTTACATTTAAATAAATTAACTGAT \
      TTATTATTTTACCTAGAATTAAGC \
      **\>Ga0072400_11133** \
      ---------------------TTGGCAAAATTTCAAACATTAATTTTTATTCTTGAGGGC \
      AGTTTATTAGATGAAAAGATTGCTGAACAAAGTGCATTAAAGCAAACTTTAAAGTCAACT \
      GGCAGAGATTTTGGTCCCAGTGAACGTTTAAAATATAATTCTGTACGAGAAAATAATAAG \
      TTGCTTGGCTTTGAAGACCGCATACAATTAATTTTACAAACATTTTTTCATGAAAATTGG \
      CAAGATGCAGGGCAGATTTTTATCAAAGAATTACAAAAGCAAAATCGCTTGAATAAAGAA \
      GTATTGCCATTTTTAAACAAAGTTAAC---------TGCAAGGTTAAACTAATTCTGCTG \
      GCAAAAGAGAACAAAAAAGTAGCATTACAGCGCATGAAGAACACAGAGTTGGTAAATTAT \
      TTTCCGTTTGCTTATTTTAAAGATGACTTTACGGAAAAATTGCCACATAAAAAAGTTTTG \
      ACCACCATTTTGCAGAAACAAAACTTGGCGTTCGCAACTAGTTTAGTAATCGGAACTGAC \
      TTAGCAGATGAAATTCAGGCTGCAGAGAATGCCAAAATACAGTCACTCTGGCTAGCGCCT \
      AAGAAAGTAAAAATGCCGATTAGCCCGCACCCAACTTTACATTTAAATAAATTAAACGAT \
      TTATTATTTTACCTAGAATTAAGC
    + **trim_aln.py** and `sed` to simplify headers to contain just genome ID and leave out gene identifier (as they are all single copy core genes).
      + This script trims out all the sections that do not align by counting which positions have "-" and removing those from all the members of the orthogroup.
      + `cat ./database/Orthofinder/firm5_ortho_sequences/OG0001034_aln_trim.fasta` \
        **\>Ga0061073** \
        GTGACTAAATATCAAACGTTAATTTTTGTTCCTGAAGGTAGTTTATTAAATGAAAAAACG \
        GCTGAACAAGTCGCACTCAGGCAAACTTTAAAAGAACTCGGACATGATTTTGGACCAGCT \
        GAACGCCTAAAATATTCTAGCTTACAAGGACAAGTTAAAATGATGGGTTTCAGCGAGCGC \
        ATTGCACTAACCCTGCAAAATTTTTGTACCGACGATTTGGCTGAGGCCGAAAAAATTTTC \
        AAAACAAAATTAGGAGGTCAGCGACAACTAGTCAAAGATGCTATTCCATTTCTTGACCAA \
        ATAACAAACCAAGTTAAGCTAATTCTCCTTGCCAAAGAAGAACGTGAACTAATCTCAGCT \
        CGCCTATCTGATAGCGAACTACTTAACTATTTTTCTGCTTCCTATTTTAAAGAAGATTTT \
        GCTGATCCTTTGCCAAATAAAAATGTCCTGTTTCAAATTATAAAAGAGCAAGAATTAGAT \
        CCAGATAATTGCCTAGTTATCGGCACAGATTTAGTTGAAGAAATTCAAGGAGCAGAAAAC \
        GCTGGCTTGCAATCATTATGGATTGCACCAAAAAAGGTTAAAATGCCAATTAGTCCTCGA \
        CCTACTCTGCATTTAACTAAACTCAATGACTTGCTTTTTTATCTTGAATTAAAC \
        **\>Ga0070887** \
        TTGGCAAAATATGAAACTTTAATTTTTATTCTTGAAGGAAGCTTATTAAACGAAAAAGTT \
        GCAGAACAAAATGCACTTAGGCAAACTTTGAAATTAACTGGCAGAGAATATGGTCCAGCT \
        GAGCGCATACAATATAATTCATTACAAGAAAAGATTAAATTACTAGGATTTGATGAGCGC \
        ATTAAATTAACTTTGCAGGAATTCTTTAAAAATGACTGGATTTCTGCGAAAGGCACTTTT \
        TATAACCAGTTGCAAAAACAAGATCAGTTAAATAAAGATGTAGTGCCCTTTTTAGATGAG \
        GTGAAAAACAAAGTTAACTTGGTTTTGCTGACGAAAGAGAAAAAAGATGTGGCTTCATAC \
        CGCATGCAAAATACAGAGCTAATAAATTATTTTTCCGCAGTTTATTTTAAAGACGATTTT \
        GCATGTAAGTTTCCAAATAAGAAGGTTTTGATAACAATATTGCAGCAGCAGAATCTGACG \
        CCAGCCACTTGTCTTGTAATTGGGACAAACTTAGTCGATGAAATTCAGGGTGCCGAAAAT \
        GCTAACCTGGATTCTCTTTGGCTAGCGCCCAAGAAAGTAAAAATGCCAATTAGTCCACGT \
        CCAACTTTACATTTAAATAAATTAACTGATTTATTATTTTACCTAGAATTAAGC \
        **\>Ga0072400** \
        TTGGCAAAATTTCAAACATTAATTTTTATTCTTGAGGGCAGTTTATTAGATGAAAAGATT \
        GCTGAACAAAGTGCATTAAAGCAAACTTTAAAGTCAACTGGCAGAGATTTTGGTCCCAGT \
        GAACGTTTAAAATATAATTCTGTACGAGAAAATAATAAGTTGCTTGGCTTTGAAGACCGC \
        ATACAATTAATTTTACAAACATTTTTTCATGAAAATTGGCAAGATGCAGGGCAGATTTTT \
        ATCAAAGAATTACAAAAGCAAAATCGCTTGAATAAAGAAGTATTGCCATTTTTAAACAAA \
        GTTAACTGCAAGGTTAAACTAATTCTGCTGGCAAAAGAGAACAAAAAAGTAGCATTACAG \
        CGCATGAAGAACACAGAGTTGGTAAATTATTTTCCGTTTGCTTATTTTAAAGATGACTTT \
        ACGGAAAAATTGCCACATAAAAAAGTTTTGACCACCATTTTGCAGAAACAAAACTTGGCG \
        TTCGCAACTAGTTTAGTAATCGGAACTGACTTAGCAGATGAAATTCAGGCTGCAGAGAAT \
        GCCAAAATACAGTCACTCTGGCTAGCGCCTAAGAAAGTAAAAATGCCGATTAGCCCGCAC \
        CCAACTTTACATTTAAATAAATTAAACGATTTATTATTTTACCTAGAATTAAGC
    + **calc_perc_id_orthologs.py**
      + Uses as input, trimmed aligned sequences and a metafile (`./database/genome_db_210402_metafile.txt`) which is a tab-delim file with genome-id in tab1 and SDP-affiliation in tab 3
      + First, it checks the number of SDPs contained within the alignment. If more than one, it continues by calculating alignment percentage identity stats across SDPs. If only one SDP, exits script.
      + Next, it Compares the genomes in each SDP to all other genomes in the alignment: calculates percentage identity for all pairwise combinations. Calculates the max, min, and mean values, prints to file `./database/Orthofinder/{phylotype}_perc_id.txt` showing one orthogroup per line.
      EXAMPLE:
      + `cat ./database/Orthofinder/firm5_perc_id.txt` \
        ... \
        OG0001034	0.674	0.586	0.972 \
        ... \

+ `rule filter_orthogroups`
  - orthogroups are filtered based on:
    - Minimum gene-length 300bp (applied to all members of each gene-family)
    - Inter-SDP max alignment identity 95% (only if the phylotype contain multiple SDPs)
  - Short genes are filtered off, because they are likley to be less reliable for accurate coverage estimates. Similarly, the inter-SDP similarity threshold is used to ensure that there is enough divergence between the SDPs for reliable mapping (at least as estimated from the currently availabe genomes). It is worthwhile to check the number of gene-families before/after filtering. If a lot of gene-families were filtered off, this could be an indication that the SDPs are not properly discrete.
  - This finally results in the single-copy core genes that have been filtered to be used for core coverage estimation. `./database/Orthofinder/{phylotype}_single_ortho_filt.txt`.
+ `rule core_cov`
  - takes as input bam files with the alignments for each sample to be considered (as a text file containing a list of these files) and the _\_single_ortho_filt_ file. Outputs are written to `./04_CoreCov_"+ProjectIdentifier+"/{phylotype}_corecov.txt`.
  - The script reads the filtered orthofile `./database/Orthofinder/{phylotype}_single_ortho_filt.txt` and gets the gene-famililes and genome-ids for each SDP.
  - Then, from bed files, it finds the start and end positions of each of the genes in an orthogroup for each of the genomes of the orthogroup. It writes these to the file, `./04_CoreCov_*/{phylotype}_corecov.txt` each SDP in the phylotype, start position for each gene family in the genome marked reference for that SDP.
  - The coverage is also written to this file.
  Example:
    + SDP	Sample	OG	Ref_pos	Coverage \
      firm5_1	DrY1_N1_microbiome_mapped	OG0000932	448	18.81 \
      firm5_1	DrY1_N1_microbiome_mapped	OG0000931	1991	23.34 \
      ... \
      firm5_2	M1.5_microbiome_mapped	OG0000935	1852405	12.29 \
      firm5_2	M1.5_microbiome_mapped	OG0000934	1853270	9.95 \
      firm5_3	DrY1_N1_microbiome_mapped	OG0000932	1	501.61 \
      firm5_3	DrY1_N1_microbiome_mapped	OG0000931	1542	534.77 \
      ... \
      firm5_bombus	M1.5_microbiome_mapped	OG0000936	1674767	0.0 \
      firm5_bombus	M1.5_microbiome_mapped	OG0000935	1676256	0.0 \
      firm5_bombus	M1.5_microbiome_mapped	OG0000934	1677124	0.0
  - SDP abundance is estimated based on mapped read coverage of core genes. It sums up gene coverages of all the genes og OG families associated with said SDP across genomes belogining to the SDP.
  - It also reports PTR (Peak-Trough Ratio).
  - Most species in the database are represented by multiple genomes (< 98.5% gANI between genomes). Core genes are inferred at the phylotype. More accurate estimates can be obtained by using a large number (+700) of core genes.
+ `rule core_cov_plots`
  - This R-script will estimate the coverage at the terminus, using the summed core gene family coverages. If the cov-ter cannot be properly estimated (fx. due to draft genome status or lack of replication), an estimate will be generated using the median coverage across core gene families, and the PTR is set to NA. If more than 20\% of the core gene families have no coverage, the abundance will be set to zero. As output, a tabular file is generated (including the cov-ter/median cov, and PTR), and a pdf-file with plots for visual validation.
  - First, filter for samples with coverage of at least 1 on > 80% of the core genes. Next, values that are deviating no more than 2 times the median are kept others are discarded as outliers.
  - Next, gets fitted coordinates and append values to coord-table. It does this by using the segmented package. As explained below,

```{r eval=FALSE, echo=TRUE}
    x <- data_filt$Ref_pos
 	  y <- data_filt$Coverage
 	  psi_est <- max(x)/2
    lin.mod = y ~ x
    segmented(lin.mod, seg.Z=~x, psi=psi_est)
```
where, `lin.mod` is a simple linear model that was made by base R. The R package `Segmented` supports breakpoint analysis. The methods used by this package are applicable when segments are (nearly continuous) so this means that for the regression to make sense the core gene families selected should cover the reference genome well and without too many huge gaps. `psi`, is a starting value of the breakpoint. Example of a model fit using segemented,
```{r eval=FALSE, echo=TRUE}
    Call: segmented.lm(obj = lin.mod, seg.Z = ~x, psi = psi_est)

    Meaningful coefficients of the linear terms:
    (Intercept)            x         U1.x
      1.332e+02   -5.984e-05    1.243e-04

    Estimated Break-Point(s):
    psi1.x
    860065
```
`x` is the slope of the first segment and `U1.x` is the difference in slopes between the first and second segment. `psi_est` is the newly estimated breakpoint. This along with the slopes
    - The summary function shows:
```{r eval=FALSE, echo=TRUE}
***Regression Model with Segmented Relationship(s)***

Call:
segmented.lm(obj = lin.mod, seg.Z = ~x, psi = psi_est)

Estimated Break-Point(s):
    Est.   St.Err
psi1.x 860065 9421.565

Meaningful coefficients of the linear terms:
    Estimate Std. Error t value Pr(>|t|)
(Intercept)  1.332e+02  9.672e-01  137.75   <2e-16 ***
x           -5.984e-05  1.782e-06  -33.57   <2e-16 ***
U1.x         1.243e-04  2.688e-06   46.24       NA
---
Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1

Residual standard error: 8.804 on 750 degrees of freedom
Multiple R-Squared: 0.7417,  Adjusted R-squared: 0.7407

Convergence attained in 3 iter. (rel. change 2.8661e-06)
```
Finally, from the segmented model the ptr is calculated as follows:
```{r eval=FALSE, echo=TRUE}
cov_ter <- round(slope1*psi + intercept1, digits=1)
cov_ori2  <- slope2*(tail(x, n=1)) + intercept2
max_ori_cov <- max(intercept1, cov_ori2)
min_ori_cov <- min(intercept1, cov_ori2)
if ((psi<psi_min) || (psi>psi_max) || (min_ori_cov<cov_ter)){
    ptr <- NA
}  else {
    ptr <- round(max_ori_cov/cov_ter, digits=2)
}

# where,
psi <- (summary.segmented(seg.mod)[[12]])[2]
psi_est <- max(x)/2
psi_est <- max(x)/2
psi_min <- psi_est-(0.5*psi_est)
psi_max <- psi_est+(0.5*psi_est)
```
For `cor_ter` is the coverage $y = ax + b$ where x is psi (the breakpoint on the x axis) and the `cor_ori2` is the coverage at the ori which is the section with maximum coverage and at the `tail`. The condition `(psi<psi_min) || (psi>psi_max) || (min_ori_cov<cov_ter)` checks: **First**; If the break-point is too far from the expected place (+/-50% of break-point estimate), ptr is set to `NA`. **Second**; If the coverage at ori (either beginning or end of dataframe) is lower than the estimated coverage at ter, ptr is also set to `NA`. Finally, if the coverage of the origin is not greater than the terminus, ptr is set to `NA`.

  - the PTR was set to `NA`, the median will be plotted and used for quantification. Else, the segmented regression line is plotted, and the terminus coverage is used for quantification.

+ rule assemble_host_unmapped
  - Takes as input the R1 and R2 reads that were not mapped to the host and assembles them using [spades](https://cab.spbu.ru/software/meta-spades/) with the `--meta` tag and default parameters.
  - Memory allocation is not obvious. More documentation on this soon.
+ rule map_to_assembly
  - Map reads that were assembled against the contigs that they were assembled into using [bwa mem](http://bio-bwa.sourceforge.net).
+ rule cat_and_clean_counts_assembly
  - Compiles counts into one file for summarizing
+ rule summarize_mapping_assembly
  - similar to earlier rule "summarize_mapping"
+ rule backmapping
  - NxN mapping for
+ rule merge_depths
+ rule binning
+ rule process_metabat2
+ rule checkm_evaluation
+ rule prepare_info_for_drep
+ rule drep
+ rule gtdb_annotate
+ rule compile_report
+ rule backup
<!-- + `rule assemble_host_unmapped`
+ `rule mapping_red_db`
+ `rule subset_ortho_and_meta`
+ `rule core_cov_red`
+ `rule core_cov_red_plots`
+ `rule parse_core_cov_red`
+ `rule de_duplicate`
+ `rule freebayes_profiling`
+ `rule vcf_summary_stats`
+ `rule vcf_filtering1`
+ `rule vcf_filtering2`
+ `rule vcf_filtering3` -->
+ `rule onsuccess`

## Scripts

+ `aln_aa_to_dna.py`
+ `aln_calc.sh`
+ `calc_perc_id_orthologs.py`
+ `core_cov.py`
+ `core_cov.R`
+ `download_data.py`
+ `extract_orthologs.py`
+ `fasta_generate_regions.py`
+ `filter_bam.py`
+ `filter_orthologs.py`
+ `filter_sam_aln_length.pl`
+ `filter_sam_aln_length_unmapped.pl`
+ `filter_snvs.pl`
+ `filt_vcf_samples.pl`
+ `get_single_ortho.py`
+ `parse_core_cov.py`
+ `parse_spades_metagenome.pl`
+ `rearange_faa.py`
+ `subset_orthofile.py`
+ `trim_aln.py`
+ `./scripts/write_adapters.py`

## Envs


`core-cov-env.yaml`

```{yaml echo=TRUE}
name: core-cov-env

channels:

  - bioconda
  - conda-forge

dependencies:
  - python=3.*
  - samtools
  - bwa
  - mafft
  - orthofinder
  - biopython
  - r-base=3.5.1
  - r-plyr=1.8.6
  - r-segmented=1.1_0
  - r-cairo
```

`mapping-env.yaml`

```{yaml echo=TRUE}
name: mapping-env

channels:
  - bioconda
  - conda-forge
  - hcc

dependencies:
  - python=3.9.7
  - openjdk=11.0.9.1
  - perl=5.32.1=0_h7f98852_perl5
  - samtools=1.13=h8c37831_0
  - picard=2.26.2=hdfd78af_0
  - bwa=0.7.17=h5bf99c6_8
```

`rmd-env.yaml`

```{yaml echo=TRUE}
name: rmd-env

channels:
  - bioconda
  - conda-forge

dependencies:
  - r-base
  - r-rmarkdown
  - r-ggplot2
  - r-kableExtra
  - r-codetools
  - r-tidyverse
  - r-prettydoc
  - r-viridis
  - r-hrbrthemes
  - r-ggthemes
  - r-RColorBrewer
  - r-scales
  - r-segmented
  - r-shiny
  - r-dplyr
  - r-xlsx
  - r-DT
  - r-leaflet
```

`snv-env.yaml`

```{yaml echo=TRUE}
name: snv-env

channels:
  - bioconda
  - conda-forge
  - hcc

dependencies:
  - freebayes
  - vcftools
  - vcflib
```

`trim-qc-env.yaml`

```{yaml echo=TRUE}
name: trim-qc-env

channels:
  - bioconda
  - conda-forge
  - hcc

dependencies:
  - python
  - trimmomatic
  - fastqc
  - quast
```
