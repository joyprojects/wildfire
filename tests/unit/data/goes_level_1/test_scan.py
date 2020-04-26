import datetime
import glob
import os
import tempfile

import pytest

from wildfire.data import goes_level_1


def test_scan(goes_level_1_filepaths_no_wildfire):
    actual = goes_level_1.GoesScan(
        bands=[
            goes_level_1.read_netcdf(band_filepath)
            for band_filepath in goes_level_1_filepaths_no_wildfire
        ]
    )
    assert actual.region == "M1"
    assert actual.satellite == "G17"
    assert actual.scan_time_utc == datetime.datetime(2019, 12, 1, 10, 27, 27, 500000)
    assert list(actual.keys) == [f"band_{idx}" for idx in range(1, 17)]
    assert actual["band_1"].dataset.equals(actual.bands["band_1"].dataset)

    for _, actual_band in actual.iteritems():
        assert isinstance(actual_band, goes_level_1.GoesBand)

    with tempfile.TemporaryDirectory() as temp_directory:
        filepaths = actual.to_netcdf(directory=temp_directory)
        for filepath in filepaths:
            assert os.path.exists(filepath)


def test_scan_init_bad_args(goes_level_1_filepaths_no_wildfire):
    bands = [
        goes_level_1.read_netcdf(band_filepath)
        for band_filepath in goes_level_1_filepaths_no_wildfire
    ]
    too_many_bands = bands + [bands[0]]
    with pytest.raises(ValueError) as error_message:
        goes_level_1.GoesScan(bands=too_many_bands)
        assert "Too many bands" in error_message

    too_few_bands = bands[:15]
    with pytest.raises(ValueError) as error_message:
        goes_level_1.GoesScan(bands=too_few_bands)
        assert "Missing bands" in error_message


def test_read_netcdfs(goes_level_1_filepaths_no_wildfire):
    actual = goes_level_1.read_netcdfs(local_filepaths=goes_level_1_filepaths_no_wildfire)
    assert isinstance(actual, goes_level_1.GoesScan)


def test_rescale_to_2km(goes_level_1_filepaths_no_wildfire):
    original = goes_level_1.read_netcdfs(goes_level_1_filepaths_no_wildfire)
    actual = original.rescale_to_2km()
    assert isinstance(actual, goes_level_1.GoesScan)
    assert actual.satellite == original.satellite
    assert actual.region == original.region
    assert actual.scan_time_utc == original.scan_time_utc
    for _, band_data in actual.iteritems():
        assert band_data.dataset.Rad.shape == (500, 500)


def test_get_goes_scan_local(goes_level_1_filepaths_no_wildfire):
    region, _, satellite, scan_time = goes_level_1.utilities.parse_filename(
        goes_level_1_filepaths_no_wildfire[0]
    )

    actual = goes_level_1.get_goes_scan(
        satellite=goes_level_1.utilities.SATELLITE_LONG_HAND[satellite],
        region=region,
        scan_time_utc=scan_time,
        local_directory=os.path.join(
            "tests", "resources", "goes_level_1_scan_no_wildfire"
        ),
        s3=False,
    )
    assert isinstance(actual, goes_level_1.GoesScan)
    assert actual.region == region
    assert actual.satellite == satellite
    assert actual.scan_time_utc == scan_time
