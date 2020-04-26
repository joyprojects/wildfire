import glob
import os
import tempfile

import numpy as np
import xarray as xr

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

    data = np.ones(shape=(1500, 2500, 17))  # CONUS
    actual = training_data.extract_patches_2d(arr=data, height=32, width=32, stride=32)
    assert actual.shape == (3713, 32, 32, 17)

    data = np.ones(shape=(5424, 5424, 17))  # Full
    actual = training_data.extract_patches_2d(arr=data, height=32, width=32, stride=32)
    assert actual.shape == (28900, 32, 32, 17)


def test_process_file(goes_level_2):
    with tempfile.TemporaryDirectory() as temporary_directory:
        actual = training_data.process_file(
            level_2_filepath=goes_level_2["level_2"],
            level_1_directory=goes_level_2["level_1_directory"],
            height=32,
            width=32,
            stride=32,
            persist_directory=temporary_directory,
        )

        assert isinstance(actual, xr.core.dataset.Dataset)
        np.testing.assert_array_equal(list(actual.keys()), ["abi", "fire_temp"])
        assert actual.abi.shape == (5, 32, 32, 16)  # num fire patches, height, width, 17
        assert actual.fire_temp.shape == (5, 32, 32)  # num fire patches, height, width
        assert (
            len(
                glob.glob(os.path.join(temporary_directory, "**", "*.nc"), recursive=True)
            )
            == 1
        )


def test_create_goes_level_2_training_data(goes_level_2):
    level_2_directory = os.path.dirname(goes_level_2["level_2"])

    with tempfile.TemporaryDirectory() as temporary_directory:
        training_data.create_goes_level_2_training_data(
            level_2_directory=level_2_directory,
            level_1_directory=goes_level_2["level_1_directory"],
            height=32,
            width=32,
            stride=32,
            persist_directory=temporary_directory,
        )

        assert len(
            glob.glob(os.path.join(temporary_directory, "**", "*.nc"), recursive=True)
        ) == len(glob.glob(os.path.join(level_2_directory, "**", "*.nc"), recursive=True))
