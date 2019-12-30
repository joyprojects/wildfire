"""Wrapper for a GOES-16/17 satellite image."""
import logging
import os
import urllib

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from . import downloader, utilities

LOCAL_DIRECTORY = "downloaded_data"

_logger = logging.getLogger(__name__)


def read_netcdf(filepath):
    """maybe returns one channel?"""
    if filepath.startswith("s3://"):
        return
        # read from s3
    # else, read from local


def _normalize(data):
    """Normalize `data` to be centered around 0."""
    sample_mean = data.mean()
    sample_sd = data.std()
    return (data - sample_mean) / sample_sd


class GoesScan:
    def __init__(self, region, satellite, scan_time_utc):
        # do we want to automatically process the data? or have a process method that user must call?

    def _get(self):
        # we only need bands 2, 3, 6, 7, 14, and 15 for threshold model, should we only get these bands or all of them?

        # I don't think that we should persist automatically, let the user call to_netcdf, of use the downloader bin script
        # ABI-L1b-RadM/2019/001/00/OR_ABI-L1b-RadM1-M3C01_G17_s20190010000270_e20190010000327_c20190010000358.nc

        # check local first?
        key_format = "ABI-L1b-RadM/{year}/{day_of_year}/{hour}/OR_ABI-L1b-Rad{region}-{**}C{channel}_{satellite_shorthand}_s{YYYYDOYHHMM***}0_e{**************}_c{**************}.nc"

        # or can use utilities.query_s3

    def plot(self):

    def to_netcdf(self):

    def process(self):
        # process all bands
        # either reflectance factor or brightness temperature
        # either scale everything down to 500m or up to 2km

    def highlight_wildfires(self):
        # must have processed the data already
        return (
            self._is_hot() &
            (self._is_night() | (self.is_not_cloud() & self._is_not_water))
        )

    def plot_wildfire(self):


    @staticmethod
    def _calculate_reflectance_factor():
        return dataset.assign(reflectance_factor=lambda ds: ds.Rad * ds.kappa0)

    @staticmethod
    def _calculate_brightness_temperature():
        return dataset.assign(
            brightness_temperature=lambda ds: (
                (ds.planck_fk2 / (np.log((ds.planck_fk1 / ds.Rad) + 1)) - ds.planck_bc1)
                / ds.planck_bc2
            )
        )

    @staticmethod
    def _rescale_to_500m():

    @staticmethod
    def _rescale_to_2km():

    def _is_hot():
        condition_1 = _normalize(self.band_7.brightness_temperature.data) > 2
        condition_2 = _normalize(
            self.band_7.brightness_temperature.data - self.band_14.dataset.brightness_temperature.data
        ) > 3
        return condition_1 & condition_2

    def _is_not_water():
        return self.band_6.reflectance_factor.data > 0.03

    def _is_night():
        return (
            (np.abs(self.band_2.reflectance_factor.data[::4, ::4]) < 0.008) |
            (np.abs(self.band_3.reflectance_factor.data[::2, ::2]) < 0.008)
        )


    def is_not_cloud():
        band_2 = self.band_2.reflectance_factor.data[::4, ::4]
        band_3 = self.band_3.reflectance_factor.data[::2, ::2]
        band_15 = self.band_15.brightness_temperature.data

        condition_1 = (band_2 + band_3) < 1.2
        condition_2 = band_15 > 265
        condition_3 = ((band_2 + band_3) < 0.5) | (band_15 > 285)
        return condition_1 & condition_2 & condition_3
