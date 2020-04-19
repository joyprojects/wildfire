"""Utilities for multiprocessing."""
import logging
import os

import numpy as np
import ray

_logger = logging.getLogger(__name__)


def map_function(function, function_args):
    """Map function arguments across function in parallel.

    Uses the number of cores available on the machine as the number of workers. Uses
    multiprocessing's `imap` in order to log a progress bar over its progress.

    https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool.imap

    User should read documentation on `multiprocessing.Pool` before using this method.
    https://docs.python.org/3.7/library/multiprocessing.html

    Parameters
    ----------
    function : function
        Function to pool across multiple threads.
    function_args : list of Any
        Arguments to iteratively pass to `function` across multiple threads. All elements
        must be pickleable. Only supports one iterable argument.

    Returns
    -------
    list of Any
        A list over the return values of `function` across the number of threads.
        Length is equal to `len(function_args)`.
    """
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True, webui_host="127.0.0.1")

    if len(np.array(function_args).shape) == 1:
        function_args = np.expand_dims(function_args, axis=1).tolist()

    _logger.info(
        "Using %s workers to run %s with args of shape %s...",
        os.cpu_count(),
        function.__name__,
        np.array(function_args).shape,
    )

    remote_function = ray.remote(function)
    futures = [remote_function.remote(*args) for args in function_args]
    return flatten_array(ray.get(futures))


def flatten_array(list_2d):
    """Flatten 2d array to 1 dimension."""
    shape = np.array(list_2d).shape
    if len(shape) == 1:
        return list_2d
    if len(shape) == 2:
        return [item for list_1d in list_2d for item in list_1d]
    return list_2d
