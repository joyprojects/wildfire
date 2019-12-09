from dask_jobqueue import PBSCluster
from dask.distributed import Client
import time
from dask.distributed import progress

cluster = PBSCluster(
          # Dask-worker specific keywords
          cores=3,
          memory='100GB',
          processes=6,          # Number of Python processes to cut up each job
          local_directory='$TMPDIR',  # Location to put temporary data if necessary
          # Job scheduler specific keywords
          resource_spec='select=2:ncpus=24:model=sky_gpu:mem=16GB',
          queue='normal',
          project='wildfire',
          walltime='02:00:00',
    )

client = Client(cluster)


def slow_increment(x):
    time.sleep(1)
    return x + 1


futures = client.map(slow_increment, range=5000)
progress(futures)
