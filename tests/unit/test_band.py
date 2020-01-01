import datetime

import numpy as np
import scipy.stats as st

from wildfire.goes import band


def test_reflective_band(reflective_band):
    actual = band.GoesBand(dataset=reflective_band)
    assert actual.region == "M1"
    assert actual.satellite == "noaa-goes17"
    assert actual.scan_time_utc == datetime.datetime(2019, 10, 27, 20, 0, 27, 500000)
    assert actual.band == 1
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


def test_emissive_band(emissive_band):
    actual = band.GoesBand(dataset=emissive_band)
    assert actual.region == "M1"
    assert actual.satellite == "noaa-goes17"
    assert actual.scan_time_utc == datetime.datetime(2019, 10, 27, 20, 0, 27, 500000)
    assert actual.band == 11
    assert actual.parse().equals(actual.brightness_temperature)
    assert np.isnan(actual.reflectance_factor.data).sum() == actual.dataset.Rad.data.size
    assert np.isnan(actual.brightness_temperature.data).sum() == 0
    np.testing.assert_array_equal(
        actual.normalize(), st.zscore(actual.brightness_temperature, axis=None)
    )
