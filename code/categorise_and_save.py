# -*- coding: utf-8 -*-
"""
Categorise selected runs and save the full dataframe for later use
"""
import numpy as np
from tqdm import tqdm
import xarray as xr

import mypaths
from common_defs import cat_kw, winters, columns

from octant.core import TrackRun

# Select runs
runs2process = dict(era5=[0]) # , interim=[100, 106])

# Load land-sea mask
lsm = xr.open_dataarray(mypaths.era5_dir / 'lsm.nc').squeeze()
# Shift longitude coordinate from (0, 359) to (-180, 179)
lsm = (lsm.assign_coords(longitude=(((lsm.longitude + 180) % 360) - 180))
       .sortby('longitude'))
# Select a subset of longitudes and latitudes to speed up categorisation
lsm = lsm.sel(longitude=(lsm.longitude > -25) & (lsm.longitude < 55),
              latitude=(lsm.latitude > 64) & (lsm.latitude < 86))
lsm = lsm.where(lsm==0, 1)  # set all non-zero values to 1
lon2d, lat2d = np.meshgrid(lsm.longitude, lsm.latitude)

period = f'{winters[0][:4]}_{winters[-1][-4:]}'

for dset, run_nums in tqdm(runs2process.items(), desc='dset'):
    for run_num in tqdm(run_nums, leave=False, desc='run_num'):
        TR = TrackRun()
        for winter in tqdm(winters, desc='winter', leave=False):
            track_res_dir = (mypaths.trackresdir / dset
                             / f'run{run_num:03d}' / winter)
            _tr = TrackRun(track_res_dir, columns=columns)
            _tr.categorise(lsm=lsm, **cat_kw)
            TR += _tr

        TR.to_archive(mypaths.procdir /
                      f'{dset}_run{run_num:03d}_{period}.h5')
