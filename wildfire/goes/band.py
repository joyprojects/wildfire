"""Wrapper around the a single band's data from a GOES satellite scan."""
import datetime
import logging
import os
import urllib

import numpy as np
import xarray as xr

from . import downloader, utilities

_logger = logging.getLogger(__name__)


def get_goes_band(satellite, region, band, scan_time_utc):
    """Get the GoesBand corresponding the input.

    Parameters
    ----------
    satellite : str
        Must be in the set (noaa-goes16, noaa-goes17).
    region : str
        Must be in the set (C, F, M1, M2).
    band : int
        Must be between 1 and 16 inclusive.
    scan_time_utc : datetime.datetime
        Datetime of the scan. Must be specified to the minute.

    Returns
    -------
    GoesBand
    """
    region_time_resolution = utilities.REGION_TIME_RESOLUTION_MINUTES[region]
    s3_objects = downloader.query_s3(
        satellite=satellite,
        regions=[region],
        channels=[band],
        start=scan_time_utc - datetime.timedelta(minutes=region_time_resolution),
        end=scan_time_utc + datetime.timedelta(minutes=region_time_resolution),
    )

    if len(s3_objects) == 0:
        raise ValueError(f"Could not find well-formed scan near {scan_time_utc}")

    closest_s3_object = utilities.find_scans_closest_to_times(
        s3_scans=s3_objects, desired_times=[scan_time_utc]
    )[0]
    return read_netcdf(filepath=closest_s3_object)


def read_netcdf(filepath):
    """Read a GoesBand from the filepath.

    Parameters
    ----------
    filepath : str
        May be a local filepath, or an Amazon S3 URI.

    Returns
    -------
    GoesBand
    """
    if filepath.startswith("s3://"):
        s3_url = urllib.parse.urlparse(filepath)
        dataset = downloader.read_s3(
            s3_bucket=s3_url.netloc, s3_key=s3_url.path.lstrip("/")
        )
    else:  # local
        dataset = xr.open_dataset(filepath)
    return GoesBand(dataset=dataset)


