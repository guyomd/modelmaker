
import numpy as np
import utm


def lonlat2utm(lon, lat):
    """
    Convert coordinates expressed in Latitude and Longitude (decimal degrees, WGS84) to
    UTM coordinates (expressed in meters)

    :param lon: numpy.ndarray, array of longitudes, expressed in decimal degrees
    :param lat: numpy.ndarray, array of latitudes, expressed in decimal degrees
    :return: x, y: numpy.ndarray, arrays of Easting and Northing UTM coordinates, in m.
    """
    x = list()
    y = list()
    zone = list()
    for long, lati in zip(lat, lon):
        east, north, num, letter = utm.from_latlon(long, lati)
        x.append(east)
        y.append(north)
        zone.append(str(num)+letter)
    return np.array(x), np.array(y)