"""Wrapper around a time series of GOES satellite scans."""
import datetime
import logging
import multiprocessing

import boto3

from .scan import GoesScan, read_netcdfs
from . import downloader, utilities

_logger = logging.getLogger(__name__)


def get_goes_sequence(
    satellite, region, start_time_utc, end_time_utc, max_scans_per_hour=None, threads=None
):
    """Get the GoesSequence corresponding to the input.

    Parameters
    ----------
    satellite : str
        Must be in the set (G16, G17).
    region : str
        Must be in the set (C, F, M1, M2).
    start_time_utc : datetime.datetime
        Datetime of the first scan. Must be specified to the minute.
    end_time_utc : datetime.datetime
        Datetime of the last scan. Must be specified to the minute.
    max_scans_per_hour : int
        Optional, maximum number of scans to get per hour. Defaults to `None` which will
        get all scans available. The number of scans available per hour is also dependent
        on the region scanned.
    threads : int
        Optional, maximum number of threads to use in parallel. Defaults to `None` which
        will use the number of cores available to set the number of threads.

    Returns
    -------
    GoesSequence
    """
    _logger.info("Getting GoesSequence from S3...")
    if max_scans_per_hour is None:
        max_scans_per_hour = -1

    threads = threads if not None else multiprocessing.cpu_count()
    _logger.info("Using %s threads..", threads)

    s3_objects = downloader.query_s3(
        satellite=satellite,
        regions=[region],
        channels=list(range(1, 17)),
        start=start_time_utc,
        end=end_time_utc,
    )
    s3_objects = [(s3_object.bucket_name, s3_object.key) for s3_object in s3_objects]

    if len(s3_objects) == 0:
        raise ValueError(f"Could not find well-formed scans matching parameters")

    time_resolution = max(
        [60 // max_scans_per_hour, (utilities.REGION_TIME_RESOLUTION_MINUTES[region])]
    )
    scan_times_utc = _create_range_of_utc_times(
        start_time_utc=start_time_utc,
        end_time_utc=end_time_utc,
        time_resolution_minutes=time_resolution,
    )
    pool = multiprocessing.Pool(threads)
    scans = pool.starmap(
        func=_download_sequence,
        iterable=[[s3_objects, scan_time] for scan_time in scan_times_utc],
    )
    return GoesSequence(scans=[scan for scan in scans if scan is not None])


def _download_sequence(s3_objects, scan_time):
    """Download a GoesScan for a give scan time.

    ** This function is used in starmap. Starmap requires that the arguments to this method
    be pickle-able. Natively, s3ObjectSummaries are not pickle-able, hence we convert s3Objects to
    and from bucket and key strings.

    Parameters
    ----------
    s3_objects : list of tuple of (str, str)
    scan_time : datetime.datetime

    Returns
    -------
    wildfire.goes.GoesScan
    """
    _logger.info("Finding scan close to %s", scan_time)
    s3 = boto3.resource("s3")
    s3_objects = [s3.ObjectSummary(bucket, key) for bucket, key in s3_objects]
    closest_scan_objects = utilities.find_scans_closest_to_time(
        s3_scans=s3_objects, desired_time=scan_time
    )
    if len(closest_scan_objects) != 16:
        _logger.warning("Could not find well-formed scan near %s", scan_time)
        return None
    return read_netcdfs(
        filepaths=[
            f"s3://{s3_obj.bucket_name}/{s3_obj.key}" for s3_obj in closest_scan_objects
        ]
    )


def _create_range_of_utc_times(start_time_utc, end_time_utc, time_resolution_minutes):
    """Create a list of times over a time period given a resolution interval.

    Parameters
    ----------
    start_time_utc : datetime.datetime
    end_time_utc : datetime.datetime
    time_resolution_minutes : int

    Returns
    -------
        list of datetime.datetime
    """
    utc_time_range = []
    current_time_utc = start_time_utc
    while current_time_utc <= end_time_utc:
        utc_time_range.append(current_time_utc)
        current_time_utc += datetime.timedelta(minutes=time_resolution_minutes)

    return utc_time_range


class GoesSequence:
    """Wrapper around a time series of GOES satellite scans.

    Attributes
    ----------
    scans : dict
        {datetime.datetime: wildfire.goes.scan.GoesScan}
        Is ordered by smallest key to largest key
    satellite : str
        Must be in the set (G16, G17).
    region : str
        Must be in the set (C, F, M1, M2).
    first_scan_utc : datetime.datetime
        Datetime of first scan in sequence.
    last_scan_utc : datetime.datetime
        Datetime of last scan in sequence.
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
        self.satellite = scans[0].satellite
        self.region = scans[0].region
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
        filepaths = []
        for _, goes_scan in self.iteritems():
            for _, goes_band in goes_scan.iteritems():
                filepaths.append(goes_band.to_netcdf(directory=directory))
        return filepaths


def _assert_input_goes_scan(scans):
    for scan in scans:
        if not isinstance(scan, GoesScan):
            raise ValueError(
                f"Input must be of type list of GoesScan. Found {type(scan)}"
            )
