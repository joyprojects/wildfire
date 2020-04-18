import datetime
import os
import tempfile

import s3fs

from wildfire.data.goes_level_1 import downloader, utilities


def test_list_s3_files():
    region = "M1"
    satellite = "noaa-goes17"
    start_time = datetime.datetime(2019, 1, 1, 1)
    end_time = datetime.datetime(2019, 1, 1, 2)

    actual = downloader.list_s3_files(
        satellite=satellite, region=region, start_time=start_time, end_time=end_time
    )
    assert len(actual) == 960

    (actual_region, _, actual_satellite, actual_started_at,) = utilities.parse_filename(
        filename=actual[0]
    )
    assert actual_region == region
    assert actual_satellite == utilities.SATELLITE_SHORT_HAND[satellite]
    assert actual_started_at >= start_time
    assert actual_started_at <= end_time


def test_list_s3_files_single_scan():
    region = "M1"
    satellite = "noaa-goes17"
    start_time = datetime.datetime(2019, 1, 1, 1)

    actual = downloader.list_s3_files(  # no end_time
        satellite=satellite, region=region, start_time=start_time
    )
    assert len(actual) == 16

    (actual_region, _, actual_satellite, actual_scan_time) = utilities.parse_filename(
        filename=actual[0]
    )
    for filepath in actual:
        (parsed_region, _, parsed_satellite, parsed_scan_time) = utilities.parse_filename(
            filename=filepath
        )
        assert actual_region == parsed_region
        assert actual_satellite == parsed_satellite
        assert actual_scan_time == parsed_scan_time


def test_download_file(s3_filepath):
    with tempfile.TemporaryDirectory() as temporary_directory:
        actual = downloader.download_file(
            s3_filepath=s3_filepath, local_directory=temporary_directory,
        )
        assert os.path.exists(actual)


def test_download_files():
    with tempfile.TemporaryDirectory() as temporary_directory:
        actual = downloader.download_files(
            local_directory=temporary_directory,
            satellite="noaa-goes17",
            region="M1",
            start_time=datetime.datetime(2019, 1, 1, 1, 0),
            end_time=datetime.datetime(2019, 1, 1, 1, 1),
        )
        assert len(actual) == 16
        for actual_local_filepath in actual:
            assert os.path.exists(actual_local_filepath)
