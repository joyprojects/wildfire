import numpy as np
import pytest

from wildfire import wildfire
from wildfire.data import goes_level_1
from wildfire.models import threshold_model


def test_predict_wildfire(all_bands_wildfire):
    wildfire_scan = goes_level_1.GoesScan(bands=all_bands_wildfire)
    model_features = wildfire.get_model_features_goes(goes_scan=wildfire_scan)
    actual_wildfire = threshold_model.predict(
        is_hot=model_features.is_hot,
        is_cloud=model_features.is_cloud,
        is_night=model_features.is_night,
        is_water=model_features.is_water,
    )
    assert actual_wildfire.mean() > 0


def test_predict_no_wildfire(all_bands_no_wildfire):
    no_wildfire_scan = goes_level_1.GoesScan(bands=all_bands_no_wildfire)
    model_features = wildfire.get_model_features_goes(goes_scan=no_wildfire_scan)
    no_actual_wildfire = threshold_model.predict(
        is_hot=model_features.is_hot,
        is_cloud=model_features.is_cloud,
        is_night=model_features.is_night,
        is_water=model_features.is_water,
    )
    assert no_actual_wildfire.mean() == 0.0


def test_predict_bad_args():
    with pytest.raises(ValueError) as error_message:
        threshold_model.predict(
            is_hot=np.ones(1),
            is_water=np.ones(2),
            is_night=np.ones(1),
            is_cloud=np.ones(1),
        )
        assert "Shapes do not match" in error_message
