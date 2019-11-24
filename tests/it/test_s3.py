import os
import tempfile

import boto3
import xarray as xr

from wildfire.goes import downloader


def test_downloader():
    bucket = "noaa-goes17"
    key = "ABI-L1b-RadM/2019/001/00/OR_ABI-L1b-RadM1-M3C01_G17_s20190010000270_e20190010000327_c20190010000358.nc"
    with tempfile.TemporaryDirectory() as temp_dir:
        actual = downloader.download_scan(
            s3_bucket=bucket, s3_key=key, local_directory=temp_dir
        )
        assert os.path.exists(actual)

        actual = xr.open_dataset(filename_or_obj=actual)
        assert actual.dataset_name == os.path.basename(key)
