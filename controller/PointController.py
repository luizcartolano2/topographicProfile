import json
import os
from typing import Tuple

from analyzer.TopographicProfile import TopographicProfile
from analyzer.FileAnalyzer import FileAnalyzer


class PointController:
    def __init__(self, output_dir: str, file_analyzer: FileAnalyzer, topographic_profile: TopographicProfile):
        """
        Constructor for the PointController class. It initializes the object with directories and dependencies for
        analyzing antenna data and generating topographic profiles.

        :param output_dir: The directory where output files will be saved.
        :param file_analyzer: An instance of the FileAnalyzer class used to analyze antennas.
        :param topographic_profile: An instance of the TopographicProfile class used to retrieve and plot topographic profiles.
        """
        self.output_dir = output_dir
        self.file_analyzer = file_analyzer
        self.topographic_profile = topographic_profile

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
        with open(output_file_path, 'w') as file:
            file.write(json.dumps(data, indent=4))

    def analyze_lat_lon(self, lat_lon: Tuple[int, int]):
        """
        Public method that analyzes the antennas and topographic profile for a given latitude/longitude point. It retrieves
        the available antennas, saves the result to a JSON file, and generates the topographic profile plot for the antennas.

        :param lat_lon: The latitude and longitude of the reference point to analyze.
        """
        subfolder_name = f"subfolder_{lat_lon[0]}_{lat_lon[1]}"
        subfolder_path = os.path.join(self.output_dir, subfolder_name)

        available_antennas = self.file_analyzer.get_antennas_to_create_profile(4, ref_lat_lon=lat_lon)

        self.__create_output_file(subfolder_path, available_antennas)
        antennas_lat_lon = []
        for _, value in available_antennas.items():
            antennas_lat_lon.append(value['lat/lon'])

        profiles_to_plot = self.topographic_profile.get_topographic_profile(lat_lon, antennas_lat_lon)
        self.topographic_profile.plot_topographic_profile(profiles_to_plot, antennas_lat_lon, subfolder_path)
