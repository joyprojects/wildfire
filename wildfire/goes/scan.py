"""Wrapper around the 16 bands of a GOES satellite scan."""
from . import utilities


def get_goes_scan(satellite, region, scan_time_utc):
    """Get the GoesScan corresponding the input.

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
    raise NotImplementedError


def from_netcdfs(filepaths):
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
    raise NotImplementedError


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
        bands : list of wildfire.goes.band.GoesBand

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
        parsed = {dataset.band_id.data[0]: dataset for dataset in bands}
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

    def scale_to_500m(self):
        """Scale all bands to 500 meters.

        The spatial resolution is band-dependent:
            1 km: bands 1, 3, 5
            500 m: band 2
            2 km: bands 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16

        And so, it is sometimes important to downscale all bands to be in the same
        spatial resolution.

        Returns
        -------
        GoesScan
            A `GoesScan` object where each band has been rescaled to 500 meters.
        """
        raise NotImplementedError

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
        raise NotImplementedError

    def next(self):
        """Get the next available `GoesScan` from Amazon S3.

        Returns
        -------
        GoesScan
            A `GoesScan` object of the scan occuring directly after this scan's time.
        """
        raise NotImplementedError

    def previous(self):
        """Get the `GoesScan` from Amazon S3 that occured directly before this scan.

        Returns
        -------
        GoesScan
            A `GoesScan` object of the scan occuring directly before this scan's time.
        """
        raise NotImplementedError

    def plot(self, bands):
        """Plot the specified bands.

        Parameters
        ----------
        bands : list of int
            Each element must be between 1 and 16 inclusive.

        Returns
        -------
        plt.figure.Figure, np.ndarray of plt.axes._subplots.AxesSubplot
        """
        raise NotImplementedError


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
