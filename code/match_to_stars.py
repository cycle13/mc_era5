# coding: utf-8
"""Match cyclone tracks from ERA5 and ERA-Interim to STARS list of polar lows."""
import json
from loguru import logger as L

import octant
from octant.core import TrackRun
from octant.decor import get_pbar

from common_defs import CAT, bbox, datasets, period, winters
import mypaths
from obs_tracks_api import read_all_stars, prepare_tracks


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
winter_dates_dict = {
    k: (f"{k.split('_')[0]}-10-01", f"{k.split('_')[1]}-04-30") for k in winters[1:11]
}
run_group_start = 100
runs_grid_paths = {
    "era5": mypaths.procdir / "runs_grid_tfreq_era5.json",
    "interim": mypaths.procdir / "runs_grid_tfreq_interim.json",
}


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
    L.remove(0)
    L.add("log_match_to_stars_{time}.log")
    octant.RUNTIME.enable_progress_bar = True
    pbar = get_pbar(use="tqdm")
    octant.RUNTIME.enable_progress_bar = False

    obs_tracks = prepare_tracks(
        read_all_stars(), filter_func=[lambda ot: ot.within_rectangle(*bbox)]
    )
    n_ref = len(obs_tracks)
    L.debug(f"Number of suitable tracks: {n_ref}")

    # Define an output directory and create it if it doesn't exist
    output_dir = mypaths.procdir / "matches"
    output_dir.mkdir(exist_ok=True)

    # Loop over datasets, runs, subsets, matching methods
    for dset in pbar(datasets):  # , desc="dataset"):
        with runs_grid_paths[dset].open("r") as fp:
            runs_grid = json.load(fp)
        for run_id, _ in pbar(enumerate(runs_grid, run_group_start)):
            TR = TrackRun.from_archive(mypaths.procdir / f"{dset}_run{run_id:03d}_{period}.h5")
            L.debug(mypaths.procdir / f"{dset}_run{run_id:03d}_{period}.h5")
            L.debug(TR)
            for match_kwargs in pbar(match_options):  # , desc="match options"):
                match_pairs_abs = []
                for winter, w_dates in pbar(winter_dates_dict.items()):  # , desc="winter"):
                    tr = TR.time_slice(*w_dates)
                    L.debug(tr)
                    L.debug(run_id)
                    L.debug(match_kwargs)
                    L.debug(winter)
                    match_pairs = tr.match_tracks(obs_tracks, subset=CAT, **match_kwargs)
                    for match_pair in match_pairs:
                        match_pairs_abs.append(
                            (match_pair[0], obs_tracks[match_pair[1]].N.unique()[0])
                        )
                match_kwargs_label = _make_match_label(match_kwargs)

                # Save matching pairs to a text file
                fname = f"{dset}_run{run_id:03d}_{period}_{match_kwargs_label}.txt"
                with (output_dir / fname).open("w") as fout:
                    fout.write(
                        f"""# {dset}
# {run_id:03d}
# {period}
# {match_kwargs_label}
"""
                    )
                    for match_pair in match_pairs_abs:
                        fout.write("{:d},{:d}\n".format(*match_pair))


if __name__ == "__main__":
    main()
