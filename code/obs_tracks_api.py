# -*- coding: utf-8 -*-
"""Functions for loading STARS and ACCACIA datasets of PMCs."""
from octant.core import OctantTrack

import pandas as pd

import mypaths


def read_stars_file(fname=mypaths.starsdir / "PolarLow_tracks_North_2002_2011"):
    """Read data into a `pandas.DataFrame` from the standard file."""

    def _date_parser(*x):
        return pd.datetime.strptime(" ".join(x), "%Y %m %d %H %M")

    dtype_tuple = (int,) + 5 * (str,) + 4 * (float,)
    dtypes = {k: v for k, v in enumerate(dtype_tuple)}

    df = pd.read_csv(
        fname,
        dtype=dtypes,
        sep=r"\s+",
        skiprows=5,
        date_parser=_date_parser,
        parse_dates={"time": [1, 2, 3, 4, 5]},
    )
    return df


def read_all_stars():
    """Read both North and South subsets of STARS."""
    df_n = read_stars_file(fname=mypaths.starsdir / "PolarLow_tracks_North_2002_2011")
    df_s = read_stars_file(fname=mypaths.starsdir / "PolarLow_tracks_South_2002_2011")

    df_s.N += df_n.N.values[-1]

    return df_n.append(df_s).reset_index(drop=True)


def read_all_accacia():
    """Load ACCACIA tracks as `pandas.DataFrame`"""

    def _date_parser(x):
        return pd.datetime.strptime(x, "%Y%m%d%H%M")

    df = pd.read_csv(
        mypaths.acctracks,
        delimiter="\t",
        names=["N", "time", "lon", "lat"],
        parse_dates=["time"],
        date_parser=_date_parser,
    )
    return df


def prepare_tracks(obs_df, bbox=None):
    """Make a list of those tracks that have lifetime >= 6h and stay within bounding box."""

    selected = []
    for i, df in obs_df.groupby("N"):
        ot = OctantTrack.from_df(df)
        if ot.lifetime_h >= 6:
            if bbox is not None:
                if ot.within_rectangle(*bbox, thresh=0.5):
                    selected.append(ot)
            else:
                selected.append(ot)
    return selected
