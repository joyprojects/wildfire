import glob
import os

import numpy as np

from wildfire import wildfire
from wildfire.data import goes_level_1
from wildfire.models import threshold_model


def test_find_wildfires_goes(wildfire_scan_filepaths, no_wildfire_scan_filepaths):
    actual = wildfire.find_wildfires_goes(filepaths=wildfire_scan_filepaths)
    assert isinstance(actual, list)
    assert len(actual) == 1

    actual = wildfire.find_wildfires_goes(filepaths=no_wildfire_scan_filepaths)
    assert isinstance(actual, list)
    assert len(actual) == 0


def test_parse_scan_for_wildfire(wildfire_scan_filepaths, no_wildfire_scan_filepaths):
    actual = wildfire.parse_scan_for_wildfire(filepaths=wildfire_scan_filepaths)
    assert isinstance(actual, dict)

    actual = wildfire.parse_scan_for_wildfire(filepaths=no_wildfire_scan_filepaths)
    assert actual is None


def test_parse_scan_for_wildfire_bad_scan(wildfire_scan_filepaths):
    actual = wildfire.parse_scan_for_wildfire(filepaths=wildfire_scan_filepaths[:5])
    assert actual is None


def test_get_model_features_goes(all_bands_wildfire):
    goes_scan = goes_level_1.GoesScan(bands=all_bands_wildfire)
    actual = wildfire.get_model_features_goes(goes_scan=goes_scan)
    assert isinstance(actual, threshold_model.model.ModelFeatures)

    for actual_feature in actual:
        assert isinstance(actual_feature, np.ndarray)
        assert actual_feature.shape == (500, 500)


def test_predict_wildfires_goes(all_bands_wildfire):
    goes_scan = goes_level_1.GoesScan(bands=all_bands_wildfire)
    actual = wildfire.predict_wildfires_goes(goes_scan=goes_scan)
    assert isinstance(actual, np.ndarray)
    assert actual.shape == (500, 500)
    assert actual.mean() > 0
