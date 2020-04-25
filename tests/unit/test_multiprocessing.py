import datetime
import os
import time

import dask
import numpy as np

from wildfire import multiprocessing


def test_flatten_array():
    actual = multiprocessing.flatten_array([[1], [2], [3], [4]])
    np.testing.assert_array_equal(actual, np.array([1, 2, 3, 4]))


def test_start_dask_client():
    actual = multiprocessing.start_dask_client()
    assert isinstance(actual, dask.distributed.client.Client)
    actual.close()


def test_map_function():
    num_cpus = os.cpu_count()

    def timer(x):
        time.sleep(1)
        return x + 1

    started_at = datetime.datetime.utcnow()
    multiprocessing.map_function(timer, range(num_cpus * 2))
    finished_at = datetime.datetime.utcnow()

    np.testing.assert_almost_equal(
        (finished_at - started_at).total_seconds(), 2, decimal=0
    )
