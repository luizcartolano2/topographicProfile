""" Docstring for the point_controller.py file.

"""
import json
import logging
import os
from typing import Tuple

from analyzer.topographic_profile import TopographicProfile
from analyzer.file_analyzer import FileAnalyzer


# pylint: disable=too-few-public-methods
class PointController:
    """
    This module defines the PointController class, which coordinates the analysis and plotting of antenna data and
    topographic profiles. It relies on FileAnalyzer for antenna selection and TopographicProfile for retrieving and
    plotting topographic profiles.
    """
    def __init__(self, output_dir: str, file_analyzer: FileAnalyzer, topographic_profile: TopographicProfile):
        """
        Constructor for the PointController class. It initializes the object with directories and dependencies for
        analyzing antenna data and generating topographic profiles.

        :param output_dir: The directory where output files will be saved.
        :param file_analyzer: An instance of the FileAnalyzer class used to analyze antennas.
        :param topographic_profile: An instance of the TopographicProfile class used to retrieve and plot
        topographic profiles.
        """
        self.output_dir = output_dir
        self.file_analyzer = file_analyzer
        self.topographic_profile = topographic_profile
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def __create_output_file(subfolder_path: str, data: dict):
        """
        Private static method that creates a directory (if it doesn't exist) and writes the given data to a JSON file.

        :param subfolder_path: The path of the subfolder where the output file will be saved.
        :param data: The data to be saved in JSON format.
        """
        # Create the directory
        os.makedirs(subfolder_path, exist_ok=True)
        # Full path for the output file
        output_file_path = os.path.join(subfolder_path, "output.json")
        # Save dictionary to a text file in JSON format
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(json.dumps(data, indent=4))

    @staticmethod
    def extract_antennas_from_data_dict(data_dict: dict):
        """
        Extracts antenna data, including lat/lon and height, from the given data dictionary.

        :param data_dict: A dictionary containing location data with 'height' and 'lat/lon' keys.
        :return: A list of tuples, each containing lat/lon and height data for antennas.
        """
        antennas = []
        for _, value in data_dict.items():
            lat_lon = value['lat/lon']
            heights = {
                provider: list(map(float, data['Altura']))
                for provider, data in value.items()
                if isinstance(data, dict) and 'Altura' in data
            }
            antennas.append((lat_lon, heights))

        return antennas

    def analyze_lat_lon(self, lat_lon: Tuple[int, int]):
        """
        Public method that analyzes the antennas and topographic profile for a given latitude/longitude point.
        It retrieves the available antennas, saves the result to a JSON file, and generates the topographic profile
        plot for the antennas.

        :param lat_lon: The latitude and longitude of the reference point to analyze.
        """
        subfolder_name = f"subfolder_{lat_lon[0]}_{lat_lon[1]}"
        subfolder_path = os.path.join(self.output_dir, subfolder_name)

        available_antennas = self.file_analyzer.get_antennas_to_create_profile(4, ref_lat_lon=lat_lon)

        self.__create_output_file(subfolder_path, available_antennas)
        antennas_lat_lon_height = self.extract_antennas_from_data_dict(available_antennas)
        antennas_lat_lon = [ant[0] for ant in antennas_lat_lon_height]

        self.topographic_profile.plot_points_on_map(lat_lon, antennas_lat_lon, subfolder_path)
        profiles_to_plot = self.topographic_profile.get_topographic_profile(lat_lon, antennas_lat_lon)
        self.topographic_profile.plot_topographic_profile(antennas_lat_lon_height, profiles_to_plot, subfolder_path)
