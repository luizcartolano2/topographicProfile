""" Docstring for the topographic_profile.py file.

"""
import logging
import os
from typing import Tuple

import googlemaps
import plotly.graph_objects as go
from matplotlib import pyplot as plt

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

    @staticmethod
    def plot_topographic_profile(profiles_to_plot: list, antennas_lat_lon: list, path: str):
        """
        Static method that generates and saves a plot of the topographic profile for each antenna.
        It calculates cumulative distances along the path and plots elevation against distance.

        :param profiles_to_plot: A list of elevation profiles to plot.
        :param antennas_lat_lon: A list of antenna locations.
        :param path: The directory path where the plots will be saved.
        """
        # Define the path and the number of samples
        for ite_, profile in enumerate(profiles_to_plot):
            output_file_path = os.path.join(path, f"{antennas_lat_lon[ite_]}.png")

            # Extract elevation and calculate real distances
            elevations = [point['elevation'] for point in profile]
            coordinates = [(point['location']['lat'], point['location']['lng']) for point in profile]

            # Calculate cumulative distances
            distances = [0]  # Start with zero for the first point
            for i in range(1, len(coordinates)):
                lat1, lon1 = coordinates[i - 1]
                lat2, lon2 = coordinates[i]
                distance = haversine(lat1, lon1, lat2, lon2)
                distances.append(distances[-1] + distance)  # Add cumulative distance

            # Convert distances to meters (optional)
            distances = [d * 1000 for d in distances]

            # Plot the elevation profile
            plt.figure(figsize=(10, 6))
            plt.plot(distances, elevations, label='Elevation Profile', color='blue')
            plt.fill_between(distances, elevations, color='lightblue', alpha=0.5)
            plt.title('Topographic Profile')
            plt.xlabel('Distance (meters)')
            plt.ylabel('Elevation (meters)')
            plt.legend()
            plt.grid(True)
            plt.savefig(output_file_path)

    @staticmethod
    def calculate_dynamic_zoom(latitudes, longitudes):
        """
        Calculate the optimal zoom level based on the bounding box of the points.
        The zoom level will depend on the range of latitudes and longitudes.

        :param latitudes: List of latitudes.
        :param longitudes: List of longitudes.
        :return: A zoom level (integer).
        """
        # Calculate the bounding box
        lat_min, lat_max = min(latitudes), max(latitudes)
        lon_min, lon_max = min(longitudes), max(longitudes)

        # Calculate the center of the bounding box
        center_lat = (lat_min + lat_max) / 2
        center_lon = (lon_min + lon_max) / 2

        # Calculate the spread (distance) of the points in both latitude and longitude
        lat_diff = lat_max - lat_min
        lon_diff = lon_max - lon_min

        # Determine the zoom level based on the spread of the points
        zoom = max(10, 12 - (lat_diff + lon_diff) // 1.5)  # You can fine-tune the divisor for zoom sensitivity

        return center_lat, center_lon, zoom

    def plot_points_on_map(self, spot: Tuple[int, int], antennas_lat_lon: list, path: str):
        """
        .

        :param spot: The central reference point (latitude, longitude), displayed in blue.
        :param antennas_lat_lon: A list of antenna locations.
        :param path: The directory path where the plots will be saved.
        """
        # Combine the main spot and antennas latitudes and longitudes
        latitudes = [spot[0]] + [antenna[0] for antenna in antennas_lat_lon]
        longitudes = [spot[1]] + [antenna[1] for antenna in antennas_lat_lon]

        # Calculate dynamic zoom level and center
        center_lat, center_lon, zoom = self.calculate_dynamic_zoom(latitudes, longitudes)

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
