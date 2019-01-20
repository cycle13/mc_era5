# !!!IMPORTANT!!!
# make should be run in the appropriate python (conda) environment!
# CONDA_ACTIVATE=conda activate clim
# CONDA_DEACTIVATE=conda deactivate
EXEC_NB=python execute_notebook.py

CODE_DIR=code
FIG_DIR=figures
DATA_DIR=data

FIGURES=\
    $(FIG_DIR)/era5_vs_interim_accacia_case_vort_wspd.pdf \
    $(FIG_DIR)/test1.png

SCRIPTS=\
    $(CODE_DIR)/ACCACIA-Case-Example.ipynb

DATA_IN=\
    $(DATA_DIR)/tracks/stars/PolarLow_tracks_North_2002_2011

$(FIG_DIR)/era5_vs_interim_accacia_case_vort_wspd.pdf: $(CODE_DIR)/ACCACIA-Case-Example.ipynb
$(FIG_DIR)/test1.png: $(CODE_DIR)/Untitled1.ipynb


all: $(FIGURES)

$(FIGURES):
	@echo "making figure: $@"
	$(EXEC_NB) $<

.PHONY: clean help
clean:
	@echo "Cleaning..."
	rm -f $(FIG_DIR)/*

help:
	@echo ""
	@echo "Usage:"
	@echo "    make all: run Jupyter Notebooks to create all figures"
	@echo "    make clean: Delete files in figures/ folder"
	@echo "    make help: Print this message and exit"
	@echo ""
