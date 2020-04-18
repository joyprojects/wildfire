import glob
import os

import pytest
import xarray as xr

from wildfire.data import goes_level_1


@pytest.fixture()
def reflective_band():
    return xr.load_dataset(
        os.path.join(
            "tests",
            "resources",
            "test_scan_wildfire",
            "ABI-L1b-RadM",
            "2019",
            "300",
            "20",
            "OR_ABI-L1b-RadM1-M6C01_G17_s20193002000275_e20193002000332_c20193002000379.nc",
        )
    )


@pytest.fixture()
def emissive_band():
    return xr.load_dataset(
        os.path.join(
            "tests",
            "resources",
            "test_scan_wildfire",
            "ABI-L1b-RadM",
            "2019",
            "300",
            "20",
            "OR_ABI-L1b-RadM1-M6C07_G17_s20193002000275_e20193002000344_c20193002000390.nc",
        )
    )


@pytest.fixture()
def all_bands_wildfire():
    return [
        goes_level_1.read_netcdf(local_filepath=filepath)
        for filepath in glob.glob(
            os.path.join(
                "tests",
                "resources",
                "test_scan_wildfire",
                "ABI-L1b-RadM",
                "2019",
                "300",
                "20",
                "*.nc",
            )
        )
    ]


@pytest.fixture()
def all_bands_no_wildfire():
    return [
        goes_level_1.read_netcdf(local_filepath=filepath)
        for filepath in glob.glob(
            os.path.join(
                "tests",
                "resources",
                "test_scan_no_wildfire",
                "ABI-L1b-RadM",
                "2019",
                "335",
                "10",
                "*.nc",
            )
        )
    ]


@pytest.fixture()
def wildfire_scan_filepaths():
    return glob.glob(
        os.path.join(
            "tests",
            "resources",
            "test_scan_wildfire",
            "ABI-L1b-RadM",
            "2019",
            "300",
            "20",
            "*.nc",
        )
    )


@pytest.fixture()
def no_wildfire_scan_filepaths():
    return glob.glob(
        os.path.join(
            "tests",
            "resources",
            "test_scan_no_wildfire",
            "ABI-L1b-RadM",
            "2019",
            "335",
            "10",
            "*.nc",
        )
    )


@pytest.fixture()
def s3_filepath():
    return (  # in the format used by the s3fs library
        "noaa-goes17/ABI-L1b-RadM/2019/001/00/"
        "OR_ABI-L1b-RadM1-M3C01_G17_s20190010000270_e20190010000327_c20190010000358.nc"
    )
