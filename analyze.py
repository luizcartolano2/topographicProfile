import os

import pandas as pd

from TopographicProfile import TopographicProfile

if __name__ == '__main__':
    download_path = f'{os.getcwd()}/files'
    df = pd.read_csv(f'{download_path}/antennas-SP.csv', on_bad_lines='skip', delimiter=',')

    top_profile = TopographicProfile('google', 'AIzaSyB00vnm5fWSn7C6JLRgIkzL_EWe8oaCeRI')

    ref_lat_lon = (-22.799555, -45.195437)

    antennas_to_profile = top_profile.get_antennas_to_create_profile(
        ref_lat_lon[0], ref_lat_lon[1], df, 0.5
    )

    antennas_lat_lon = [tuple(map(float, t)) for t in antennas_to_profile[['Latitude', 'Longitude']].values]
    profiles_to_plot = top_profile.get_topographic_profile(ref_lat_lon, antennas_lat_lon)

    top_profile.plot_topographic_profile(profiles_to_plot)
