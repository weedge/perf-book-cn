#!/bin/bash
# bibtex to markdown for cite(reference)

# https://pandoc.org/MANUAL.html

# wget https://raw.githubusercontent.com/dendibakh/perf-book/main/biblio.bib -O references.bib

#pandoc -t markdown_strict \
#    --filter=pandoc-citeproc pandoc-bib-ref.md \
#    --bibliography references.bib \
#    -o ./zh/chapters/References.md

pandoc -t gfm \
    --filter=pandoc-citeproc pandoc-bib-ref.md \
    --bibliography references.bib \
    | sed 's/<\/div>//g' \
    | sed 's/id="ref-/id="/g' \
    > ./zh/chapters/References.md

# cite table
#python3 bib2markdown.py references.bib > ./zh/chapters/References.md