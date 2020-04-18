"""Utilities for the GOES level 2 product."""
import datetime

from .. import goes_level_1

SCAN_TYPE = {"Full Disk": "F", "CONUS": "C"}


def match_level_1(level_2, level_1_directory, download=False):
    """For a given GOES level 2 product, find the level 1 product from the same scan."""
    start_time = datetime.datetime.strptime(
        level_2.attrs["time_coverage_start"], "%Y-%m-%dT%H:%M:%S.%fZ"
    )
    satellite = goes_level_1.utilities.SATELLITE_LONG_HAND[level_2.attrs["platform_ID"]]
    region = SCAN_TYPE[level_2.attrs["scene_id"]]

    if download:
        level_1_files = goes_level_1.downloader.download_files(
            local_directory=level_1_directory,
            satellite=satellite,
            region=region,
            start_time=start_time,
        )
    else:
        level_1_files = goes_level_1.utilities.list_local_files(
            local_directory=level_1_directory,
            satellite=satellite,
            region=region,
            start_time=start_time,
        )
    level_1_scan = goes_level_1.read_netcdfs(local_filepaths=level_1_files)
    return level_1_scan
