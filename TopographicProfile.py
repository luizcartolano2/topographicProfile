import googlemaps
import numpy as np
from matplotlib import pyplot as plt


class TopographicProfile:
    def __init__(self, api_name, api_key):
        self.api_name = api_name
        self.api_client = self.__build_api_client(api_key)

    def __build_api_client(self, api_key):
        if self.api_name == 'google':
            return googlemaps.client.Client(key=api_key)

    @staticmethod
    def _apply_filters(df, filters):
        filtered_df = df.copy()
        for column, condition in filters.items():
            if callable(condition):
                # Apply custom function
                filtered_df = filtered_df[filtered_df[column].apply(condition)]
            elif isinstance(condition, tuple) and len(condition) == 2:
                # Apply range filter (min, max)
                filtered_df = filtered_df[(filtered_df[column] >= condition[0]) & (filtered_df[column] <= condition[1])]
            else:
                # Apply equality filter
                filtered_df = filtered_df[filtered_df[column] == condition]

        return filtered_df

    @staticmethod
    def _haversine(lat1, lon1, lat2, lon2):
        """
        Calculate the great-circle distance between two points on the Earth using the Haversine formula.

        Parameters:
            lat1, lon1 (float): Latitude and longitude of the first point in decimal degrees.
            lat2, lon2 (float): Latitude and longitude of the second point in decimal degrees.

        Returns:
            float: Distance between the two points in kilometers.
        """
        # Earth's radius in kilometers
        EARTH_RADIUS_KM = 6371.0

        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

        # Differences in coordinates
        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1

        # Haversine formula
        a = np.sin(delta_lat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(delta_lon / 2) ** 2
        c = 2 * np.arcsin(np.sqrt(a))

        # Distance in kilometers
        distance_km = EARTH_RADIUS_KM * c
        return distance_km

    def get_antennas_to_create_profile(self, ref_lat, ref_lon, available_antennas, radius=50, filters=None):
        if filters is not None:
            available_antennas = self._apply_filters(available_antennas, filters)

        available_antennas["distance_km"] = available_antennas.apply(
            lambda row: self._haversine(ref_lat, ref_lon, row["Latitude"], row["Longitude"]), axis=1
        )

        available_antennas = available_antennas[available_antennas["distance_km"] <= radius]

        return available_antennas

    def get_topographic_profile(self, ref_lat_lon, antennas_lat_lon):
        list_of_profiles = []

        for antenna in antennas_lat_lon:
            path = [ref_lat_lon, antenna]
            response = googlemaps.client.elevation_along_path(self.api_client, path, samples=50)

            list_of_profiles.append(response)

        return list_of_profiles

    def plot_topographic_profile(self, profiles_to_plot):
        # Define the path and the number of samples
        for profile in profiles_to_plot:
            # Extract elevation and calculate real distances
            elevations = [point['elevation'] for point in profile]
            coordinates = [(point['location']['lat'], point['location']['lng']) for point in profile]

            # Calculate cumulative distances
            distances = [0]  # Start with zero for the first point
            for i in range(1, len(coordinates)):
                lat1, lon1 = coordinates[i - 1]
                lat2, lon2 = coordinates[i]
                distance = self._haversine(lat1, lon1, lat2, lon2)
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
            plt.show()
