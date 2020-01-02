import datetime
import os
import tempfile

import numpy as np
import scipy.stats as st
import xarray as xr

from wildfire.goes import band


def test_goes_band(reflective_band):
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
    with tempfile.TemporaryDirectory() as temp_directory:
        filepath = actual.to_netcdf(directory=temp_directory)
        assert os.path.exists(filepath)
        assert isinstance(xr.open_dataset(filepath), xr.core.dataset.Dataset)


def test_reflective_band(reflective_band):
    actual = band.GoesBand(dataset=reflective_band)
    assert actual.parse().equals(actual.reflectance_factor)
    assert np.isnan(actual.reflectance_factor.data).sum() == 0
    np.testing.assert_array_equal(
        actual.normalize(), st.zscore(actual.reflectance_factor, axis=None)
    )


def test_emissive_band(emissive_band):
    actual = band.GoesBand(dataset=emissive_band)
    assert actual.parse().equals(actual.brightness_temperature)
    assert np.isnan(actual.brightness_temperature.data).sum() == 0
    np.testing.assert_array_equal(
        actual.normalize(), st.zscore(actual.brightness_temperature, axis=None)
    )


def test_filter_bad_pixels(emissive_band):
    actual = band.GoesBand(dataset=emissive_band).filter_bad_pixels()
    assert isinstance(actual, band.GoesBand)
    assert (np.isnan(emissive_band.Rad.data).sum() == 0) & (
        np.isnan(actual.dataset.Rad).data.sum() > 0
    )


def test_from_netcdf_local():
    actual = band.from_netcdf(
        filepath=os.path.join(
            "tests",
            "resources",
            "test_scan",
            "OR_ABI-L1b-RadM1-M6C07_G17_s20193002000275_e20193002000344_c20193002000390.nc",
        )
    )
    assert isinstance(actual, band.GoesBand)
