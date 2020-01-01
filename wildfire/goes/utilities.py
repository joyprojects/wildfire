"""Utilities to use across modules in the goes sub-package."""
import datetime
import re
import os

SATELLITE_CONVERSION = {
    # satellite shorthand: satellite bucket name
    "G16": "noaa-goes16",
    "G17": "noaa-goes17",
}


def build_local_path(local_directory, filepath, satellite):
    """Build local path (matched S3 file structure).

    Parameters
    ----------
    local_directory : str
    filepath : str
    satellite : str

    Returns
    -------
    str
        e.g. {local_directory}/noaa-goes17/ABI-L1b-RadM/2019/300/20/
        OR_ABI-L1b-RadM1-M6C14_G17_s20193002048275_e20193002048332_c20193002048405.nc
    """
    return os.path.join(local_directory, satellite, filepath)


def parse_filename(filename):
    """Parse necessary information from the filename.

    This method also verifies correct filename input.

    Examples
    --------
    OR_ABI-L1b-RadM1-M6C14_G17_s20193002048275_e20193002048332_c20193002048405.nc
    Region = M1
    Channel = 14
    Satellite = noaa-goes17
    Scan Start Time = 2019-10-27 20:48:27.5

    Parameters
    ----------
    filename : str

    Returns
    -------
    tuple of (str, int, str, datetime.datetime)
        region, channel, satellite, started_at
    """
    region, channel, satellite, started_at = re.search(
        r"OR_ABI-L1b-Rad(.*)-M\dC(\d{2})_(G\d{2})_s(.*)_e.*_c.*.nc", filename
    ).groups()
    started_at = datetime.datetime.strptime(started_at, "%Y%j%H%M%S%f")
    satellite = SATELLITE_CONVERSION[satellite]
    channel = int(channel)
    return region, channel, satellite, started_at
