"""Utilities for multiprocessing."""
from contextlib import contextmanager
import logging

from dask.distributed import Client, LocalCluster, progress
from dask_jobqueue import PBSCluster
import numpy as np

_logger = logging.getLogger(__name__)


def map_function(function, function_args, pbs=False, **cluster_kwargs):
    """Parallize `function` over `function_args` across available CPUs.

    Utilizes dask.distributed.Client.map which follows the implementation of built-in
    `map`. See https://docs.python.org/3/library/functions.html#map and
    https://distributed.dask.org/en/latest/client.html.

    Examples
    --------
    ```
    def add(x, y):
        return x + y

    xs = [1, 2, 3, 4]
    ys = [11, 12, 13, 14]

    map_function(add, [xs, ys]) => [12, 14, 16, 18]
    ```


    Parameters
    ----------
    function : function | method
    function_args : list
        If `function` takes multiple args, follow implementation of `map`. Namely, if
        f(x1, x2) => y, then `function_args` should be `[all_x1, all_x2]`.
    pbs : bool, optional
        Whether or not to create a PBS job over whose cluster to parallize, by default
        False.

    Returns
    -------
    list
    """
    _logger.info(
        "Running %s in parallel with args of shape %s",
        function.__name__,
        np.shape(function_args),
    )
    with dask_client(pbs=pbs, **cluster_kwargs) as client:
        if len(np.shape(function_args)) == 1:
            function_args = [function_args]

        futures = client.map(function, *function_args)
        progress(futures)
        return_values = client.gather(futures)

    return return_values


@contextmanager
def dask_client(pbs=False, **cluster_kwargs):
    """Context manager surrounding a dask client. Handles closing upon completion.

    Examples
    --------
    ```
    with dask_client() as client:
        client.do_something()
    ```

    Parameters
    ----------
    pbs: bool, optional
        Whether or not dask should submit a PBS job over whose cluster to operate.
    **cluster_kwargs:
        Arguments to either `PBSCluster` or `LocalCluster` which are pretty much the
        same. Some usefule arguments include:
            - n_workers
            - cores
            - interface
            - memory
            - walltime
    """
    cluster = (
        PBSCluster(**cluster_kwargs)
        if pbs
        else LocalCluster(processes=False, **cluster_kwargs)
    )
    client = Client(cluster)
    try:
        _logger.info("Dask Cluster: %s\nDask Client: %s", cluster, client)
        yield client

    finally:
        client.close()
    _logger.info("Dask Cluster: %s\nDask Client: %s", cluster, client)
    return client


def flatten_array(arr):
    """Flatten an array by 1 dimension."""
    shape = np.array(arr).shape
    if len(shape) == 1:
        return arr
    return [item for list_1d in arr for item in list_1d]
