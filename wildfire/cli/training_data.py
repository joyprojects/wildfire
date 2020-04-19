"""Create training datasets.

Uses `ray` so that it can also be distributed across compute nodes.
"""
import logging

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
def goes_l2_cnn(
    level_1_directory, level_2_directory, persist_directory, height, width, stride
):
    """Create GOES level 2 training data for the DNN.

    Usage: `training-data goes-l2-cnn ./level_1_directory ./level_2_directory`
    """
    _logger.info("Creating training data from GOES level 2 wildfire data...")
    dnn.training_data.create_goes_level_2_training_data(
        level_2_directory=level_2_directory,
        level_1_directory=level_1_directory,
        persist_directory=persist_directory,
        height=height,
        width=width,
        stride=stride,
    )
    _logger.info("Job complete.")


@training_data.command()
def threshold_cnn():
    """Not yet implemented."""
    pass
