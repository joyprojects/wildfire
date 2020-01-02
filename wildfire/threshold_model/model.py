"""Threshold model for predicting wildfires."""
from collections import namedtuple

import matplotlib.pyplot as plt
import numpy as np

from wildfire.goes import utilities

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
    condition_1 = utilities.normalize(data=brightness_temperature_3_89) > 2
    condition_2 = (
        utilities.normalize(
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


def plot_wildfires(goes_scan):
    """Highlight pixels in a wildfire and plot next to the 11.19 micrometer scan.

    Parameters
    ----------
    goes_scan : wildfire.goes.scan.GoesScan
        A scan of 16 bands of light over some region on Earth.

    Returns
    -------
    list of plt.image.AxesImage
    """
    model_features = get_features(goes_scan=goes_scan)
    model_predictions = predict(
        is_hot=model_features.is_hot,
        is_cloud=model_features.is_cloud,
        is_night=model_features.is_night,
        is_water=model_features.is_water,
    )
    is_wildfire_predicted = model_predictions.mean() > 0

    _, (axis_fire, axis_scan) = plt.subplots(ncols=2, figsize=(20, 8))
    axis_fire.set_title(f"Wildfire Present: {is_wildfire_predicted}", fontsize=20)

    image_fire = axis_fire.imshow(model_predictions)
    image_scan = goes_scan["band_7"].plot(axis=axis_scan)

    image_fire.axes.axis("off")
    image_scan.axes.axis("off")
    plt.tight_layout()
    return [image_fire, image_scan]


def get_features(goes_scan):
    """Calculate the features of the threshold model from a GoesScan.

    To do this, the provided GoesScan is first rescaled such that all bands are in the
    same spatial resoltuion (namely 500m).

    Parameters
    ----------
    goes_scan : wildfire.goes.scan.GoesScan
        A scan of 16 bands of light over some region on Earth.

    Returns
    -------
    ModelFeatures
        Namedtuple of features used as input to the `predict` method.
    """
    rescaled_scan = goes_scan.rescale_to_500m()

    is_hot = is_hot_pixel(
        brightness_temperature_3_89=rescaled_scan["band_7"].brightness_temperature.data,
        brightness_temperature_11_19=rescaled_scan["band_14"].brightness_temperature.data,
    )
    is_night = is_night_pixel(
        reflectance_factor_0_64=rescaled_scan["band_2"].reflectance_factor.data,
        reflectance_factor_0_87=rescaled_scan["band_3"].reflectance_factor.data,
    )
    is_water = is_water_pixel(
        reflectance_factor_2_25=rescaled_scan["band_6"].reflectance_factor.data
    )
    is_cloud = is_cloud_pixel(
        reflectance_factor_0_64=rescaled_scan["band_2"].reflectance_factor.data,
        reflectance_factor_0_87=rescaled_scan["band_3"].reflectance_factor.data,
        brightness_temperature_12_27=rescaled_scan["band_15"].brightness_temperature.data,
    )
    return ModelFeatures(
        is_hot=is_hot, is_night=is_night, is_water=is_water, is_cloud=is_cloud,
    )


def _assert_shapes_match(*args):
    shapes = {arg.shape for arg in args}
    if len(shapes) != 1:
        raise ValueError(f"Shapes do no match! Got shapes {shapes}")
