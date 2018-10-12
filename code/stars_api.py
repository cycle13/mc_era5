# -*- coding: utf-8 -*-
"""
Python functions to work with STARS-DAT dataset of polar lows
"""
# Standard packages
import pandas as pd
# Local files
import mypaths


def read_tracks_file(fname=mypaths.starsdir/'PolarLow_tracks_North_2002_2011'):
    def _date_parser(*x):
        return pd.datetime.strptime(' '.join(x), '%Y %m %d %H %M')

    dtype_tuple = (int,) + 5*(str,) + 4*(float,)
    dtypes = {k: v for k, v in enumerate(dtype_tuple)}

    df = pd.read_csv(fname, dtype=dtypes, sep='\s+', skiprows=5,
                     date_parser=_date_parser,
                     parse_dates={'time': [1, 2, 3, 4, 5]})
    return df
