LATEXMK ?= latexmk
BUILD_DIR := ../build
OUTPUT_DIR := ../../output/pdf
TEX := solver_analysis.tex
PDF := solver_analysis.pdf

.PHONY: all clean

all:
	mkdir -p $(BUILD_DIR) $(OUTPUT_DIR)
	$(LATEXMK) -xelatex -interaction=nonstopmode -halt-on-error \
		-outdir=$(BUILD_DIR) $(TEX)
	cp $(BUILD_DIR)/$(PDF) $(PDF)
	cp $(BUILD_DIR)/$(PDF) $(OUTPUT_DIR)/$(PDF)

clean:
	$(LATEXMK) -C -outdir=$(BUILD_DIR) $(TEX)
	rm -f $(PDF)
