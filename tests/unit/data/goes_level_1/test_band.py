import datetime
import os
import tempfile

import numpy as np
import scipy.stats as st
import xarray as xr

from wildfire.data import goes_level_1


def test_goes_band(goes_level_1_mesoscale):
    actual = goes_level_1.GoesBand(dataset=goes_level_1_mesoscale)
    assert actual.region == "M1"
    assert actual.satellite == "G16"
    np.testing.assert_almost_equal(actual.band_wavelength_micrometers, 0.47, decimal=2)
    assert actual.scan_time_utc == datetime.datetime(2020, 1, 1, 0, 1, 26, 200000)
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


def test_reflective_band(goes_level_1_mesoscale):
    actual = goes_level_1.GoesBand(dataset=goes_level_1_mesoscale)
    assert actual.parse().equals(actual.reflectance_factor)
    assert np.isnan(actual.reflectance_factor.data).sum() == 0
    np.testing.assert_array_equal(
        actual.normalize(), st.zscore(actual.reflectance_factor, axis=None)
    )


def test_emissive_band(goes_level_1_channel_7):
    actual = goes_level_1.GoesBand(dataset=goes_level_1_channel_7)
    assert actual.parse().equals(actual.brightness_temperature)
    assert np.isnan(actual.brightness_temperature.data).sum() == 0
    np.testing.assert_array_equal(
        actual.normalize(), st.zscore(actual.brightness_temperature, axis=None)
    )


def test_filter_bad_pixels(goes_level_1_mesoscale):
    goes_band = goes_level_1.GoesBand(dataset=goes_level_1_mesoscale)
    actual = goes_band.filter_bad_pixels()

    assert isinstance(actual, goes_level_1.GoesBand)
    assert actual.scan_time_utc == goes_band.scan_time_utc
    assert actual.band_id == goes_band.band_id
    assert np.isnan(actual.reflectance_factor).sum() == 0


def test_rescale_to_2km(goes_level_1_mesoscale, goes_level_1_conus, goes_level_1_full):
    actual = goes_level_1.GoesBand(dataset=goes_level_1_mesoscale).rescale_to_2km()
    assert isinstance(actual, goes_level_1.GoesBand)
    assert actual.dataset.Rad.shape == (500, 500)
    assert actual.rescale_to_2km().dataset.Rad.shape == (500, 500)

    actual = goes_level_1.GoesBand(dataset=goes_level_1_conus).rescale_to_2km()
    assert actual.dataset.Rad.shape == (1500, 2500)
    assert actual.rescale_to_2km().dataset.Rad.shape == (1500, 2500)

    actual = goes_level_1.GoesBand(dataset=goes_level_1_full).rescale_to_2km()
    assert actual.dataset.Rad.shape == (5424, 5424)
    assert actual.rescale_to_2km().dataset.Rad.shape == (5424, 5424)


def test_read_netcdf(goes_level_1_filepaths_no_wildfire):
    actual = goes_level_1.read_netcdf(
        local_filepath=goes_level_1_filepaths_no_wildfire[0],
    )
    assert isinstance(actual, goes_level_1.GoesBand)


def test_normalize():
    x = np.array([1, 2, 3, 4, 5])
    actual = goes_level_1.band.normalize(data=x)
    expected = st.zscore(x)
    np.testing.assert_array_equal(actual, expected)


def test_get_goes_band_local(goes_level_1_filepaths_no_wildfire):
    local_filepath = goes_level_1_filepaths_no_wildfire[0]
    region, channel, satellite, scan_time = goes_level_1.utilities.parse_filename(
        local_filepath
    )

    actual = goes_level_1.get_goes_band(
        satellite=goes_level_1.utilities.SATELLITE_LONG_HAND[satellite],
        region=region,
        channel=channel,
        scan_time_utc=scan_time,
        local_directory=os.path.join(
            "tests", "resources", "goes_level_1_scan_no_wildfire"
        ),
        s3=False,
    )
    assert isinstance(actual, goes_level_1.GoesBand)
    assert actual.band_id == channel
    assert actual.region == region
    assert actual.satellite == satellite
    assert actual.scan_time_utc == scan_time
