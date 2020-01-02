import datetime
import os
import tempfile

import boto3
import xarray as xr

from wildfire.goes import downloader


def test_persist_s3(s3_bucket_key):
    with tempfile.TemporaryDirectory() as temp_dir:
        actual = downloader.persist_s3(
            s3_bucket=s3_bucket_key["bucket"],
            s3_key=s3_bucket_key["key"],
            local_directory=temp_dir,
        )
        assert os.path.exists(actual)

        actual = xr.open_dataset(filename_or_obj=actual)
        assert actual.dataset_name == os.path.basename(s3_bucket_key["key"])


def test_read_s3(s3_bucket_key):
    actual = downloader.read_s3(
        s3_bucket=s3_bucket_key["bucket"], s3_key=s3_bucket_key["key"]
    )
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


def test_download_batch(s3_bucket_key):
    s3 = boto3.resource("s3")
    test_object = s3.ObjectSummary(
        bucket_name=s3_bucket_key["bucket"], key=s3_bucket_key["key"]
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        actual = downloader.download_batch(
            s3_object_summaries=[test_object], local_directory=temp_dir,
        )
        assert len(actual) == 1

        local_filepath = actual[0]
        actual = local_filepath
        assert os.path.exists(actual)

        actual = xr.open_dataset(filename_or_obj=actual)
        assert actual.dataset_name == os.path.basename(local_filepath)
