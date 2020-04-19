import numpy as np

from wildfire import multiprocessing


def test_flatten_array():
    actual = multiprocessing.flatten_array([[1], [2], [3], [4]])
    np.testing.assert_array_equal(actual, np.array([1, 2, 3, 4]))
