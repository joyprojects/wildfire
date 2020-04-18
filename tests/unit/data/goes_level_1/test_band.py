import datetime
import os
import tempfile

import numpy as np
import scipy.stats as st
import xarray as xr

from wildfire.data import goes_level_1


def test_goes_band(reflective_band):
    actual = goes_level_1.GoesBand(dataset=reflective_band)
    assert actual.region == "M1"
    assert actual.satellite == "G17"
    np.testing.assert_almost_equal(actual.band_wavelength_micrometers, 0.47, decimal=0)
    assert actual.scan_time_utc == datetime.datetime(2019, 10, 27, 20, 0, 27, 500000)
    assert actual.band_id == 1
    assert actual.parse().equals(actual.reflectance_factor)
    assert np.isnan(actual.reflectance_factor.data).sum() == 0
    assert (
        np.isnan(actual.brightness_temperature.data).sum() == actual.dataset.Rad.data.size
    )
    np.testing.assert_array_equal(
        actual.normalize(), st.zscore(actual.reflectance_factor, axis=None)
    )
    np.testing.assert_array_equal(
        actual.normalize(use_radiance=True), st.zscore(actual.dataset.Rad, axis=None),
    )
    with tempfile.TemporaryDirectory() as temp_directory:
        filepath = actual.to_netcdf(directory=temp_directory)
        assert os.path.exists(filepath)
        assert isinstance(xr.open_dataset(filepath), xr.core.dataset.Dataset)


def test_reflective_band(reflective_band):
    actual = goes_level_1.GoesBand(dataset=reflective_band)
    assert actual.parse().equals(actual.reflectance_factor)
    assert np.isnan(actual.reflectance_factor.data).sum() == 0
    np.testing.assert_array_equal(
        actual.normalize(), st.zscore(actual.reflectance_factor, axis=None)
    )


def test_emissive_band(emissive_band):
    actual = goes_level_1.GoesBand(dataset=emissive_band)
    assert actual.parse().equals(actual.brightness_temperature)
    assert np.isnan(actual.brightness_temperature.data).sum() == 0
    np.testing.assert_array_equal(
        actual.normalize(), st.zscore(actual.brightness_temperature, axis=None)
    )


def test_filter_bad_pixels(emissive_band):
    actual = goes_level_1.GoesBand(dataset=emissive_band).filter_bad_pixels()
    assert isinstance(actual, goes_level_1.GoesBand)
    assert (np.isnan(emissive_band.Rad.data).sum() == 0) & (
        np.isnan(actual.dataset.Rad).data.sum() > 0
    )


def test_rescale_to_2km(reflective_band, emissive_band):
    actual = goes_level_1.GoesBand(dataset=reflective_band).rescale_to_2km()
    assert isinstance(actual, goes_level_1.GoesBand)
    assert actual.dataset.Rad.shape == (500, 500)

    actual = goes_level_1.GoesBand(dataset=emissive_band).rescale_to_2km()
    assert isinstance(actual, goes_level_1.GoesBand)
    assert actual.dataset.Rad.shape == (500, 500)


def test_read_netcdf(wildfire_scan_filepaths):
    actual = goes_level_1.read_netcdf(local_filepath=wildfire_scan_filepaths[0],)
    assert isinstance(actual, goes_level_1.GoesBand)


def test_normalize():
    x = np.array([1, 2, 3, 4, 5])
    actual = goes_level_1.band.normalize(data=x)
    expected = st.zscore(x)
    np.testing.assert_array_equal(actual, expected)


def test_get_goes_band_local(wildfire_scan_filepaths):
    local_filepath = wildfire_scan_filepaths[0]
    region, channel, satellite, scan_time = goes_level_1.utilities.parse_filename(
        local_filepath
    )

    actual = goes_level_1.get_goes_band(
        satellite="noaa-goes17",
        region=region,
        channel=channel,
        scan_time_utc=scan_time,
        local_directory=os.path.join("tests", "resources", "test_scan_wildfire"),
        s3=False,
    )
    assert isinstance(actual, goes_level_1.GoesBand)
    assert actual.band_id == channel
    assert actual.region == region
    assert actual.satellite == satellite
    assert actual.scan_time_utc == scan_time
