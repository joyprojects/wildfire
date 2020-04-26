import numpy as np
import pytest

from wildfire.data import goes_level_1
from wildfire.models.threshold_model import model, goes_level_1_wildfires


def test_predict_wildfire(goes_level_1_filepaths_wildfire):
    wildfire_scan = goes_level_1.read_netcdfs(goes_level_1_filepaths_wildfire)
    model_features = goes_level_1_wildfires.get_model_features(goes_scan=wildfire_scan)
    actual_wildfire = model.predict(
        is_hot=model_features.is_hot,
        is_cloud=model_features.is_cloud,
        is_night=model_features.is_night,
        is_water=model_features.is_water,
    )
    assert actual_wildfire.mean() > 0


def test_predict_no_wildfire(goes_level_1_filepaths_no_wildfire):
    no_wildfire_scan = goes_level_1.read_netcdfs(goes_level_1_filepaths_no_wildfire)
    model_features = goes_level_1_wildfires.get_model_features(goes_scan=no_wildfire_scan)
    no_actual_wildfire = model.predict(
        is_hot=model_features.is_hot,
        is_cloud=model_features.is_cloud,
        is_night=model_features.is_night,
        is_water=model_features.is_water,
    )
    assert no_actual_wildfire.mean() == 0.0


def test_predict_bad_args():
    with pytest.raises(ValueError) as error_message:
        model.predict(
            is_hot=np.ones(1),
            is_water=np.ones(2),
            is_night=np.ones(1),
            is_cloud=np.ones(1),
        )
        assert "Shapes do not match" in error_message
