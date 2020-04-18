import datetime
import glob
import os
import tempfile

import pytest

from wildfire.data import goes_level_1


def test_scan(all_bands_wildfire):
    actual = goes_level_1.GoesScan(bands=all_bands_wildfire)
    assert actual.region == "M1"
    assert actual.satellite == "G17"
    assert actual.scan_time_utc == datetime.datetime(2019, 10, 27, 20, 0, 27, 500000)
    assert list(actual.keys) == [f"band_{idx}" for idx in range(1, 17)]
    assert actual["band_1"].dataset.equals(actual.bands["band_1"].dataset)
    for _, actual_band in actual.iteritems():
        assert isinstance(actual_band, goes_level_1.GoesBand)
    with tempfile.TemporaryDirectory() as temp_directory:
        filepaths = actual.to_netcdf(directory=temp_directory)
        for filepath in filepaths:
            assert os.path.exists(filepath)


def test_scan_init_bad_args(all_bands_wildfire):
    too_many_bands = all_bands_wildfire + [all_bands_wildfire[0]]
    with pytest.raises(ValueError) as error_message:
        goes_level_1.GoesScan(bands=too_many_bands)
        assert "Too many bands" in error_message

    too_few_bands = all_bands_wildfire[:15]
    with pytest.raises(ValueError) as error_message:
        goes_level_1.GoesScan(bands=too_few_bands)
        assert "Missing bands" in error_message

    all_bands_wildfire[15].dataset.attrs[
        "dataset_name"
    ] = "OR_ABI-L1b-RadM1-M6C01_G16_s20193002000275_e20193002000332_c20193002000379.nc"
    with pytest.raises(ValueError) as error_message:
        goes_level_1.GoesScan(bands=all_bands_wildfire)
        assert "must have same" in error_message


def test_rescale_to_2km(all_bands_wildfire):
    original = goes_level_1.GoesScan(bands=all_bands_wildfire)
    actual = original.rescale_to_2km()
    assert isinstance(actual, goes_level_1.GoesScan)
    assert actual.satellite == original.satellite
    assert actual.region == original.region
    assert actual.scan_time_utc == original.scan_time_utc
    for _, band_data in actual.iteritems():
        assert band_data.dataset.Rad.shape == (500, 500)


def test_read_netcdfs(wildfire_scan_filepaths):
    actual = goes_level_1.read_netcdfs(local_filepaths=wildfire_scan_filepaths)
    assert isinstance(actual, goes_level_1.GoesScan)


def test_get_goes_scan_local(wildfire_scan_filepaths):
    local_filepath = wildfire_scan_filepaths
    region, _, satellite, scan_time = goes_level_1.utilities.parse_filename(
        local_filepath[0]
    )

    actual = goes_level_1.get_goes_scan(
        satellite="noaa-goes17",
        region=region,
        scan_time_utc=scan_time,
        local_directory=os.path.join("tests", "resources", "test_scan_wildfire"),
        s3=False,
    )
    assert isinstance(actual, goes_level_1.GoesScan)
    assert actual.region == region
    assert actual.satellite == satellite
    assert actual.scan_time_utc == scan_time
