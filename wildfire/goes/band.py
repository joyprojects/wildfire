"""Wrapper around the a single band's data from a GOES satellite scan."""
import os

import numpy as np
import xarray as xr

from . import downloader, utilities


def get_goes_band(satellite, region, channel, scan_time_utc, local_directory, s3=True):
    """Read the GoesBand defined by parameters from the local filesystem or s3.

    Gives preference to data already on the local filesystem with downloading from
    Amazon S3 used as a backup, if `s3` is `True`.

    Parameters
    ----------
    satellite : str
        Must be in set (noaa-goes16, noaa-goes17).
    region : str
        Must be in set (M1, M2, C, F).
    channel : int
        Must be between 1 and 16 inclusive.
    scan_time_utc : datetime.datetime
    local_directory : str
    s3 : bool
        Whether s3 access is allowed.

    Returns
    -------
    GoesBand
    """
    local_filepaths = utilities.list_local_files(
        local_directory=local_directory,
        satellite=satellite,
        region=region,
        start_time=scan_time_utc,
        channel=channel,
    )

    if len(local_filepaths) == 1:
        return read_netcdf(local_filepath=local_filepaths[0])

    if s3:
        s3_filepaths = downloader.list_s3_files(
            satellite=satellite, region=region, channel=channel, start_time=scan_time_utc,
        )
        if len(s3_filepaths) == 1:
            downloaded_filepath = downloader.download_file(
                s3_filepath=s3_filepaths[0], local_directory=local_directory,
            )
            return read_netcdf(local_filepath=downloaded_filepath)

        raise ValueError(
            f"Could not find band. local: {len(local_filepaths)} files; "
            f"downloaded: {len(s3_filepaths)} files"
        )
    raise ValueError(f"Could not find band. local: {len(local_filepaths)} files")


def read_netcdf(local_filepath, transform_func=None):
    """Read netcdf4 file defined at `local_filepath`.

    If `transform_func` is provided, then transform dataset defined by `filepath` before
    returning.

    Parameters
    ----------
    local_filepath : str
    transform_func : function
        (xr.core.dataset.Dataset) -> (xr.core.dataset.Dataset)

    Returns
    -------
    GoesBand
    """
    dataset = xr.load_dataset(local_filepath)
    if transform_func is not None:
        dataset = transform_func(dataset)
    return GoesBand(dataset=dataset)


class GoesBand:
    """Wrapper around the a single band's data from a GOES satellite scan.

    Attributes
    ----------
    dataset : xr.core.dataset.Dataset
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
        dataset : xr.core.dataset.Dataset
        """
        self.dataset = dataset
        (
            self.region,
            self.band_id,
            self.satellite,
            self.scan_time_utc,
        ) = utilities.parse_filename(filename=dataset.dataset_name)
        self.band_wavelength_micrometers = dataset.band_wavelength.data[0]

    def __repr__(self):
        """Represent GoesBand."""
        return (
            f"GoesBand(satellite={self.satellite}, region={self.region}, "
            f"band={self.band_id}, wavelength={self.band_wavelength_micrometers:.2f}µm, "
            f"scan_time={self.scan_time_utc:%Y-%m-%dT%H:%M:%S})"
        )

    def plot(self, axis=None, use_radiance=False, **xr_imshow_kwargs):
        """Plot the band.

        If not plotting spectral radiance, will plot the reflectance factor for bands 1 -
        6, and the brightness temperature for bands 7 - 16.

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
            f"Band {self.band_id} ({self.band_wavelength_micrometers:.2f} micrometers)"
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
            return normalize(self.dataset.Rad)

        parsed_data = self.parse()
        return normalize(parsed_data)

    def rescale_to_2km(self):
        """Scale band to 2km meters x 2km meters.

        The spatial resolution is band-dependent:
            2 km: bands 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16
            500 m: bands 1, 3, 5
            1 km: band 2

        Notes
        -----
        We are currently ignoring the fact that after rescaling the X and Y coordinates
        across the different bands don't correspond. We rely on the fact that they are
        close enough to each other, however, this could open up problems in the future.

        Returns
        -------
        GoesBand
            A `GoesBand` object where each band has been rescaled to 500 meters.
        """
        if self.band_id in (1, 3, 5):
            rescaled_data = self.dataset.thin(2)  # 500m -> 2km
        elif self.band_id == 2:
            rescaled_data = self.dataset.thin(4)  # 1km -> 2km
        else:
            rescaled_data = self.dataset  # 2km -> 2km

        return GoesBand(dataset=rescaled_data)

    def parse(self):
        """Parse spectral radiance into appropriate units.

        Will parse into reflectance factor for the reflective bands (1 - 6), and
        brightness temperature for emissive bands (7 - 16).

        Returns
        -------
        xr.core.dataarray.DataArray
        """
        if self.band_id < 7:  # reflective band
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
        return GoesBand(dataset=filter_bad_pixels(dataset=self.dataset))

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


def filter_bad_pixels(dataset):
    """Use the Data Quality Flag (DQF) to filter out bad pixels.

    Each pixel (value according to a specific X-Y coordinate) has a DQF, which ranges
    from 0 (good) to 3 (no value). We follow NOAA's suggestion of filtering out all
    pixes with a flag of 2 or 3.

    Returns
    -------
    xr.core.dataset.Dataset
        An xarray dataset where the spectral radiance (`Rad`) of any pixel with DQF
        greater than 1 is set to `np.nan`.
    """
    return dataset.where(dataset.DQF.isin([0, 1]))


def normalize(data):
    """Normalize data to be centered around 0.

    Parameters
    ----------
    data : np.ndarray | xr.core.dataarray.DataArray

    Returns
    -------
    np.ndarray | xr.core.dataarray.DataArray
    """
    return (data - data.mean()) / data.std()
