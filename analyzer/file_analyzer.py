""" Docstring for the file_analyzer.py file.

"""
import logging
from typing import Tuple
import pandas as pd
from .distance_utils import haversine


# pylint: disable=too-few-public-methods
class FileAnalyzer:
    """
    This module defines the FileAnalyzer class, which provides functionality for reading a CSV file containing antenna
    information, processing the data, and calculating distances between antenna locations.
    """

    def __init__(self, filename: str):
        """
        Constructor for the FileAnalyzer class. Initializes the object with a CSV filename and predefined column names.

        :param filename: The path to the CSV file containing the antenna data.
        """
        self.logger = logging.getLogger(__name__)
        self.filename = filename
        self.columns = ['NomeEntidade', 'Tecnologia', 'FreqTxMHz', 'Azimute', 'Latitude', 'Longitude', 'AlturaAntena']
        self.numeric_columns = ["Latitude", "Longitude"]
        self.logger.info("Initializing FileAnalyzer with file: %s", filename)
        self.antennas_df = self.__read_csv()

    def __read_csv(self) -> pd.DataFrame:
        """
        Private method that reads the CSV file specified by the filename attribute.

        :return: A cleaned DataFrame containing the relevant antenna data.
        """
        self.logger.info("Reading data from file: %s", self.filename)

        try:
            antennas = pd.read_csv(self.filename, on_bad_lines='skip', delimiter=',', usecols=self.columns, dtype=str)
            self.logger.info("CSV file read successfully, processing columns...")
        except Exception as e:
            self.logger.error("Error reading CSV file: %s", e)
            raise

        try:
            antennas[self.numeric_columns] = antennas[self.numeric_columns].apply(
                lambda col: pd.to_numeric(col.str.replace(",", "."), errors='coerce').round(5)
            )
            antennas = antennas.dropna(subset=self.numeric_columns)
            antennas = antennas.dropna(subset=["Tecnologia"])
            self.logger.info("Data cleaning complete, %d rows remaining", len(antennas))
        except Exception as e:
            self.logger.error("Error during data cleaning: %s", e)
            raise

        return antennas

    def __create_df_with_distance_column(self, ref_lat_lon: Tuple[float, float]) -> pd.DataFrame.groupby:
        """
        Private method that calculates the distance between each antenna's latitude and longitude and a reference
        latitude and longitude using the Haversine formula.

        :param ref_lat_lon: A tuple containing the reference latitude and longitude.
        :return: A grouped DataFrame based on distance and antenna name.
        """
        self.logger.info("Calculating distances from reference point: %s", ref_lat_lon)
        try:
            antennas_df_copy = self.antennas_df.copy()
            antennas_df_copy["distance_km"] = self.antennas_df.apply(
                lambda row: round(
                    haversine(ref_lat_lon[0], ref_lat_lon[1], row["Latitude"], row["Longitude"]), 2
                ), axis=1
            )
            antennas_df_copy = antennas_df_copy.sort_values(by="distance_km", ascending=True)
            self.logger.info("Distance calculation complete, %d antennas processed", len(antennas_df_copy))
        except Exception as e:
            self.logger.error("Error calculating distances: %s", e)
            raise

        return antennas_df_copy.groupby(["distance_km", "NomeEntidade"])

    def get_antennas_to_create_profile(self, num_antennas: int, ref_lat_lon: Tuple[float, float]) -> dict:
        """
        Public method that calls __create_df_with_distance_column to generate a DataFrame with distance information
        and selects antennas to create a profile.

        :param num_antennas: The number of antennas to gather.
        :param ref_lat_lon: A tuple containing the reference latitude and longitude.
        :return: A dictionary where the keys are distances and the values are dictionaries containing information about
         the antennas (e.g., frequency, technology, azimuth, and location).
        """
        self.logger.info("Getting antennas to create profile, num_antennas: %d", num_antennas)
        grouped_data = self.__create_df_with_distance_column(ref_lat_lon=ref_lat_lon)

        distances = set()
        available_companies = set()
        available_antennas = {}

        try:
            for _, group in grouped_data:
                if len(distances) < num_antennas or len(available_companies) < 2:
                    # Extract information from the group
                    distance = group['distance_km'].unique().tolist()
                    company_name = group['NomeEntidade'].unique().tolist()
                    lat = group['Latitude'].unique().tolist()[0]
                    lon = group['Longitude'].unique().tolist()[0]
                    company_info = {
                        'Freq': group['FreqTxMHz'].unique().tolist(),
                        'Tecnologia': group['Tecnologia'].unique().tolist(),
                        'Azimute': group['Azimute'].unique().tolist(),
                        'Altura': group['AlturaAntena'].unique().tolist()
                    }

                    # Update distances and companies
                    if distance:
                        distances.update(distance)

                        # Ensure distance[0] exists in available_antennas
                        if distance[0] not in available_antennas:
                            available_antennas[distance[0]] = {}

                        # Update lat/lon and company info
                        available_antennas[distance[0]]['lat/lon'] = (lat, lon)
                        for name in company_name:
                            available_antennas[distance[0]][name] = company_info

                    available_companies.update(company_name)
                else:
                    self.logger.info("Reached the maximum number of antennas or companies, stopping.")
                    break
        except Exception as e:
            self.logger.error("Error while selecting antennas: %s", e)
            raise

        self.logger.info("Antennas profile created with %d entries", len(available_antennas))
        return available_antennas