class GoesBand:
    """Wrapper around the a single band's data from a GOES satellite scan.

    Attributes
    ----------
    dataset : xr.core.dataset.DataSet
    band : int
        Between 1 and 16 inclusive. The band of light over which the scan was made.
    band_wavelength_micrometers : float
        The central wavelength of the band of light over which the scan was made.
    scan_time_utc : datetime.datetime
        Datetime of the scan's start time.
    satellite : str
        In the set (noaa-goes16, noaa-goes17). The satellite the scan was made by.
    region : str
        In the set (C, F, M1, M2). The region over which the scan was made.
    """

    def __init__(self, dataset):
        """Initialize.

        Parameters
        ----------
        dataset : xr.core.dataset.DataSet
        """
        self.dataset = dataset
        (
            self.region,
            self.band,
            self.satellite,
            self.scan_time_utc,
        ) = utilities.parse_filename(filename=dataset.dataset_name)
        self.band_wavelength_micrometers = dataset.band_wavelength.data[0]

    def plot(self, axis=None, use_radiance=False, **xr_imshow_kwargs):
        """Plot the band.

        If not plotting the radiance, will plot the reflectance factor for bands 1 - 6,
        and the brightness temperature for bands 7 - 16.

        Parameters
        ----------
        axis : plt.axes._subplots.AxesSubplot
            Optional, axis to draw on. Defaults to `None`. If `None`, which causes the
            method to create its own axis object.
        use_radiance : bool
            Optional, whether to plot the spectral radiance. Defaults to `False`, which
            will plot either the reflectance factor or the brightness temperature
            depending on the band.
        **xr_imshow_kwargs : dict
            Keyword arguments for xarray's plotting method
            (http://xarray.pydata.org/en/stable/generated/xarray.plot.imshow.html). Some
            useful keywords are figsize or cmap.

        Returns
        -------
        plt.image.AxesImage
        """
        if use_radiance:
            data = self.dataset.Rad
        else:
            data = self.parse()

        axis_image = data.plot.imshow(ax=axis, **xr_imshow_kwargs)
        axis_image.axes.set_title(
            f"Band {self.band} ({self.band_wavelength_micrometers:.2f} micrometers)"
            f"\n{self.scan_time_utc:%Y-%m-%d %H:%M} UTC",
            fontsize=20,
        )
        axis_image.axes.set_xlabel(None)
        axis_image.axes.set_ylabel(None)
        axis_image.colorbar.ax.yaxis.label.set_size(20)
        return axis_image

    def normalize(self, use_radiance=False):
        """Normalize data to be centered around 0.

        If not normalizing the radiance, will normalize the reflectance factor for bands
        1 - 6, and the brightness temperature for bands 7 - 16.

        Parameters
        ----------
        use_radiance : bool
            Optional, whether to plot the spectral radiance. Defaults to `False`, which
            will normalize either the reflectance factor or the brightness temperature
            depending on the band.

        Returns
        -------
        xr.core.dataarray.DataArray
        """
        if use_radiance:
            return utilities.normalize(self.dataset.Rad)

        parsed_data = self.parse()
        return utilities.normalize(parsed_data)

    def parse(self):
        """Parse spectral radiance into appropriate units.

        Will parse into reflectance factor for the reflective bands (1 - 6), and
        brightness temperature for emissive bands (7 - 16).

        Returns
        -------
        xr.core.dataarray.DataArray
        """
        if self.band < 7:  # reflective band
            return self.reflectance_factor
        # emissive band
        return self.brightness_temperature

    @property
    def reflectance_factor(self):
        """Calculate the reflectance factor from spectral radiance.

        For more information, see the Reflective Channels section at
        https://github.com/joyprojects/wildfire/blob/master/documentation/notebooks/noaa_goes_documentation.ipynb

        Returns
        -------
        xr.core.dataarray.DataArray
        """
        dataarray = self.dataset.Rad * self.dataset.kappa0
        dataarray.attrs["long_name"] = "ABI L1b Reflectance Factor"
        dataarray.attrs["units"] = "unitless"
        return dataarray

    @property
    def brightness_temperature(self):
        """Calculate the brightness temperature from spectral radiance.

        For more information, see the Emissive Channels section at
        https://github.com/joyprojects/wildfire/blob/master/documentation/notebooks/noaa_goes_documentation.ipynb

        Returns
        -------
        xr.core.dataarray.DataArray
        """
        dataarray = (
            self.dataset.planck_fk2
            / (np.log((self.dataset.planck_fk1 / self.dataset.Rad) + 1))
            - self.dataset.planck_bc1
        ) / self.dataset.planck_bc2
        dataarray.attrs["long_name"] = "ABI L1b Brightness Temperature"
        dataarray.attrs["units"] = "Kelvin"
        return dataarray

    def to_lat_lon(self):
        """Convert the X and Y of the ABI fixed grid to latitude and longitude."""
        raise NotImplementedError

    def filter_bad_pixels(self):
        """Use the Data Quality Flag (DQF) to filter out bad pixels.

        Each pixel (value according to a specific X-Y coordinate) has a DQF, which ranges
        from 0 (good) to 3 (no value). We follow NOAA's suggestion of filtering out all
        pixes with a flag of 2 or 3.

        Returns
        -------
        GoesBand
            A `GoesBand` object where the spectral radiance (`Rad`) of any pixel with DQF
            greater than 1 is set to `np.nan`.
        """
        return GoesBand(dataset=self.dataset.where(self.dataset.DQF.isin([0, 1])))

    def to_netcdf(self, directory):
        """Persist to netcdf4.

        Persists file in a form matching the file struture in Amazon S3:
            {local_directory}/{s3_bucket_name}/{s3_key}
        For example:
            {local_directory}/noaa-goes17/ABI-L1b-RadM/2019/300/20/
        OR_ABI-L1b-RadM1-M6C14_G17_s20193002048275_e20193002048332_c20193002048405.nc

        Parameters
        ----------
        directory : str
            Path to local directory in which to persist.

        Returns
        -------
        str
            The filepath of the persisted file.
        """
        local_filepath = os.path.join(
            directory,
            self.satellite,
            f"ABI-L1b-Rad{self.region[0]}",
            str(self.scan_time_utc.year),
            self.scan_time_utc.strftime("%j"),
            self.scan_time_utc.strftime("%H"),
            self.dataset.dataset_name,
        )
        os.makedirs(os.path.dirname(local_filepath), exist_ok=True)
        self.dataset.to_netcdf(
            path=local_filepath,
            encoding={"x": {"dtype": "float32"}, "y": {"dtype": "float32"}},
        )
        return local_filepath
