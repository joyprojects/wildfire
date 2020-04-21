"""Utilities for multiprocessing."""
import logging
import os

import numpy as np
import ray

_logger = logging.getLogger(__name__)


def map_function(function, function_args, flatten=True):
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
    flatten : bool
        Optional, defaults to True. Whether or not to flatten the output by a single
        dimension before returning.

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
    responses = ray.get(futures)
    if flatten:
        return flatten_array(responses)
    return responses


def flatten_array(arr):
    """Flatten an array by 1 dimension."""
    shape = np.array(arr).shape
    if len(shape) == 1:
        return arr
    return [item for list_1d in arr for item in list_1d]
