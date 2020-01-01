import datetime
import os

import numpy as np
import xarray as xr

from wildfire.goes import band


def test_goes_band_init(single_band):
    actual = band.GoesBand(dataset=single_band)
    assert actual.dataset.equals(single_band)
    assert actual.region == "M1"
    assert actual.satellite == "noaa-goes17"
    assert actual.scan_time_utc == datetime.datetime(2019, 10, 27, 20, 0, 27, 500000)
    assert actual.band == 1
    np.testing.assert_almost_equal(actual.band_wavelength_micrometers, 0.47)
