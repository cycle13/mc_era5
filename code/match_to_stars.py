# coding: utf-8
"""Match cyclone tracks from ERA5 and ERA-Interim to STARS list of polar lows."""
from loguru import logger as L

import octant
from octant.core import TrackRun, OctantTrack
from octant.decor import get_pbar

from common_defs import CAT, datasets, nruns, period, winters
import mypaths
from stars_api import read_all


match_options = [
    dict(method="bs2000", beta=25.0),
    dict(method="bs2000", beta=50.0),
    dict(method="bs2000", beta=75.0),
    dict(method="bs2000", beta=100.0),
    dict(method="simple", thresh_dist=150.0),
    dict(method="simple", thresh_dist=200.0),
    dict(method="simple", thresh_dist=250.0),
    dict(method="simple", thresh_dist=300.0),
]
winter_dates_stars = {
    k: (f"{k.split('_')[0]}-10-01", f"{k.split('_')[1]}-04-30") for k in winters[1:11]
}


def prepare_stars(bbox=None):
    """Make a list of those STARS tracks that have lifetime 6 h or greater."""
    stars = read_all()

    stars_tracks = []
    for i, df in stars.groupby("N"):
        ot = OctantTrack.from_df(df)
        if ot.lifetime_h >= 6:
            if bbox is not None:
                if ot.within_rectangle(*bbox, thresh=0.5):
                    stars_tracks.append(ot)
            else:
                stars_tracks.append(ot)
    return stars_tracks


def _make_match_label(match_kwargs, delim="_"):
    match_kwargs_label = []
    for k, v in match_kwargs.items():
        try:
            vv = int(v)
        except ValueError:
            vv = v
        match_kwargs_label.append(f"{k}={vv}")
    return delim.join(match_kwargs_label)


@L.catch
def main():
    L.add("log_match_to_stars_{time}.log")
    octant.RUNTIME.enable_progress_bar = False
    pbar = get_pbar(use="tqdm")

    stars_tracks = prepare_stars()
    n_ref = len(stars_tracks)
    L.info(f"Number of suitable STARS tracks: {n_ref}")

    # Define an output directory and create it if it doesn't exist
    output_dir = mypaths.procdir / "matches"
    output_dir.mkdir(exist_ok=True)

    # Loop over datasets, runs, subsets, matching methods
    for dset in pbar(datasets, desc="dataset"):
        for run_num in pbar(range(nruns), desc="run_num"):
            TR = TrackRun.from_archive(mypaths.procdir / f"{dset}_run{run_num:03d}_{period}.h5")
            L.info(mypaths.procdir / f"{dset}_run{run_num:03d}_{period}.h5")
            L.info(TR)
            for match_kwargs in pbar(match_options, desc="match options"):
                match_pairs_abs = []
                for winter, w_dates in pbar(winter_dates_stars.items(), desc="winter"):
                    tr = TR.time_slice(*w_dates)
                    L.debug(tr)
                    L.debug(run_num)
                    L.debug(match_kwargs)
                    L.debug(winter)
                    match_pairs = tr.match_tracks(stars_tracks, subset=CAT, **match_kwargs)
                    for match_pair in match_pairs:
                        match_pairs_abs.append(
                            (match_pair[0], stars_tracks[match_pair[1]].N.unique()[0])
                        )
                match_kwargs_label = _make_match_label(match_kwargs)

                # Save matching pairs to a text file
                fname = f"{dset}_run{run_num:03d}_{period}_{match_kwargs_label}.txt"
                with (output_dir / fname).open("w") as fout:
                    fout.write(
                        f"""# {dset}
# {run_num:03d}
# {period}
# {match_kwargs_label}
"""
                    )
                    for match_pair in match_pairs_abs:
                        fout.write("{:d},{:d}\n".format(*match_pair))


if __name__ == "__main__":
    main()
