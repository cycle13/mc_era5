# -*- coding: utf-8 -*-
"""
Paths to data

Depends on path.py package
"""
from pathlib import Path

# Top-level directory containing code and data (one level up)
topdir = Path('.').absolute().parent

# Local data
accdir = topdir/'data'/'tracks'/'accacia'
acctracks = accdir/'pmc_loc_time_ch4_20Mar-02Apr.txt'
starsdir = topdir/'data'/'tracks'/'stars'
starstracks = starsdir/'PolarLow_tracks_North_2002_2011'

# Temporary
phddir = Path.home()/'phd'
plotdir = phddir/'plots'/'climatology'
trackresdir = phddir/'pmc_tracking'/'results'
procdir = phddir/'pmc_tracking'/'results'/'processed_data'
runsgridfile = trackresdir/'runs_grid.json'

# Output directories
# plotdir = topdir/'figures'

# Reanalyses
era5_dir = phddir/'reanalysis'/'era5'
interim_dir = phddir/'reanalysis'/'interim'
