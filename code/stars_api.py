# -*- coding: utf-8 -*-
"""Python functions to work with STARS dataset of polar lows."""
import pandas as pd

import mypaths


def read_tracks_file(fname=mypaths.starsdir / "PolarLow_tracks_North_2002_2011"):
    """Read data into a `pandas.DataFrame` from the standard file."""

    def _date_parser(*x):
        return pd.datetime.strptime(" ".join(x), "%Y %m %d %H %M")

    dtype_tuple = (int,) + 5 * (str,) + 4 * (float,)
    dtypes = {k: v for k, v in enumerate(dtype_tuple)}

    df = pd.read_csv(
        fname,
        dtype=dtypes,
        sep="\s+",
        skiprows=5,
        date_parser=_date_parser,
        parse_dates={"time": [1, 2, 3, 4, 5]},
    )
    return df


def read_all():
    """Read both North and South subsets of STARS."""
    df_n = read_tracks_file(fname=mypaths.starsdir / "PolarLow_tracks_North_2002_2011")
    df_s = read_tracks_file(fname=mypaths.starsdir / "PolarLow_tracks_South_2002_2011")

    df_s.N += df_n.N.values[-1]

    return df_n.append(df_s).reset_index(drop=True)
