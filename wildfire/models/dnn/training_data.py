"""Create and load data to be used by the CNNs."""
import datetime
import glob
import logging
import os

import numpy as np
import xarray as xr

from wildfire import multiprocessing
from wildfire.data import goes_level_2

_logger = logging.getLogger(__name__)


def get_patch_indices(max_index, length, stride):
    """Compute path indices.

    Return indices such that each every the last range would have the full `length`
    (i.e. always returns `max_index - length` as the last element).

    Examples
    --------
    get_patch_indices(10, 2, 2) = [0, 2, 4, 6, 8]
    get_patch_indices(9, 2, 3) = [0, 3, 6, 7]
    get_patch_indices(7, 3, 3) = [0, 3, 4]

    Parameters
    ----------
    max_index :int
    length: int
    stride : int

    Returns
    -------
    list
    """
    if max_index < length:
        raise ValueError("Max index must be larger than stride")
    last_patch = max_index - length
    indices = np.arange(0, last_patch, stride)
    return np.append(indices, [last_patch])


def extract_patches_2d(arr, height, width, stride):
    """Extract 2d patches from array.

    if stride = width, then shape of the returned object will be:
        arr_height, arr_width, _ = arr.shape
        ceil(arr_heigh / height) * ceil(arr_width / width)

    Parameters
    ----------
    arr : array-like
    height : int
    width : int
    stride : int

    Returns
    -------
    array-like
    """
    max_height, max_width = arr.shape[:2]

    height_indices = get_patch_indices(max_index=max_height, length=height, stride=stride)
    width_indices = get_patch_indices(max_index=max_width, length=width, stride=stride)

    patches = []
    for height_idx in height_indices:
        for width_idx in width_indices:
            patches.append(
                arr[height_idx : height_idx + height, width_idx : width_idx + width]
            )
    return np.array(patches)


def process_file(
    level_2_filepath, level_1_directory, height, width, stride, persist_directory
):
    """Create training data from a GOES level 2 fire dataset.

    For a given GOES L2 fire product, find the accompanying GOES L1 data, and return the
    pixels with fire in it.

    Parameters
    ----------
    level_2_filepath : str
    level_1_directory : str
    height : int
    width : int
    stride : int

    Returns
    -------
    array-like
        shape: (num_fire_patches, height, width, 17)
    """
    _logger.info("Processing %s...", level_2_filepath)

    level_2 = xr.load_dataset(level_2_filepath)
    level_1 = goes_level_2.utilities.match_level_1(
        level_2=level_2, level_1_directory=level_1_directory
    )

    two_km_coords = {
        "x": level_1["band_16"].dataset.x.values,
        "y": level_1["band_16"].dataset.y.values,
    }

    level_1 = xr.concat(
        objs=[
            band.rescale_to_2km().normalize().assign_coords(**two_km_coords)
            for _, band in level_1.iteritems()
        ],
        dim="band",
    )

    # shape = (x, y, 17)
    data = np.concatenate(
        [level_1.values, np.expand_dims(level_2.Temp.values, axis=0)]
    ).transpose([1, 2, 0])

    # shape = (num_patches, height, width, 17)
    data = extract_patches_2d(arr=data, height=height, width=width, stride=stride)
    fire_indices = np.any(np.isfinite(data[:, :, :, -1]), axis=(1, 2))

    # shape = (num_fire_pathces, height, width, 17)
    data = data[fire_indices]

    now = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    basename = os.path.basename(level_2_filepath)
    persist_filepath = os.path.join(persist_directory, f"cnn_training_c{now}_{basename}")

    data = xr.Dataset(
        {
            "abi": xr.DataArray(data[:, :, :, :-1].astype(np.float32)),
            "fire_temp": xr.DataArray(data[:, :, :, -1].astype(np.float32)),
        }
    )
    data.to_netcdf(persist_filepath)
    _logger.info("Saved training data to file: %s", persist_filepath)
    return data


def create_goes_level_2_training_data(
    level_2_directory,
    level_1_directory,
    persist_directory,
    height,
    width,
    stride,
    pbs=False,
    **cluster_kwargs,
):
    """Create GOES L2 training data for the CNN to predict wildfire presence.

    Parameters
    ----------
    level_2_directory : str
    level_1_directory : str
    persist_directory : str
    height : int
    width : int
    stride : int
    """
    goes_l2_filepaths = glob.glob(
        os.path.join(level_2_directory, "**", "*.nc"), recursive=True
    )

    num_filepaths = len(goes_l2_filepaths)
    _logger.info(
        "Creating training data from %d file for the DNN using %d processes...",
        num_filepaths,
        os.cpu_count(),
    )
    multiprocessing.map_function(
        function=process_file,
        function_args=[
            goes_l2_filepaths,
            [level_1_directory] * num_filepaths,
            [height] * num_filepaths,
            [width] * num_filepaths,
            [stride] * num_filepaths,
            [persist_directory] * num_filepaths,
        ],
        pbs=pbs,
        **cluster_kwargs,
    )
    _logger.info("Saved training data to directory: %s", persist_directory)
