import numpy as np
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from matplotlib import axes, path
from matplotlib import pyplot as plt

from modelmaker.utils.projections import lonlat2utm


class EarthquakeCatalogue(object):

    def __init__(self, t=None, x=None, y=None, z=None, m=None, is_lonlat=True):

        def _convert2numpy(array):
            if array is None:
                return None
            elif len(array) > 1:
                return np.array(array)
            else:
                return array

        self.t = _convert2numpy(t)
        self.x = _convert2numpy(x)
        self.y = _convert2numpy(y)
        self.z = _convert2numpy(z)
        self.m = _convert2numpy(m)
        self.is_lonlat = is_lonlat


    def load_from_csv(self, csvfile, is_lonlat=True, usecols=(0, 1, 2, 3, 4), **kwargs):
        """
        Load earthquake catalogue from a CSV-formatted input file. File format contains 1 header line,
        followed by 1 line for each earthquake. Optional argument usecols=() must be used to  Earthquake attributes must be ordered in the following
        order: T, X, Y, Z, M

        :param csvfile: Path to a CSV-formatted earthquake catalogue file.
        :pararm is_lonlat: Boolean, If True, indicates that (X, Y) coordinates are expressed in decimal degrees
        (Longitude, Latitude), otherwise considers coordinates in cartesian units (meters, km, ...).
        :param usecols: tuple, indicate the column index (zero-based) of fields T, X, Y, Z, M, in this order.
        :param kwargs: additional keyword-value optional arguments passed to the numpy.loadtxt() method
        """
        self.t, self.x, self.y, self.z, self.m = np.loadtxt(csvfile,
                                                            skiprows=1,
                                                            unpack=True,
                                                            usecols=usecols,
                                                            **kwargs)
        if is_lonlat:
            self.x, self.y = lonlat2utm(self.x, self.y)


    def load_from_xlsx(self):
        """
        to be completed...
        """
        print('Not implemented yet...')
        pass


    def decimate(self, indices, inplace=False):
        """
        Decimate the catalog, and returns a copy of the current EarthquakeCatalogue instance,
        containing only elements matching the input array of indices.

        :param indices: numpy.ndarray, indices of elements kept in the returned catalogue
        :param inplace: boolean, If True, decimation is applied to the current EarthquakeCatalogue instance.

        :return: if inplace==False, returns an EarthquakeCatalogue instance, otherwise None
        """
        if inplace:
            self.t = self.t[indices]
            self.x = self.x[indices]
            self.y = self.y[indices]
            self.z = self.z[indices]
            self.m = self.m[indices]
        else:
            return EarthquakeCatalogue(t=self.t[indices],
                                       x=self.x[indices],
                                       y=self.y[indices],
                                       z=self.z[indices],
                                       m=self.m[indices],
                                       is_lonlat=self.is_lonlat)


    def select_in_polygon(self, h=None):
        """
        Graphical plot-based selection of events enclosed in a polygon drawn by
        successive mouse-clicks
        """
        if h is None:
          h = plt.gcf()
        print('Draw your polygon to select events:\nLeft-click: add polygon vertex\nRight-click: remove last polygon vertex\nMid-click: stop adding vertices')
        points = h.ginput(n=-1, show_clicks=True)
        p = path.Path(points)
        # Retrieve axes:
        for child in h.get_children():
          if isinstance(child, axes._axes.Axes):
            ha = child
            break
        print(points)
        points.append(points[0])
        pts = np.array(points)
        ha.plot(pts[:,0], pts[:,1], 'k--', linewidth=2)
        xKey = ha.get_xlabel()
        yKey = ha.get_ylabel()
        evtPoints = [ (self.table.ix[k,xKey], self.table.ix[k,yKey]) for k in range(self.table.shape[0]) ]
        isInside = p.contains_points(evtPoints)
        csub = self.decimate(isInside)
        return csub


    def in_polygon(self, polygon_coords, is_lonlat=False):
        """
        Return a boolean array indicating whether each earthquake in the catalogue is included (True) or
        not (False) in the polygon specified as input.

        :param polygon_coords: list of tuples, list of (x, y) coordinates for polygon vertices
        :param is_lonlat: boolean, specify whether polygon coordinates are expressed in geographical (if True),
        or in cartesian coordinates (if False).
        :return: is_inside, numpy.ndarray of boolean values. Equals True for earthquakes included in the polygon
        """
        if is_lonlat:
            for k in range(len(polygon_coords)):
                polygon_coords[k] = lonlat2utm(polygon_coords[k][0], polygon_coords[k][1])

        poly = Polygon([Point(xy for xy in polygon_coords)])
        is_inside = np.array([poly.contains((x, y)) for x, y in zip(self.x, self.y)])
        return is_inside

