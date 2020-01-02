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


def test_is_good_object(s3_bucket_key):
    assert downloader._is_good_object(
        key=s3_bucket_key["key"],
        regions=["M1"],
        channels=[1],
        start=datetime.datetime(2019, 1, 1),
        end=datetime.datetime(2019, 12, 1),
    )
    assert not downloader._is_good_object(
        key=s3_bucket_key["key"],
        regions=["M2"],
        channels=[1],
        start=datetime.datetime(2019, 1, 1),
        end=datetime.datetime(2019, 12, 1),
    )
    assert not downloader._is_good_object(
        key=s3_bucket_key["key"],
        regions=["M1"],
        channels=[14],
        start=datetime.datetime(2019, 1, 1),
        end=datetime.datetime(2019, 12, 1),
    )
    assert not downloader._is_good_object(
        key=s3_bucket_key["key"],
        regions=["M1"],
        channels=[1],
        start=datetime.datetime(2019, 11, 1),
        end=datetime.datetime(2019, 12, 1),
    )
