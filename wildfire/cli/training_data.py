"""Create training datasets.

Uses `ray` so that it can also be distributed across compute nodes.
"""
import logging
import os

import click

from wildfire.models import dnn

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


@click.group()
def training_data():
    """Create training data for the wildfire models."""
    pass


@training_data.command()
@click.argument("level_1_directory", type=click.Path(exists=True, file_okay=False))
@click.argument("level_2_directory", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--persist_directory",
    type=click.Path(exists=True, file_okay=False),
    default="./downloaded_data",
)
@click.option("--height", default=32, type=click.INT, help="Height of image patch")
@click.option("--width", default=32, type=click.INT, help="Width of image patch")
@click.option("--stride", default=32, type=click.INT, help="Stride of image patch")
@click.option("--pbs", is_flag=True, help="If running using a PBS cluster.")
@click.option("--num_jobs", default=1, help="Number of jobs to submit.")
def goes_l2_cnn(
    level_1_directory,
    level_2_directory,
    persist_directory,
    height,
    width,
    stride,
    pbs,
    num_jobs,
):
    """Create GOES level 2 training data for the DNN.

    Usage: `training-data goes-l2-cnn ./level_1_directory ./level_2_directory`

    If using PBS, then additional configuration can be set in the file located at
    `os.environ["PBS_CONFIG_FILE"]`
    """
    _logger.info(
        """Creating training data from GOES level 2 wildfire data.
    GOES Level 1 Directory: %s
    GOES Level 2 Directory: %s
    Persist Directory: %s
    Height: %s
    Width: %s
    Stride: %s
    PBS: %s
    Number of Processes: %s
    Number of Jobs: %s""",
        level_1_directory,
        level_2_directory,
        persist_directory,
        height,
        width,
        stride,
        pbs,
        os.cpu_count(),
        num_jobs,
    )

    cluster_kwargs = {"n_workers": num_jobs}
    dnn.training_data.create_goes_level_2_training_data(
        level_2_directory=level_2_directory,
        level_1_directory=level_1_directory,
        persist_directory=persist_directory,
        height=height,
        width=width,
        stride=stride,
        pbs=pbs,
        **cluster_kwargs,
    )
    _logger.info("Job completed.")


@training_data.command()
def threshold_cnn():
    """Not yet implemented."""
    pass
