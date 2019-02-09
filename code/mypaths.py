# -*- coding: utf-8 -*-
"""Paths to data."""
from os import getenv
from pathlib import Path


# Top-level directory containing code and data (one level up)
topdir = Path(__file__).absolute().parent.parent

# Local data
accdir = topdir / "data" / "tracks" / "accacia"
acctracks = accdir / "pmc_loc_time_ch4_20Mar-02Apr.txt"
starsdir = topdir / "data" / "tracks" / "stars"
starstracks = starsdir / "PolarLow_tracks_North_2002_2011"

# External data
if getenv("HOSTNAME", "") in [None, "postproc", "xcslc0", "xcslc1"]:
    datadir = Path("/projects/accacia/deser")
    trackresdir = datadir / "pmctrack" / "output"
    procdir = datadir / "pmctrack" / "processed_data"
else:
    datadir = Path.home() / "phd"
    trackresdir = datadir / "pmc_tracking" / "results"
    procdir = datadir / "pmc_tracking" / "results" / "processed_data"
runsgridfile = trackresdir / "runs_grid.json"

# Output directories
plotdir = topdir / "figures"

# Reanalyses
ra_dir = datadir / "reanalysis"
era5_dir = ra_dir / "era5"
interim_dir = ra_dir / "interim"
