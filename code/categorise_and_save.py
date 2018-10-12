# -*- coding: utf-8 -*-
"""
Categorise selected runs and save the full dataframe for later use
"""
import numpy as np
from tqdm import tqdm
import xarray as xr

import mypaths
from common_defs import cat_kw, winters

from octant.core import TrackRun

# Select runs
runs2process = dict(era5=[0], interim=[100, 106])

# Load land-sea mask
lsm = xr.open_dataarray(mypaths.era5_dir / 'lsm.nc').squeeze()
lon2d, lat2d = np.meshgrid(lsm.longitude, lsm.latitude)


period = f'{winters[0][:4]}_{winters[-1][-4:]}'

for dset, run_nums in tqdm(runs2process.items(), desc='dset'):
    for run_num in tqdm(run_nums, leave=False, desc='run_num'):
        TR = TrackRun()
        for winter in tqdm(winters, desc='winter', leave=False):
            track_res_dir = (mypaths.trackresdir / dset
                             / f'run{run_num:03d}' / winter)
            TR += TrackRun(track_res_dir)

        TR.categorise(lsm=lsm, **cat_kw)

        TR.data.to_parquet((mypaths.procdir /
                           f'{dset}_run{run_num:03d}_{period}_top10.parquet'),
                           engine='pyarrow')
