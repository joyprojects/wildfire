"""Wrapper around the 16 bands of a GOES satellite scan."""
import math

import matplotlib.pyplot as plt
import numpy as np

from . import band, downloader, utilities


def get_goes_scan(satellite, region, scan_time_utc, local_directory, s3=True):
    """Read the GoesScan defined by parameters from the local filesystem or s3.

    Gives preference to scans already on the local filesystem with downloading from
    Amazon S3 used as a backup.

    Parameters
    ----------
    satellite : str
        Must be in set (noaa-goes16, noaa-goes17).
    region : str
        Must be in set (M1, M2, C, F).
    scan_time_utc : datetime.datetime
    local_directory : str
    s3 : bool
        Whether s3 access is allowed.

    Returns
    -------
    GoesScan
    """
    local_filepaths = utilities.list_local_files(
        local_directory=local_directory,
        satellite=satellite,
        region=region,
        start_time=scan_time_utc,
    )

    if len(local_filepaths) == 16:
        return read_netcdfs(local_filepaths=local_filepaths)

    if s3:
        downloaded_filepaths = downloader.download_files(
            local_directory=local_directory,
            satellite=satellite,
            region=region,
            start_time=scan_time_utc,
        )
        if len(downloaded_filepaths) == 16:
            return read_netcdfs(local_filepaths=downloaded_filepaths)

        raise ValueError(
            f"Could not find well-formed scan. local: {len(local_filepaths)} files; "
            f"downloaded: {len(downloaded_filepaths)} files"
        )
    raise ValueError(f"Could not find scan. local: {len(local_filepaths)} files")


def read_netcdfs(local_filepaths, transform_func=None):
    """Read scan defined by `filepaths` from the local filesystem as GoesScan.

    If `transform_func` is provided, then transform datasets defined by `filepaths` before
    returning.

    Parameters
    ----------
    local_filepaths : list of str
    transform_func : function
        (xr.core.dataset.Dataset) -> (xr.core.dataset.Dataset)

    Returns
    -------
    GoesScan
    """
    return GoesScan(
        bands=[
            band.read_netcdf(local_filepath=filepath, transform_func=transform_func)
            for filepath in local_filepaths
        ]
    )


class GoesScan:
    """Wrapper around the 16 bands of a GOES satellite scan.

    Attributes
    ----------
    bands : dict
        {"band_{idx}": wildfire.data.goes_level_1.GoesBand},
        where `idx` are the integers between 1 and 16 inclusive and ordered from least
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
        bands : list of wildfire.data.goes_level_1.GoesBand

        Raises
        ------
        ValueError
            If `bands` is not of type `list of wildfire.data.goes_level_1.GoesBand` or if `bands`
            is not of length 16, with one element for each band scanned.
        """
        self.bands = self._parse_input(bands=bands)
        self.region, _, self.satellite, self.scan_time_utc = utilities.parse_filename(
            filename=bands[0].dataset.dataset_name
        )

    def __repr__(self):
        """Represent GoesScan."""
        return (
            f"GoesScan(satellite={self.satellite}, region={self.region}, "
            f"scan_time={self.scan_time_utc:%Y-%m-%dT%H:%M:%S})"
        )

    def __eq__(self, other):
        """Overrides default implementation."""
        if isinstance(other, GoesScan):
            return (
                (self.satellite == other.satellite)
                & (self.scan_time_utc == other.scan_time_utc)
                & (self.region == other.region)
            )
        return False

    def __getitem__(self, key):
        """Get the GoesBand at a specific band in the scan.

        Parameters
        ----------
        key : str
            Of the form "band_{number}", where `number` is between 1 and 16 inclusive.
            e.g. "band_7"

        Returns
        -------
        wildfire.data.goes_level_1.GoesBand
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
        bands : list of wildfire.data.goes_level_1.GoesBand

        Returns
        -------
        dict
            Of the form:
                {str: wildfire.data.goes_level_1.GoesBand}
            A dictionary of GOES satellite data, ordered by band number from smallest to
            greatest.
        """
        parsed = {band.band_id: band for band in bands}
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

    def rescale_to_2km(self):
        """Scale all bands to 2 kilometers.

        The spatial resolution is band-dependent:
            2 km: bands 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16
            1 km: bands 1, 3, 5
            500 m: band 2

        To perform any operation comparing data from different bands, it may be important
        to first rescale the bands of interest to the same spatial resolution.

        Notes
        -----
        We are currently ignoring the fact that after rescaling the X and Y coordinates
        across the different bands don't correspond. We rely on the fact that they are
        close enough to each other such that they can be appoximated by the coordinates
        of a 2km band (namely band 16), however, this could open up problems in the
        future.

        Returns
        -------
        GoesScan
            A `GoesScan` object where each band has been spatially rescaled to 2 km.
        """
        band_16_coords = {
            "x": self["band_16"].dataset.x.values,
            "y": self["band_16"].dataset.y.values,
        }
        return GoesScan(
            bands=[
                band.GoesBand(
                    band_ds.rescale_to_2km().dataset.assign_coords(**band_16_coords)
                )
                for _, band_ds in self.iteritems()
            ]
        )

    def to_netcdf(self, directory):
        """Persist a netcdf4 per band.

        Persists files in a form matching the file struture in Amazon S3:
            {directory}/{s3_key}
        For example:
            {directory}/ABI-L1b-RadM/2019/300/20/
            OR_ABI-L1b-RadM1-M6C14_G17_s20193002048275_e20193002048332_c20193002048405.nc

        Parameters
        ----------
        directory : str
            Path to local directory in which to persist the datasets.

        Returns
        -------
        list of str
            The filepaths of the persisted files.
        """
        filepaths = []
        for _, goes_band in self.iteritems():
            filepaths.append(goes_band.to_netcdf(directory=directory))
        return filepaths

    def plot(self, bands=range(1, 17), use_radiance=False):
        """Plot the specified bands.

        Parameters
        ----------
        bands : list of int
            Each element must be between 1 and 16 inclusive.
        use_radiance : bool
            Optional, whether to plot the spectral radiance. Defaults to `False`, which
            will plot either the reflectance factor or the brightness temperature
            depending on the band (reflectance factor for bands 1 - 6 and brightness
            temperature for bands 7 - 16).

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
            ncols=num_cols, nrows=num_rows, figsize=(10 * num_cols, 7 * num_rows)
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
        utilities.parse_filename(filename=band.dataset.dataset_name) for band in bands
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
