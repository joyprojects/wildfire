import glob
import os

import numpy as np

from wildfire.data import goes_level_1
from wildfire.models import threshold_model
from wildfire.models.threshold_model import goes_level_1_wildfires


def test_find_wildfires(
    goes_level_1_filepaths_wildfire, goes_level_1_filepaths_no_wildfire
):
    actual = goes_level_1_wildfires.find_wildfires(
        filepaths=goes_level_1_filepaths_wildfire
    )
    assert isinstance(actual, list)
    assert len(actual) == 1

    actual = goes_level_1_wildfires.find_wildfires(
        filepaths=goes_level_1_filepaths_no_wildfire
    )
    assert isinstance(actual, list)
    assert len(actual) == 0


def test_parse_scan_for_wildfire(
    goes_level_1_filepaths_wildfire, goes_level_1_filepaths_no_wildfire
):
    actual = goes_level_1_wildfires.parse_scan_for_wildfire(
        filepaths=goes_level_1_filepaths_wildfire
    )
    assert isinstance(actual, dict)

    actual = goes_level_1_wildfires.parse_scan_for_wildfire(
        filepaths=goes_level_1_filepaths_no_wildfire
    )
    assert actual is None


def test_parse_scan_for_wildfire_bad_scan(goes_level_1_filepaths_wildfire):
    actual = goes_level_1_wildfires.parse_scan_for_wildfire(
        filepaths=goes_level_1_filepaths_wildfire[:5]
    )
    assert actual is None


def test_get_model_features(goes_level_1_filepaths_wildfire):
    goes_scan = goes_level_1.read_netcdfs(goes_level_1_filepaths_wildfire)
    actual = goes_level_1_wildfires.get_model_features(goes_scan=goes_scan)
    assert isinstance(actual, threshold_model.model.ModelFeatures)

    for actual_feature in actual:
        assert isinstance(actual_feature, np.ndarray)
        assert actual_feature.shape == (1500, 2500)


def test_predict_wildfires(goes_level_1_filepaths_wildfire):
    goes_scan = goes_level_1.read_netcdfs(goes_level_1_filepaths_wildfire)
    actual = goes_level_1_wildfires.predict_wildfires(goes_scan=goes_scan)
    assert isinstance(actual, np.ndarray)
    assert actual.shape == (1500, 2500)
    assert actual.mean() > 0
