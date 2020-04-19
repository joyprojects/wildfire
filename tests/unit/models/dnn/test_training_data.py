import numpy as np

from wildfire.models.dnn import training_data


def test_get_patch_indices():
    actual = training_data.get_patch_indices(max_index=10, length=2, stride=2)
    np.testing.assert_array_equal(actual, [0, 2, 4, 6, 8])

    actual = training_data.get_patch_indices(max_index=9, length=2, stride=3)
    np.testing.assert_array_equal(actual, [0, 3, 6, 7])

    actual = training_data.get_patch_indices(max_index=7, length=3, stride=3)
    np.testing.assert_array_equal(actual, [0, 3, 4])


def test_extract_patches_2d():
    data = np.ones(shape=(500, 500, 17))  # Mesoscale
    actual = training_data.extract_patches_2d(arr=data, height=32, width=32, stride=32)
    assert actual.shape == (256, 32, 32, 17)

    data = np.ones(shape=(1500, 2500, 17)) # CONUS
    actual = training_data.extract_patches_2d(arr=data, height=32, width=32, stride=32)
    assert actual.shape == (3713, 32, 32, 17)

    data = np.ones(shape=(5424, 5424, 17)) # Full
    actual = training_data.extract_patches_2d(arr=data, height=32, width=32, stride=32)
    assert actual.shape == (28900, 32, 32, 17)
