import datetime
import glob
import multiprocessing
import os
import time

import numpy as np

from wildfire.data.goes_level_1 import utilities


def test_parse_filename():
    filepath = "/ABI-L1b-RadM/2019/300/20/OR_ABI-L1b-RadM1-M6C14_G17_s20193002048275_e20193002048332_c20193002048405.nc"
    actual = utilities.parse_filename(filename=filepath)
    assert actual[0] == "M1"
    assert actual[1] == 14
    assert actual[2] == "G17"
    assert actual[3] == datetime.datetime(2019, 10, 27, 20, 48, 27, 500000)


def test_group_filepaths_into_scans(l1_wildfire_scan_filepaths):
    actual = utilities.group_filepaths_into_scans(filepaths=l1_wildfire_scan_filepaths)
    assert len(actual) == 1
    assert len(actual[0]) == 16


def test_decide_fastest_glob_patterns():
    # no end_time
    actual = utilities.decide_fastest_glob_patterns(
        directory="test_dir",
        satellite="noaa-goes17",
        region="M1",
        start_time=datetime.datetime(2019, 1, 1, 1, 1),
        end_time=None,
    )
    assert len(actual) == 1
    assert actual[0].count("*") == 1

    # differce 1 minunte
    actual = utilities.decide_fastest_glob_patterns(
        directory="test_dir",
        satellite="noaa-goes17",
        region="M1",
        start_time=datetime.datetime(2019, 1, 1, 1, 1),
        end_time=datetime.datetime(2019, 1, 1, 1, 2),
    )
    assert len(actual) == 1
    assert actual[0].count("*") == 2

    # difference 1 hour
    actual = utilities.decide_fastest_glob_patterns(
        directory="test_dir",
        satellite="noaa-goes17",
        region="M1",
        start_time=datetime.datetime(2019, 1, 1, 1, 1),
        end_time=datetime.datetime(2019, 1, 1, 2, 1),
    )
    assert len(actual) == 2
    assert actual[0].count("*") == 2

    # difference 1 day
    actual = utilities.decide_fastest_glob_patterns(
        directory="test_dir",
        satellite="noaa-goes17",
        region="M1",
        start_time=datetime.datetime(2019, 1, 1, 1, 1),
        end_time=datetime.datetime(2019, 1, 2, 1, 1),
    )
    assert len(actual) == 2
    assert actual[0].count("*") == 3

    # difference 1 month
    actual = utilities.decide_fastest_glob_patterns(
        directory="test_dir",
        satellite="noaa-goes17",
        region="M1",
        start_time=datetime.datetime(2019, 1, 1, 1, 1),
        end_time=datetime.datetime(2019, 2, 1, 1, 1),
    )
    assert len(actual) == 32
    assert actual[0].count("*") == 3

    # difference 1 year
    actual = utilities.decide_fastest_glob_patterns(
        directory="test_dir",
        satellite="noaa-goes17",
        region="M1",
        start_time=datetime.datetime(2019, 1, 1, 1, 1),
        end_time=datetime.datetime(2020, 1, 1, 1, 1),
    )
    assert len(actual) == 2
    assert actual[0].count("*") == 4


def test_list_local_files(l1_wildfire_scan_filepaths):
    actual = utilities.list_local_files(
        local_directory=os.path.join("tests", "resources", "goes_level_1_scan_wildfire"),
        satellite="noaa-goes17",
        region="M1",
        start_time=datetime.datetime(2019, 10, 27, 20, 0),
    )
    assert not set(actual) - set(l1_wildfire_scan_filepaths)

    actual = utilities.list_local_files(
        local_directory=os.path.join("tests", "resources", "goes_level_1_scan_wildfire"),
        satellite="noaa-goes17",
        region="M1",
        start_time=datetime.datetime(2019, 10, 27, 20, 0),
        end_time=datetime.datetime(2019, 10, 27, 20, 1),
    )
    assert not set(actual) - set(l1_wildfire_scan_filepaths)


def test_flatten_array():
    actual = utilities.flatten_array([[1], [2], [3], [4]])
    np.testing.assert_array_equal(actual, np.array([1, 2, 3, 4]))
