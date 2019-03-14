# !!!IMPORTANT!!!
# make should be run in the appropriate python (conda) environment!
# CONDA_ACTIVATE=conda activate clim
# CONDA_DEACTIVATE=conda deactivate
EXEC_NB=python execute_notebook.py

CODE_DIR=code
FIG_DIR=figures
DATA_DIR=data

FIGURES=\
    $(FIG_DIR)/ascat_era5_interim_accacia_case_vort_wspd.pdf \
    $(FIG_DIR)/vrf__vort_thresh__tfreq__bs2000_100.pdf \
    $(FIG_DIR)/characteristic_histograms.pdf \
    $(FIG_DIR)/density_maps__track_genesis_lysis.pdf

DATA_IN=\
    $(DATA_DIR)/tracks/stars/PolarLow_tracks_North_2002_2011

$(FIG_DIR)/ascat_era5_interim_accacia_case_vort_wspd.pdf: $(CODE_DIR)/ACCACIA-Case-Example.ipynb
$(FIG_DIR)/vrf__vort_thresh__tfreq__bs2000_100.pdf: $(CODE_DIR)/Verification.ipynb
$(FIG_DIR)/characteristic_histograms.pdf: $(CODE_DIR)/Characteristics.ipynb
$(FIG_DIR)/density_maps__track_genesis_lysis.pdf: $(CODE_DIR)/Density-Maps.ipynb


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
