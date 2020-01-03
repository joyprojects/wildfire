"""Wrapper around the 16 bands of a GOES satellite scan."""
import datetime
import logging
import math
import urllib

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import multiprocessing

from . import downloader, utilities
from .band import GoesBand

_logger = logging.getLogger(__name__)


def get_goes_scans(satellite, region, scan_times_utc):
    """"
    Get the GoesScans matching parameters in parallel.

    Retrieves the closest scan to `scan_time_utc` matching the `satellite` and `region`
    from Amazon S3.

    For performance improvement, we use the fact that we know how often the satellite
    produces a scan to limit the window of our search. For example, there is a CONUS
    satellite scan every 5 minutes, so we search a 10 minute window centered on
    `scan_time_utc`.

    Parameters:
    __________
    satellite : str
        Must be in the set (G16, G17).
    region : str
        Must be in the set (C, F, M1, M2).
    scan_times_utc : list of datetime.datetime
        Datetime of the scans. Datetimes must be specified to the minute.

    """
    args = []
    for scan_time_utc in scan_times_utc:
        args.append([satellite, region, scan_time_utc])

    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    file_paths = pool.starmap(get_goes_scan, scan_times_utc)
    return file_paths


def get_goes_scan(satellite, region, scan_time_utc):
    """Get the GoesScan matching parameters.

    Retrieves the closest scan to `scan_time_utc` matching the `satellite` and `region`
    from Amazon S3.

    For performance improvement, we use the fact that we know how often the satellite
    produces a scan to limit the window of our search. For example, there is a CONUS
    satellite scan every 5 minutes, so we search a 10 minute window centered on
    `scan_time_utc`.

    Parameters
    ----------
    satellite : str
        Must be in the set (G16, G17).
    region : str
        Must be in the set (C, F, M1, M2).
    scan_time_utc : datetime.datetime
        Datetime of the scan. Must be specified to the minute.

    Returns
    -------
    GoesScan
    """
    region_time_resolution = utilities.REGION_TIME_RESOLUTION_MINUTES[region]
    s3_objects = downloader.query_s3(
        satellite=satellite,
        regions=[region],
        channels=list(range(1, 17)),
        start=scan_time_utc - datetime.timedelta(minutes=region_time_resolution),
        end=scan_time_utc + datetime.timedelta(minutes=region_time_resolution),
    )
    closest_scan_objects = utilities.find_scans_closest_to_time(
        s3_scans=s3_objects, desired_time=scan_time_utc
    )
    if len(closest_scan_objects) != 16:
        raise ValueError(
            f"Could not find well-formed scan set in s3 near {scan_time_utc}"
        )

    return read_netcdfs(
        filepaths=[
            f"s3://{s3_obj.bucket_name}/{s3_obj.key}" for s3_obj in closest_scan_objects
        ]
    )


def read_netcdfs(filepaths):
    """Read a GoesScan from a list of filepaths.

    Parameters
    ----------
    filepaths : list of str
        List of local filepaths from which to read a GoesScan. There must be 16 filepaths
        each pointing to a different band's data from the same scan.

    Returns
    -------
    GoesScan
    """
    datasets = []
    for filepath in filepaths:
        if filepath.startswith("s3://"):  # s3
            s3_url = urllib.parse.urlparse(filepath)
            dataset = downloader.read_s3(
                s3_bucket=s3_url.netloc, s3_key=s3_url.path.lstrip("/")
            )
        else:  # local
            dataset = xr.open_dataset(filepath)
        datasets.append(dataset)
    return GoesScan(bands=datasets)


