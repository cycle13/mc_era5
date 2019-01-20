# !!!IMPORTANT!!!
# make should be run in the appropriate python (conda) environment!
# CONDA_ACTIVATE=conda activate clim
# CONDA_DEACTIVATE=conda deactivate
EXEC_NB=python execute_notebook.py

CODE_DIR=code
FIG_DIR=figures
DATA_DIR=data

FIGURES=\
    $(FIG_DIR)/test1.png \
    $(FIG_DIR)/test2.png

SCRIPTS=\
    $(CODE_DIR)/Untitled1.ipynb

DATA_IN=\
    $(DATA_DIR)/tracks/stars/PolarLow_tracks_North_2002_2011


all: $(FIGURES)

$(FIGURES): $(SCRIPTS) $(DATA_IN)
	@echo "in figures" 
	$(foreach scr,$<,$(EXEC_NB) $(scr);)

#new: $(outnew)
#	@xdg-open $(outnew) > /dev/null 2>&1
#
#$(outnew) : $(srcnew)
#	$(TEX) $(filter-out $<,$^ ) -o $@ --template=$< $(FLAGS)


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
