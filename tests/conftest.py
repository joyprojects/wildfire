import glob
import os

import pytest
import xarray as xr

from wildfire.goes.sequence import GoesSequence


@pytest.fixture()
def reflective_band():
    return xr.open_dataset(
        os.path.join(
            "tests",
            "resources",
            "test_scan_wildfire",
            "OR_ABI-L1b-RadM1-M6C01_G17_s20193002000275_e20193002000332_c20193002000379.nc",
        )
    )


@pytest.fixture()
def emissive_band():
    return xr.open_dataset(
        os.path.join(
            "tests",
            "resources",
            "test_scan_wildfire",
            "OR_ABI-L1b-RadM1-M6C07_G17_s20193002000275_e20193002000344_c20193002000390.nc",
        )
    )


@pytest.fixture()
def all_bands_wildfire():
    return [
        xr.open_dataset(filepath)
        for filepath in glob.glob(
            os.path.join("tests", "resources", "test_scan_wildfire", "*")
        )
    ]


@pytest.fixture()
def all_bands_no_wildfire():
    return [
        xr.open_dataset(filepath)
        for filepath in glob.glob(
            os.path.join("tests", "resources", "test_scan_no_wildfire", "*")
        )
    ]


@pytest.fixture()
def s3_bucket_key():
    return {
        "bucket": "noaa-goes17",
        "key": "ABI-L1b-RadM/2019/001/00/OR_ABI-L1b-RadM1-M3C01_G17_s20190010000270_e20190010000327_c20190010000358.nc",
    }
