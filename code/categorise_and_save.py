#!/usr/bin/env python3
"""Categorise selected runs and serialise TrackRun object for later use."""
import argparse
import sys
from pathlib import Path
from textwrap import dedent

import numpy as np
import xarray as xr

import mypaths
from common_defs import cat_kw, winters, columns, bbox, period

from octant.decor import pbar
from octant.core import TrackRun

# Select runs
# runs2process = dict(era5=[0])  # , interim=[100, 106])


def parse_args(args=None):
    """Parse command line arguments"""
    SCRIPT = Path(__file__).stem
    epilog = dedent(f"""Example of use:
    ./{SCRIPT} -n era5 -r 0,3,10,11 -ll 10,20,65,85
    """)
    ap = argparse.ArgumentParser(SCRIPT,
                                 description=__doc__,
                                 formatter_class=argparse.
                                 ArgumentDefaultsHelpFormatter,
                                 epilog=epilog)

    ap.add_argument('-n', '--name', type=str,
                    required=True, choices=['era5', 'interim'],
                    help='Name of the dataset')
    ap.add_argument('-r', '--runs', type=str,
                    required=True,
                    help='Run numbers, comma- or dash-separated (inclusive range)')

    ag_sub = ap.add_argument_group(title='Subset')
    ag_sub.add_argument('-ll', '--lonlat', type=str,
                        default=','.join([str(i) for i in bbox]),
                        help=('Lon-lat bounding box (lon0,lon1,lat0,lat1)'))

    return ap.parse_args(args)


def get_lsm(path_to_file, bbox=None, shift=False):
    """Load land-sea mask from a file and crop a region defined by `bbox`"""
    # Load land-sea mask
    lsm = xr.open_dataarray(mypaths.era5_dir / 'lsm.nc').squeeze()
    if shift:
        # Shift longitude coordinate from (0, 359) to (-180, 179)
        lsm = (lsm.assign_coords(longitude=(((lsm.longitude + 180) % 360) - 180))
               .sortby('longitude'))
    if bbox is not None:
        # Select a subset of longitudes and latitudes to speed up categorisation
        lsm = lsm.sel(longitude=(lsm.longitude > bbox[0]) & (lsm.longitude < bbox[1]),
                      latitude=(lsm.latitude > bbox[2]) & (lsm.latitude < bbox[3]))
    # Set all non-zero values to 1 to make it the mask binary (0 or 1)
    lsm = lsm.where(lsm == 0, 1)
    return lsm


def main(args=None):
    """Loop over track runs and categorise them according `cat_kw`"""
    args = parse_args(args)

    if '-' in args.runs:
        _start, _end = args.runs.split('-')
        runs = [*range(int(_start), int(_end)+1)]
    else:  # if ',' in args.runs:
        runs = [int(i) for i in args.runs.split(',')]
    runs2process = {args.name: runs}

    lonlat_box = [int(i) for i in args.lonlat.split(',')]

    lsm = get_lsm(mypaths.era5_dir / 'lsm.nc', bbox=lonlat_box, shift=True)
    lon2d, lat2d = np.meshgrid(lsm.longitude, lsm.latitude)

    for dset, run_nums in pbar(runs2process.items(), desc='dset'):
        for run_num in pbar(run_nums, leave=False, desc='run_num'):
            print(run_num)
            TR = TrackRun()
            for winter in pbar(winters, desc='winter', leave=False):
                print(winter)
                track_res_dir = (mypaths.trackresdir / dset
                                 / f'run{run_num:03d}' / winter)
                _tr = TrackRun(track_res_dir, columns=columns)
                print('Begin categorise()')
                _tr.categorise(lsm=lsm, **cat_kw)
                TR += _tr

            TR.to_archive(mypaths.procdir /
                          f'{dset}_run{run_num:03d}_{period}.h5')


if __name__ == '__main__':
    sys.exit(main())
