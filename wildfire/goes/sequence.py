"""Wrapper around a time series of GOES satellite scans."""
from .scan import GoesScan


def get_goes_sequence(
    satellite, region, band, start_time_utc, end_time_utc, time_resolution_per_hour=None
):
    """Get the GoesSequence corresponding to the input.

    Parameters
    ----------
    satellite : str
        Must be in the set (G16, G17).
    region : str
        Must be in the set (C, F, M1, M2).
    band : int
        Must be between 1 and 16 inclusive.
    start_time_utc : datetime.datetime
        Datetime of the first scan. Must be specified to the minute.
    end_time_utc : datetime.datetime
        Datetime of the last scan. Must be specified to the minute.
    time_resolution_per_hour : int
        Optional, number of scans to get per hout. Defaults to `None` which will get all
        scans available.

    Returns
    -------
    GoesSequence
    """
    raise NotImplementedError


class GoesSequence:
    """Wrapper around a time series of GOES satellite scans.

    Attributes
    ----------
    scans : dict
        {datetime.datetime: wildfire.goes.scan.GoesScan}
        Is ordered by smallest key to largest key
    first_scan_utc : datetime.datetime
    last_scan_utc : datetime.datetime
    """

    def __init__(self, scans):
        """Initialize.

        Parameters
        ----------
        scans : list of wildfire.goes.scan.GoesScan

        Raises
        ------
        ValueError
            If `scans` is not of type `list of wildfire.goes.scan.GoesScan`.
        """
        self.scans = self._parse_input(scans=scans)
        self.first_scan_utc = min(self.scans.keys())
        self.last_scan_utc = max(self.scans.keys())

    def __getitem__(self, key):
        """Get the GoesScan at a specific scan time in the sequence.

        Parameters
        ----------
        key : datetime.datetime
            Must be specific to the minute, and a valid key to `self.scans`.

        Returns
        -------
        wildfire.goes.scan.GoesScan
        """
        return self.scans[key]

    def __len__(self):
        """Return the number of scans in the sequence."""
        return len(self.scans)

    @staticmethod
    def _parse_input(scans):
        _assert_input_goes_scan(scans)
        parsed = {scan.scan_time_utc: scan for scan in scans}
        ordered_keys = sorted(parsed.keys())
        return {key: parsed[key] for key in ordered_keys}

    @property
    def keys(self):
        """List scan times in the sequence."""
        return self.scans.keys()

    def iteritems(self):
        """Iterate over the scans in the sequence from first scan to last scan.

        Ordered from least to greatest by datetime.
        """
        return self.scans.items()

    def plot(self, band):
        """Plot the time-series of a specific band as a GIF.

        Parameters
        ----------
        band : int
            Must be between 1 and 16 inclusive.

        Returns
        -------
        None
        """
        raise NotImplementedError

    def to_netcdf(self, directory):
        """Persist a netcdf4 per band per GoesScan.

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


def _assert_input_goes_scan(scans):
    for scan in scans:
        if not isinstance(scan, GoesScan):
            raise ValueError(
                f"Input must be of type list of GoesScan. Found {type(scan)}"
            )
