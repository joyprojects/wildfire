"""Threshold model for predicting wildfires."""
from collections import namedtuple

import numpy as np

from wildfire.data import goes_level_1

ModelFeatures = namedtuple(
    "ModelFeatures", ("is_hot", "is_cloud", "is_water", "is_night")
)


def predict(is_hot, is_cloud, is_water, is_night):
    """Predict the occurrence of a wildfire in an 2D image.

    The features correspond to a boolean value at each pixel in the image.

    Parameters
    ----------
    is_hot : np.ndarray of bool
        2 dimensional array representing whether a pixel is "hot". Corresponds to the
        output of `is_hot_pixel()`.
    is_cloud : np.ndarray of bool
        2 dimensional array representing whether a pixel is in a "cloud". Corresponds to
        the output of `is_cloud_pixel()`.
    is_water : np.ndarray of bool
        2 dimensional array representing whether a pixel is in "water". Corresponds to the
        output of `is_water_pixel()`.
    is_night : np.ndarray of bool
        2 dimensional array representing whether a pixel is in an image taken at "night".
        Corresponds to the output of `is_night_pixel()`.

    Raises
    ------
    ValueError
        Shapes of input must match.

    Returns
    -------
    np.ndarray of bool
        2 dimensional array representing whether each pixel in the array is in a wildfire.
    """
    _assert_shapes_match(is_hot, is_cloud, is_water, is_night)
    return is_hot & (is_night | (~is_cloud & ~is_water))


def is_hot_pixel(brightness_temperature_3_89, brightness_temperature_11_19):
    """Classiify the pixels of an image as whether they are "hot".

    Parameters
    ----------
    brightness_temperature_3_89 : ndarray of float
        The brightness temperature (Kelvin) of each pixel of an image scanned over the
        3.89 micrometer wavelength. In the GOES data this corresponds to band 7.
    brightness_temperature_11_19 : ndarray of float
        The brightness temperature (Kelvin) of each pixel of an image scanned over the
        11.19 micrometer wavelength. In the GOES data this corresponds to band 14.

    Returns
    -------
    np.ndarray of bool
    """
    condition_1 = goes_level_1.band.normalize(data=brightness_temperature_3_89) > 2
    condition_2 = (
        goes_level_1.band.normalize(
            data=brightness_temperature_3_89 - brightness_temperature_11_19
        )
        > 3
    )
    return condition_1 & condition_2


def is_cloud_pixel(
    reflectance_factor_0_64, reflectance_factor_0_87, brightness_temperature_12_27
):
    """Classiify the pixels of an image as whether they are in a cloud.

    Parameters
    ----------
    reflectance_factor_0_64 : ndarray of float
        The reflectance factor of each pixel of an image scanned over the 0.64 micrometer
        wavelength. In the GOES data this corresponds to band 2.
    reflectance_factor_0_87 : ndarray of float
        The reflectance factor of each pixel of an image scanned over the 0.87 micrometer
        wavelength. In the GOES data this corresponds to band 3.
    brightness_temperature_12_27 : ndarray of float
        The brightness temperature (Kelvin) of each pixel of an image scanned over the
        12.27 micrometer wavelength. In the GOES data this corresponds to band 15.

    Returns
    -------
    np.ndarray of bool
    """
    condition_1 = (reflectance_factor_0_64 + reflectance_factor_0_87) >= 1.2
    condition_2 = brightness_temperature_12_27 <= 265
    condition_3 = ((reflectance_factor_0_64 + reflectance_factor_0_87) >= 0.5) & (
        brightness_temperature_12_27 <= 285
    )
    return condition_1 | condition_2 | condition_3


def is_water_pixel(reflectance_factor_2_25):
    """Classiify the pixels of an image as whether they are in water.

    Parameters
    ----------
    reflectance_factor_2_25 : ndarray of float
        The reflectance factor of each pixel of an image scanned over the 2.25 micrometer
        wavelength. In the GOES data this corresponds to band 6.

    Returns
    -------
    np.ndarray of bool
    """
    return reflectance_factor_2_25 <= 0.03


def is_night_pixel(reflectance_factor_0_64, reflectance_factor_0_87):
    """Classiify the pixels of an image as whether they are in an image taken at night.

    Parameters
    ----------
    reflectance_factor_0_64 : ndarray of float
        The reflectance factor of each pixel of an image scanned over the 0.64 micrometer
        wavelength. In the GOES data this corresponds to band 2.
    reflectance_factor_0_87 : ndarray of float
        The reflectance factor of each pixel of an image scanned over the 0.87 micrometer
        wavelength. In the GOES data this corresponds to band 3.

    Returns
    -------
    np.ndarray of bool
    """
    condition_1 = np.abs(reflectance_factor_0_64) < 0.008
    condition_2 = np.abs(reflectance_factor_0_87) < 0.008
    return condition_1 | condition_2


def _assert_shapes_match(*args):
    shapes = {arg.shape for arg in args}
    if len(shapes) != 1:
        raise ValueError(f"Shapes do no match! Got shapes {shapes}")
