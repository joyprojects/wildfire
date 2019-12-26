# pylint: disable=protected-access
import datetime
import os
import tempfile

import xarray as xr

from wildfire.goes import scan

SCAN_FILE_PATH = "ABI-L1b-RadM/2019/001/00/OR_ABI-L1b-RadM1-M3C01_G17_s20190010000270_e20190010000327_c20190010000358.nc"
SCAN_LOCAL_DIRECTORY = "tests/resources"


def test_read_netcdf_local():
    actual = scan.read_netcdf(os.path.join(SCAN_LOCAL_DIRECTORY, SCAN_FILE_PATH))
    assert isinstance(actual, scan.GoesScan)


def test_read_from_local():
    actual = scan._read_from_local(os.path.join(SCAN_LOCAL_DIRECTORY, SCAN_FILE_PATH))
    assert isinstance(actual, xr.core.dataset.Dataset)


def test_goes_scan():
    actual = scan.GoesScan(
        dataset=scan._read_from_local(os.path.join(SCAN_LOCAL_DIRECTORY, SCAN_FILE_PATH))
    )
    assert actual.dataset.get("reflectance_factor", None) is not None
    assert actual.dataset.get("brightness_temperature", None) is not None
    assert actual.region == "M1"
    assert actual.channel == 1
    assert actual.satellite == "noaa-goes17"
    assert actual.started_at == datetime.datetime(2019, 1, 1, 0, 0, 27)

    with tempfile.TemporaryDirectory() as temp_directory:
        local_filepath = actual.to_netcdf(directory=temp_directory)
        assert os.path.exists(local_filepath)
        assert local_filepath == os.path.join(
            temp_directory, "noaa-goes17", SCAN_FILE_PATH
        )
