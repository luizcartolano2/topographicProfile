"""Docstring for the image_utils.py file.

"""


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
    zoom = max(10, 12 - (lat_diff + lon_diff) // 1.5)

    return center_lat, center_lon, zoom
