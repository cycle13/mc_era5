# coding: utf-8
"""Match cyclone tracks from ERA5 and ERA-Interim to STARS list of polar lows."""
from octant.core import TrackRun, OctantTrack

from tqdm import tqdm_notebook as tqdm

from common_defs import winters, period
import mypaths
from stars_api import read_tracks_file

match_options = [
    dict(method='bs2000', beta=25.),
    dict(method='bs2000', beta=50.),
    dict(method='bs2000', beta=75.),
    dict(method='bs2000', beta=100.),
    dict(method='simple', thresh_dist=150.),
    dict(method='simple', thresh_dist=200.),
    dict(method='simple', thresh_dist=250.),
    dict(method='simple', thresh_dist=300.),
]
winter_dates_stars = {k: (f"{k.split('_')[0]}-10-01",
                          f"{k.split('_')[1]}-04-30")
                      for k in winters[1:11]}


def _make_match_label(match_kwargs):
    match_kwargs_label = []
    for k, v in match_kwargs.items():
        try:
            vv = int(v)
        except ValueError:
            vv = v
        match_kwargs_label.append(f'{k}={vv}')
    return '_'.join(match_kwargs_label)


def main():
    stars = read_tracks_file()
    print(stars.N.nunique())

    # Create a list of only those STARS tracks that have lifetime 6 h or greater
    stars_tracks = []
    for i, df in stars.groupby('N'):
        ot = OctantTrack.from_df(df)
        if ot.lifetime_h >= 6:
            stars_tracks.append(ot)
    n_ref = len(stars_tracks)
    print(n_ref)

    # Define an output directory and create it if it doesn't exist
    output_dir = mypaths.procdir / 'matches'
    output_dir.mkdir(exist_ok=True)

    # runs2process = dict(era5=[0])#, interim=[100, 106])
    dset = 'era5'

    # Loop over runs, subsets, matching methods
    for run_num in tqdm(range(13), desc='run_num'):
        TR = TrackRun.from_archive(mypaths.procdir / f'{dset}_run{run_num:03d}_{period}.h5')
        TR.is_categorised = True
        for subset in tqdm(['moderate', 'strong'], desc='subset'):
            for match_kwargs in tqdm(match_options, desc='match options'):
                match_pairs_abs = []
                for winter, w_dates in tqdm(winter_dates_stars.items(), desc='winter'):
                    tr = TR.time_slice(*w_dates)
                    match_pairs = tr.match_tracks(stars_tracks, subset=subset, **match_kwargs)
                    for match_pair in match_pairs:
                        match_pairs_abs.append((match_pair[0], stars_tracks[match_pair[1]].N.unique()[0]))
                match_kwargs_label = _make_match_label(match_kwargs)

                # Save matching pairs to a text file
                fname = f'{dset}_run{run_num:03d}_{period}_subset={subset}_{match_kwargs_label}.txt'
                with (output_dir / fname).open('w') as fout:
                    fout.write(f"""# {dset}
# {run_num:03d}
# {period}
# {subset}
# {match_kwargs_label}
""")
                    for match_pair in match_pairs_abs:
                        fout.write('{:d},{:d}\n'.format(*match_pair))


if __name__ == '__main__':
    main()