class GoesScan:
    """Wrapper around the 16 bands of a GOES satellite scan.

    Attributes
    ----------
    bands : dict
        {
            "band_{idx}": wildfire.goes.band.GoesBand
        }, where `idx` are the integers between 1 and 16 inclusive and ordered from least
        to greatest by `idx`.
    scan_time_utc : datetime.datetime
        Datetime of the scan start time. The same for all bands.
    satellite : str
    In the set (noaa-goes16, noaa-goes17). The satellite the scan was made by. The
    same for all bands.
    region : str
        In the set (C, F, M1, M2). The region over which the scan was made. The same for
        all bands.
    """

    def __init__(self, bands):
        """Initialize.

        Parameters
        ----------
        bands : list of xr.core.dataset.Dataset

        Raises
        ------
        ValueError
            If `bands` is not of type `list of wildfire.goes.band.GoesBand` or if `bands`
            is not of length 16, with one element for each band scanned.
        """
        self.bands = self._parse_input(bands=bands)
        self.region, _, self.satellite, self.scan_time_utc = utilities.parse_filename(
            filename=bands[0].dataset_name
        )

    def __getitem__(self, key):
        """Get the GoesBand at a specific band in the scan.

        Parameters
        ----------
        key : str
            Of the form "band_{number}", where `number` is between 1 and 16 inclusive.

        Returns
        -------
        wildfire.goes.scan.GoesBand
        """
        return self.bands[key]

    @staticmethod
    def _parse_input(bands):
        """Validate and parse __init__ input.

        Create sorted dictionary of band data from a list of band data. Ensure input has
        16 elements with one element for every band between 1 and 16 inclusive. Ensure
        ever element in the list has the same satellite, region, and scan start time.

        Parameters
        ----------
        bands : list of xr.core.dataset.Dataset

        Returns
        -------
        dict of {str: wildfire.goes.band.GoesBand}
            Sorted dictionary of GOES satellite data, ordered by band number from
            smallest to greatest.
        """
        parsed = {dataset.band_id.data[0]: GoesBand(dataset=dataset) for dataset in bands}
        _assert_no_missing_bands(bands=parsed)
        _assert_16_bands(bands=bands)
        _assert_consistent_attributes(bands=bands)
        return {f"band_{band_id}": parsed[band_id] for band_id in list(range(1, 17))}

    @property
    def keys(self):
        """Return the names of the bands for convenience."""
        return self.bands.keys()

    def iteritems(self):
        """Return iterator over the scan in order from band 1 to band 16.

        Ordered from least to greatest by band number.
        """
        return self.bands.items()

    def rescale_to_500m(self):
        """Scale all bands to 500 meters.

        The spatial resolution is band-dependent:
            500 m: bands 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16
            1 km: bands 1, 3, 5
            2 km: band 2

        And so, it is sometimes important to downscale all bands to be in the same
        spatial resolution.

        Notes
        -----
        We are currently ignoring the fact that after rescaling the X and Y coordinates
        across the different bands don't correspond. We rely on the fact that they are
        close enough to each other, however, this could open up problems in the future.

        Returns
        -------
        GoesScan
            A `GoesScan` object where each band has been rescaled to 500 meters.
        """
        rescaled_datasets = []
        for band_id, goes_scan in self.iteritems():
            if band_id in ("band_1", "band_3", "band_5"):
                rescaled_data = goes_scan.dataset.thin(2)  # 1km -> 500m
            elif band_id == "band_2":
                rescaled_data = goes_scan.dataset.thin(4)  # 2km -> 500m
            else:
                rescaled_data = goes_scan.dataset  # 500m -> 500m
            rescaled_datasets.append(rescaled_data)
        return GoesScan(bands=rescaled_datasets)

    def to_netcdf(self, directory):
        """Persist a netcdf4 per band.

        Persists files in a form matching the file struture in Amazon S3:
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
        list of str
            The filepaths of the persisted files.
        """
        filepaths = []
        for _, goes_band in self.iteritems():
            filepaths.append(goes_band.to_netcdf(directory=directory))
        return filepaths

    def next(self, days=0, hours=0, minutes=0):
        """Get the next available `GoesScan` from Amazon S3 matching parameters.

        By default, get the next available scan.

        Parameters
        ----------
        days : int
            Optional, defaults to `0`.
        hours : int
            Optional, defaults to `0`.
        minutes : int
            Optional, defaults to `0`. If both `days` and `hours` are `0`, then this
            defaults to the time resolution of the region.

        Returns
        -------
        GoesScan
            A `GoesScan` object of the next available scan mathcing parameters.
        """
        if days + hours + minutes == 0:
            minutes = utilities.REGION_TIME_RESOLUTION_MINUTES[self.region]

        return get_goes_scan(
            satellite=self.satellite,
            region=self.region,
            scan_time_utc=self.scan_time_utc
            + datetime.timedelta(days=days, hours=hours, minutes=minutes),
        )

    def previous(self, days=0, hours=0, minutes=0):
        """Get the previous `GoesScan` from Amazon S3 that matches parameters.

        By default, get the closest previous available scan.

        Parameters
        ----------
        days : int
            Optional, defaults to `0`
        hours : int
            Optional, defaults to `0`
        minutes : int
            Optional, defaults to `0`. If both `days` and `hours` are `0`, then this
            defaults to the time resolution of the region.

        Returns
        -------
        GoesScan
            A `GoesScan` object of the previous scan matching parameters.
        """
        if days + hours + minutes == 0:
            minutes = utilities.REGION_TIME_RESOLUTION_MINUTES[self.region]

        return get_goes_scan(
            satellite=self.satellite,
            region=self.region,
            scan_time_utc=self.scan_time_utc
            - datetime.timedelta(days=days, hours=hours, minutes=minutes),
        )

    def plot(self, bands, use_radiance=False):
        """Plot the specified bands.

        Parameters
        ----------
        bands : list of int
            Each element must be between 1 and 16 inclusive.
        use_radiance : bool
            Optional, whether to plot the spectral radiance. Defaults to `False`, which
            will plot either the reflectance factor or the brightness temperature
            depending on the band.

        Returns
        -------
        list of plt.image.AxesImage
        """
        _assert_correct_bands(bands=bands)
        max_cols = 3

        num_bands = len(bands)
        num_cols = min([num_bands, max_cols])
        num_rows = math.ceil(num_bands / max_cols)
        _, axes = plt.subplots(
            ncols=num_cols, nrows=num_rows, figsize=(10 * num_cols, 8 * num_rows)
        )
        axes = np.ravel(axes)
        axes_images = []
        for axis, band_id in zip(axes, bands):
            axis_image = self[f"band_{band_id}"].plot(
                axis=axis, use_radiance=use_radiance
            )
            axes_images.append(axis_image)

        plt.tight_layout()

        empty_plots = (num_cols * num_rows) - num_bands
        for axis in axes[-empty_plots:]:
            axis.axis("off")

        return axes_images


def _assert_correct_bands(bands):
    if set(bands) - set(range(1, 17)):
        raise ValueError(f"Some invalid bands (got {bands}")


def _assert_no_missing_bands(bands):
    missing_bands = set(range(1, 17)) - set(bands.keys())
    if missing_bands:
        raise ValueError(f"Missing bands: {missing_bands}")


def _assert_16_bands(bands):
    if len(bands) != 16:
        raise ValueError(f"Too many bands provided (got {len(bands)}; expected 16)")


def _assert_consistent_attributes(bands):
    band_attributes = [
        utilities.parse_filename(filename=dataset.dataset_name) for dataset in bands
    ]
    num_unique_attributes = len(
        {
            (region, satellite, start_time)
            for region, _, satellite, start_time in band_attributes
        }
    )
    if not num_unique_attributes == 1:
        raise ValueError(
            "All bands must have the same scan start time, region, and satellite"
        )
