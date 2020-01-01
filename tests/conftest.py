import glob
import os

import pytest
import xarray as xr


@pytest.fixture()
def single_band():
    return xr.open_dataset(
        os.path.join(
            "tests",
            "resources",
            "test_scan",
            "OR_ABI-L1b-RadM1-M6C01_G17_s20193002000275_e20193002000332_c20193002000379.nc",
        )
    )


@pytest.fixture()
def all_bands():
    scans = []
    for filepath in glob.glob(os.path.join("tests", "resources", "test_scan", "*")):
        scans.append(xr.open_dataset(filepath))
    return scans
