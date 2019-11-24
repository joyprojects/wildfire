# pylint: disable=protected-access
import datetime
import os
import tempfile

from wildfire.goes import downloader


def test_make_necessary_directories():
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "this/is/a/test/filepath/")
        assert not os.path.exists(file_path)
        downloader.make_necessary_directories(file_path)
        assert os.path.exists(file_path)


def test_is_good_object():
    key = "/ABI-L1b-RadM/2019/300/20/OR_ABI-L1b-RadM1-M6C14_G17_s20193002048275_e20193002048332_c20193002048405.nc"

    assert downloader._is_good_object(
        key=key,
        regions=["M1"],
        channels=[14],
        start=datetime.datetime(2019, 1, 1),
        end=datetime.datetime(2019, 12, 1),
    )
    assert not downloader._is_good_object(
        key=key,
        regions=["M2"],
        channels=[14],
        start=datetime.datetime(2019, 1, 1),
        end=datetime.datetime(2019, 12, 1),
    )
    assert not downloader._is_good_object(
        key=key,
        regions=["M1"],
        channels=[1],
        start=datetime.datetime(2019, 1, 1),
        end=datetime.datetime(2019, 12, 1),
    )
    assert not downloader._is_good_object(
        key=key,
        regions=["M1"],
        channels=[14],
        start=datetime.datetime(2019, 11, 1),
        end=datetime.datetime(2019, 12, 1),
    )


def test_num_hours_to_check():
    actual = downloader._num_hours_to_check(
        start=datetime.datetime(2019, 12, 1, 1, 30),
        end=datetime.datetime(2019, 12, 1, 10),
    )
    assert actual == 9

    actual = downloader._num_hours_to_check(
        start=datetime.datetime(2019, 12, 1, 1, 30),
        end=datetime.datetime(2019, 12, 2, 10),
    )
    assert actual == 24 + 9
