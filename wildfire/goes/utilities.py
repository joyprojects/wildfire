"""Utilities to use across modules in the goes sub-package."""
import os


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
