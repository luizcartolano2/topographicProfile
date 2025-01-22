""" Docstring for the topographic_profile.py file.

"""
import math
import logging
import os
from typing import Tuple

import googlemaps
import plotly.graph_objects as go
from matplotlib import pyplot as plt

from .image_utils import calculate_dynamic_zoom
from .distance_utils import haversine


class TopographicProfile:
    """
    This module defines the TopographicProfile class, which provides functionality for obtaining and plotting
    topographic profiles between a reference point and a set of antennas. It utilizes Google Maps' Elevation API to
    retrieve elevation data along specified paths.
    """
    def __init__(self, api_name: str, api_key: str):
        """
        Constructor for the TopographicProfile class. Initializes the object with the specified API name and key,
        setting up the necessary API client.

        :param api_name: The name of the API to use (e.g., 'google').
        :param api_key: The API key required to authenticate the client.
        """
        self.api_name = api_name
        self.api_client = self.__build_api_client(api_key)
        self.logger = logging.getLogger(__name__)

    def __build_api_client(self, api_key: str) -> [googlemaps.Client, None]:
        """
        Private method that constructs the appropriate API client based on the specified api_name. Currently,
        it supports the Google Maps API.

        :param api_key: The API key for the client.
        :return: A Google Maps client instance if the API name is 'google'.
        """
        if self.api_name == 'google':
            return googlemaps.client.Client(key=api_key)
        return None

    def get_topographic_profile(self, ref_lat_lon: Tuple[int, int], antennas_lat_lon: list) -> list:
        """
        Public method that retrieves the topographic profiles between a reference latitude/longitude and a list of
        antenna locations. It queries the Google Maps Elevation API for each antenna's path and returns the elevation
        data.

        :param ref_lat_lon: A tuple containing the reference latitude and longitude.
        :param antennas_lat_lon: A list of tuples containing the latitude and longitude of antennas.
        :return: A list of elevation profiles for each antenna, where each profile contains elevation data and
        corresponding locations.
        """
        list_of_profiles = []

        for antenna in antennas_lat_lon:
            path = [ref_lat_lon, antenna]
            response = googlemaps.client.elevation_along_path(self.api_client, path, samples=50)

            list_of_profiles.append(response)

        return list_of_profiles

    # pylint: disable-msg=too-many-locals
    def plot_topographic_profile(self, antennas: list, profiles_to_plot: list, path: str):
        """
        Generates and saves a single figure with multiple subplots, each showing the topographic
        profile for a specific location. Additionally, plots the 'Altura' field for each antenna.

        :param antennas: A list of tuples, where each tuple contains lat/lon and height data for antennas.
        :param profiles_to_plot: A list of elevation profiles, where each profile is a list of
                                 dictionaries containing 'elevation' and 'location' keys.
        :param path: The directory path where the plot will be saved.
        """
        # Calculate the grid size for subplots
        num_profiles = len(profiles_to_plot)
        cols = 2
        rows = math.ceil(num_profiles / cols)

        # Initialize the figure
        fig, axs = plt.subplots(rows, cols, figsize=(12, rows * 4))
        axs = axs.flatten()

        # Iterate over profiles and antennas, plotting each in a separate subplot
        for ite_, (profile, (lat_lon, heights)) in enumerate(zip(profiles_to_plot, antennas)):
            # Extract elevation and calculate real distances
            elevations = [point['elevation'] for point in profile]
            coordinates = [(point['location']['lat'], point['location']['lng']) for point in profile]

            # Calculate cumulative distances
            distances = [0]
            for i in range(1, len(coordinates)):
                lat1, lon1 = coordinates[i - 1]
                lat2, lon2 = coordinates[i]
                distance = haversine(lat1, lon1, lat2, lon2)
                distances.append(distances[-1] + distance)
            distances = [d * 1000 for d in distances]

            # Plot the elevation profile
            ax = axs[ite_]
            ax.plot(distances, elevations, label='Elevation Profile', color='blue')
            ax.fill_between(distances, elevations, color='lightblue', alpha=0.5)

            last_elevation = elevations[-1]
            for _, height_values in heights.items():
                for height in height_values:
                    adjusted_height = height + last_elevation
                    ax.plot(
                        [0, distances[-1]],
                        [adjusted_height, adjusted_height],
                        color='red',
                        linestyle='--',
                        linewidth=1,
                        alpha=0.7
                    )

            # Add title and labels
            ax.set_title(f'Antenna {ite_ + 1} ({lat_lon[0]:.4f}, {lat_lon[1]:.4f})')
            ax.set_xlabel('Distance (meters)')
            ax.set_ylabel('Elevation (meters)')
            ax.grid(True)

        # Hide any unused subplots
        for i in range(num_profiles, len(axs)):
            fig.delaxes(axs[i])

        # Adjust layout and save the figure
        plt.tight_layout()
        output_file_path = os.path.join(path, "topographic_profiles.png")
        plt.savefig(output_file_path, bbox_inches='tight', dpi=300)

        self.logger.info("Topographic profiles with height saved to %s", output_file_path)

    def plot_points_on_map(self, spot: Tuple[int, int], antennas_lat_lon: list, path: str):
        """
        Plots a map with a central "spot" point and multiple antenna locations, saving the map as a PNG file.

        This function uses Plotly to create an interactive map visualization and save it as an image file.
        The central spot is marked in blue, while the antennas are marked in red. The map is dynamically zoomed to fit
        all points.

        :param spot: The central reference point (latitude, longitude), displayed in blue.
        :param antennas_lat_lon: A list of antenna locations.
        :param path: The directory path where the plots will be saved.
        """
        # Combine the main spot and antennas latitudes and longitudes
        latitudes = [spot[0]] + [antenna[0] for antenna in antennas_lat_lon]
        longitudes = [spot[1]] + [antenna[1] for antenna in antennas_lat_lon]

        # Calculate dynamic zoom level and center
        center_lat, center_lon, zoom = calculate_dynamic_zoom(latitudes, longitudes)

        # Create a Mapbox plot
        fig = go.Figure(go.Scattermapbox(
            mode="markers+text",
            lat=latitudes,
            lon=longitudes,
            marker={'size': 10, 'color': ['blue'] + ['red'] * len(antennas_lat_lon)},
            text=['Ponto Principal'] + [f'Antenna {i + 1}' for i in range(len(antennas_lat_lon))],
            textposition="top center"
        ))

        # Set the map style (use Mapbox style or OpenStreetMap)
        fig.update_layout(
            title="Locations on Map",
            # pylint: disable=use-dict-literal
            mapbox=dict(
                style="open-street-map",
                center={"lat": center_lat, "lon": center_lon},
                zoom=zoom
            ),
            showlegend=False
        )

        # Set file path for saving the image
        output_file_path = os.path.join(path, "mapa.png")

        # Save the figure as a PNG
        fig.write_image(output_file_path, format="png", scale=2)

        self.logger.info("Map saved to %s", output_file_path)
