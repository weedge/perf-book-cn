#!/bin/bash
# https://pandoc.org/MANUAL.html

# todo: loop chapters dir

pandoc -f markdown -t gfm \
    ./zh/chapters/8-Optimizing-Memory-Accesses/8-4_Reducing_DTLB_misses_cn.md \
    -o ./zh/chapters/8-Optimizing-Memory-Accesses/8-4_Reducing_DTLB_misses_cn_md.md

