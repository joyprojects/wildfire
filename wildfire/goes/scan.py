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
    """Read scan from S3 or local.

    Parameters
    ----------
    filepath : str
        Either an S3 URL, or a local file path.

    Returns
    -------
    GoesScan
    """
    if filepath.startswith("s3://"):
        s3_url = urllib.parse.urlparse(filepath)
        scan_xr = downloader.read_s3(
            s3_bucket=s3_url.netloc, s3_key=s3_url.path.lstrip("/")
        )
    else:
        scan_xr = _read_from_local(filepath)
    return GoesScan(dataset=scan_xr)


def _read_from_local(filepath):
    """Read dataset from local filepath, if exists.

    Raises
    ------
    FileNotFoundError
        If goes scan does not exist at `filepath`

    Returns
    -------
    xr.core.dataset.Dataset
    """
    if os.path.exists(filepath):
        return xr.open_dataset(filepath)
    raise FileNotFoundError(f"Could not find file at {filepath}.")


class GoesScan:  # pylint: disable=too-few-public-methods
    """Wrapper around a single channel-region-time satellite scan from GOES.

    Attributes
    ----------
    dataset : xr.core.dataset.Dataset
    region : str
        In the set (F, M1, M2, C).
    channel : int
       Between 1 - 16.
    satellite : str
        Either "noaa-goes16" or "noaa-goes17".
    started_at_utc : datetime.datetime
        Scan start datetime.
    """

    def __init__(self, dataset):
        """Initialize.

        Parameters
        ----------
        dataset : xr.core.dataset.Dataset
        """
        self.dataset = self._process(dataset=dataset)
        (
            self.region,
            self.channel,
            self.satellite,
            self.started_at,
        ) = utilities.parse_filename(dataset.dataset_name)

    def plot(self, axis=None, **imshow_kwargs):
        """Plot the reflectance factor or the brightness temperature based on channel."""
        if axis is None:
            _, axis = plt.subplots(figsize=(12, 12))
            axis.axis("off")

        title_info = f"{self.channel}\n{self.started_at_utc} UTC"
        if self.channel in range(1, 6):
            axis.set_title(f"Reflectance Factor Band \n{title_info}", fontsize=20)
            axis.imshow(self.dataset.reflectance_factor, **imshow_kwargs)
            return axis

        axis.set_title(f"Brightness Temperature Band \n{title_info}", fontsize=20)
        axis.imshow(self.dataset.brightness_temperature, **imshow_kwargs)
        return axis

    def to_netcdf(self, directory):
        local_filepath = os.path.join(
            directory,
            self.satellite,
            f"ABI-L1b-Rad{self.region[0]}",
            str(self.started_at.year),
            self.started_at.strftime("%j"),
            self.started_at.strftime("%H"),
            self.dataset.dataset_name,
        )
        os.makedirs(os.path.dirname(local_filepath), exist_ok=True)
        self.dataset.to_netcdf(
            path=local_filepath,
            encoding={"x": {"dtype": "float32"}, "y": {"dtype": "float32"}},
        )
        return local_filepath

    def _process(self, dataset):
        """Process scan.

        1. Translate spectral radiance to reflectance factor, based on channel
        2. Translate spectral radiance to brightness temperature, based on channel
        """
        _logger.info("Processing scan...")
        dataset = self._calculate_reflectance_factor(dataset=dataset)
        dataset = self._calculate_brightness_temperature(dataset=dataset)
        return dataset

    @staticmethod
    def _calculate_reflectance_factor(dataset):
        return dataset.assign(reflectance_factor=lambda ds: ds.Rad * ds.kappa0)

    @staticmethod
    def _calculate_brightness_temperature(dataset):
        return dataset.assign(
            brightness_temperature=lambda ds: (
                (ds.planck_fk2 / (np.log((ds.planck_fk1 / ds.Rad) + 1)) - ds.planck_bc1)
                / ds.planck_bc2
            )
        )
