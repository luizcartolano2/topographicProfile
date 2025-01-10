"""Docstring for the distance_utils.py file.

"""
import numpy as np


# Earth's radius in kilometers
EARTH_RADIUS_KM = 6371.0


def haversine(lat1: float, lon1: float, lat2: float, lon2: float):
    """
    Calculate the great-circle distance between two points on the Earth using the Haversine formula.

    :param lat1: Latitude of the first point in decimal degrees.
    :param lon1: Longitude of the first point in decimal degrees.
    :param lat2: Latitude of the first second in decimal degrees.
    :param lon2: Longitude of the first second in decimal degrees.
    :return: Distance between the two points in kilometers.
    """
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
