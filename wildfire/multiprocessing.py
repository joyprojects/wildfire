"""Utilities for multiprocessing."""
import logging

from dask.distributed import Client, LocalCluster, progress
from dask_jobqueue import PBSCluster
import numpy as np

_logger = logging.getLogger(__name__)


def map_function(function, function_args, pbs=False, **cluster_kwargs):
    dask_client = start_dask_client(pbs=pbs, **cluster_kwargs)

    _logger.info(
        "Running %s in parallel with args of shape %s",
        function.__name__,
        np.shape(function_args),
    )

    if len(np.shape(function_args)) == 1:
        function_args = [function_args]

    futures = dask_client.map(function, *function_args)
    progress(futures)
    return_values = dask_client.gather(futures)
    dask_client.close()
    return return_values


def start_dask_client(pbs=False, **cluster_kwargs):
    cluster = (
        PBSCluster(**cluster_kwargs)
        if pbs
        else LocalCluster(processes=False, **cluster_kwargs)
    )
    client = Client(cluster)
    _logger.info("Dask Cluster: %s\nDask Client: %s", cluster, client)
    return client


def flatten_array(arr):
    """Flatten an array by 1 dimension."""
    shape = np.array(arr).shape
    if len(shape) == 1:
        return arr
    return [item for list_1d in arr for item in list_1d]
