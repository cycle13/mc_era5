#!/usr/bin/env python3
"""Categorise selected runs and serialise TrackRun object for later use."""
import argparse
import sys
from functools import partial
from pathlib import Path
from textwrap import dedent

from loguru import logger

import numpy as np

from octant.core import TrackRun
from octant.decor import get_pbar
from octant.misc import check_by_mask

import xarray as xr

from common_defs import bbox, columns, period, winters
import mypaths

# Select runs
# runs2process = dict(era5=[0])  # , interim=[100, 106])
SCRIPT = Path(__file__).stem
lsm_paths = {"era5": mypaths.era5_dir / "lsm.nc", "interim": mypaths.interim_dir / "lsm.nc"}


def parse_args(args=None):
    """Parse command line arguments."""
    epilog = dedent(
        f"""Example of use:
    ./{SCRIPT} -n era5 --runs 0,3,10,11 -ll 10,20,65,85
    """
    )
    ap = argparse.ArgumentParser(
        SCRIPT,
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=epilog,
    )

    ap.add_argument(
        "-n",
        "--name",
        type=str,
        required=True,
        choices=["era5", "interim"],
        help="Name of the dataset",
    )
    ap.add_argument(
        "-r",
        "--runs",
        type=str,
        required=True,
        help="Run numbers, comma- or dash-separated (inclusive range)",
    )

    ag_sub = ap.add_argument_group(title="Subset")
    ag_sub.add_argument(
        "-ll",
        "--lonlat",
        type=str,
        default=",".join([str(i) for i in bbox]),
        help=("Lon-lat bounding box (lon0,lon1,lat0,lat1)"),
    )

    ag_etc = ap.add_argument_group(title="Other")
    ag_etc.add_argument(
        "--progressbar", action="store_true", help=("Show progress bar if available")
    )

    return ap.parse_args(args)


def get_lsm(path_to_file, bbox=None, shift=False):
    """Load land-sea mask from a file and crop a region defined by `bbox`."""
    # Load land-sea mask
    lsm = xr.open_dataarray(path_to_file).squeeze()
    if shift:
        # Shift longitude coordinate from (0, 359) to (-180, 179)
        lsm = lsm.assign_coords(longitude=(((lsm.longitude + 180) % 360) - 180)).sortby("longitude")
    if bbox is not None:
        # Select a subset of longitudes and latitudes to speed up categorisation
        lsm = lsm.sel(
            longitude=(lsm.longitude >= bbox[0]) & (lsm.longitude <= bbox[1]),
            latitude=(lsm.latitude >= bbox[2]) & (lsm.latitude <= bbox[3]),
        )
    # Set all non-zero values to 1 to make it the mask binary (0 or 1)
    lsm = lsm.where(lsm == 0, 1)
    
    lsm.attrs['units'] = 1

    return lsm


def main(args=None):
    """Loop over track runs and categorise them according `cat_kw`."""
    args = parse_args(args)

    if args.progressbar:
        from octant import RUNTIME

        RUNTIME.enable_progress_bar = True
    pbar = get_pbar()

    if "-" in args.runs:
        _start, _end = args.runs.split("-")
        runs = [*range(int(_start), int(_end) + 1)]
    else:  # if ',' in args.runs:
        runs = [int(i) for i in args.runs.split(",")]
    runs2process = {args.name: runs}

    lonlat_box = [int(i) for i in args.lonlat.split(",")]

    lsm = get_lsm(lsm_paths[args.name], bbox=lonlat_box, shift=True)
    lon2d, lat2d = np.meshgrid(lsm.longitude, lsm.latitude)

    # Construct categorisation functions
    mask_func = partial(check_by_mask, lsm=lsm, lmask_thresh=0.5, rad=70.0)

    for dset, run_nums in pbar(runs2process.items()):  # , desc="dset"):
        for run_num in pbar(run_nums):  # , leave=False, desc="run_num"):
            logger.info(run_num)
            full_tr = TrackRun()
            for winter in pbar(winters):  # , desc="winter", leave=False):
                logger.info(f"winter: {winter}")
                track_res_dir = mypaths.trackresdir / dset / f"run{run_num:03d}" / winter
                _tr = TrackRun(track_res_dir, columns=columns)
                logger.debug(f"TrackRun size: {len(_tr)}")
                if len(_tr) > 0:
                    logger.info("Begin classification")
                    conditions = [
                        (
                            "pmc",
                            [
                                lambda ot: ot.lifetime_h >= 6,
                                partial(mask_func, trackrun=_tr),
                                lambda ot: ((ot.vortex_type != 0).sum() / ot.shape[0] < 0.2)
                                and (ot.gen_lys_dist_km > 300.0),
                            ],
                        )
                    ]
                    _tr.classify(conditions, True)
                full_tr += _tr

            full_tr.to_archive(mypaths.procdir / f"{dset}_run{run_num:03d}_{period}.h5")


if __name__ == "__main__":
    sys.exit(main())
