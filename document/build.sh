#!/bin/bash

pandoc manual.md -o ../***REMOVED***_说明书.pdf --pdf-engine=xelatex -f markdown-implicit_figures
pandoc report.md -o ../***REMOVED***_报告.pdf --pdf-engine=xelatex -f markdown-implicit_figures
