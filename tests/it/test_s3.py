import datetime
import os
import tempfile

import boto3
import xarray as xr

from wildfire.goes import downloader


def test_persist_s3():
    bucket = "noaa-goes17"
    key = "ABI-L1b-RadM/2019/001/00/OR_ABI-L1b-RadM1-M3C01_G17_s20190010000270_e20190010000327_c20190010000358.nc"
    with tempfile.TemporaryDirectory() as temp_dir:
        actual = downloader.persist_s3(
            s3_bucket=bucket, s3_key=key, local_directory=temp_dir
        )
        assert os.path.exists(actual)

        actual = xr.open_dataset(filename_or_obj=actual)
        assert actual.dataset_name == os.path.basename(key)


def test_read_s3():
    bucket = "noaa-goes17"
    key = "ABI-L1b-RadM/2019/001/00/OR_ABI-L1b-RadM1-M3C01_G17_s20190010000270_e20190010000327_c20190010000358.nc"
    actual = downloader.read_s3(s3_bucket=bucket, s3_key=key)
    assert isinstance(actual, xr.core.dataset.Dataset)


def test_query_s3():
    actual = downloader.query_s3(
        satellite="noaa-goes17",
        regions=["M2"],
        channels=[1],
        start=datetime.datetime(2019, 1, 1, 1),
        end=datetime.datetime(2019, 1, 1, 2),
    )
    assert len(actual) == 60


def test_download_batch():
    with tempfile.TemporaryDirectory() as temp_dir:
        actual = downloader.download_batch(
            satellite="noaa-goes17",
            regions=["M2"],
            channels=[1],
            start=datetime.datetime(2019, 1, 1, 1),
            end=datetime.datetime(2019, 1, 1, 1, 1),
            local_directory=temp_dir,
        )
        assert len(actual) == 1

        local_filepath = actual[0]
        actual = local_filepath
        assert os.path.exists(actual)

        actual = xr.open_dataset(filename_or_obj=actual)
        assert actual.dataset_name == os.path.basename(local_filepath)
