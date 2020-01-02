import numpy as np
import pytest

from wildfire import goes
from wildfire.threshold_model import model


def test_predict_wildfire(all_bands_wildfire):
    wildfire_scan = goes.GoesScan(bands=all_bands_wildfire)
    model_features = model.get_features(goes_scan=wildfire_scan)
    actual_wildfire = model.predict(
        is_hot=model_features.is_hot,
        is_cloud=model_features.is_cloud,
        is_night=model_features.is_night,
        is_water=model_features.is_water,
    )
    assert actual_wildfire.mean() > 0


def test_predict_no_wildfire(all_bands_no_wildfire):
    no_wildfire_scan = goes.GoesScan(bands=all_bands_no_wildfire)
    model_features = model.get_features(goes_scan=no_wildfire_scan)
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
