"""Threshold model for predicting wildfires."""


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

    Returns
    -------
    np.ndarray of bool
        2 dimensional array representing whether each pixel in the array is in a wildfire.
    """
    raise NotImplementedError


def get_features(goes_scan):
    """Calculate the features of the threshold model from a GoesScan.

    Parameters
    ----------
    goes_scan : wildfire.goes.scan.GoesScan
        A scan of 16 bands of light over some region on Earth.

    Returns
    -------
    tuple of ndarray of bool
        The input to `predict()`.
        (is_hot, is_cloud, is_water, is_night)
    """
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError


def plot_wildfires(
    reflectance_factor_0_64,
    reflectance_factor_0_87,
    reflectance_factor_2_25,
    brightness_temperature_3_89,
    brightness_temperature_11_19,
    brightness_temperature_12_27,
):
    """Highlight pixels in a wildfire over the 11.19 micrometer scan.

    Parameters
    ----------
    reflectance_factor_0_64 : ndarray of float
        The reflectance factor of each pixel of an image scanned over the 0.64 micrometer
        wavelength. In the GOES data this corresponds to band 2.
    reflectance_factor_0_87 : ndarray of float
        The reflectance factor of each pixel of an image scanned over the 0.87 micrometer
        wavelength. In the GOES data this corresponds to band 3.
    reflectance_factor_2_25 : ndarray of float
        The reflectance factor of each pixel of an image scanned over the 2.25 micrometer
        wavelength. In the GOES data this corresponds to band 6.
    brightness_temperature_3_89 : ndarray of float
        The brightness temperature (Kelvin) of each pixel of an image scanned over the
        3.89 micrometer wavelength. In the GOES data this corresponds to band 7.
    brightness_temperature_11_19 : ndarray of float
        The brightness temperature (Kelvin) of each pixel of an image scanned over the
        11.19 micrometer wavelength. In the GOES data this corresponds to band 14.
    brightness_temperature_12_27 : ndarray of float
        The brightness temperature (Kelvin) of each pixel of an image scanned over the
        12.27 micrometer wavelength. In the GOES data this corresponds to band 15.

    Returns
    -------
    plt.axes._subplots.AxesSubplot
    """
    raise NotImplementedError
