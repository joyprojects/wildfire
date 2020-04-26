"""Create model predictions.

This module uses `ray` so that it can also be distributed across compute nodes.
"""
import logging
import os

import click

from wildfire.data import goes_level_1
from wildfire.models import threshold_model

DATETIME_FORMATS = ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


@click.group()
def predict():
    """Use the wildfire models to predict."""
    pass


@predict.command()
@click.argument("start", type=click.DateTime(formats=DATETIME_FORMATS))
@click.argument("end", type=click.DateTime(formats=DATETIME_FORMATS))
@click.option(
    "--satellite",
    default="noaa-goes17",
    type=click.Choice(["noaa-goes16", "noaa-goes17"]),
    help="GOES East|GOES East.",
)
@click.option(
    "--region",
    default="M1",
    type=click.Choice(["M1", "M2", "C", "F"]),
    help="US West Coast|US East Coast|US Full|Hemisphere.",
)
@click.option(
    "--goes_directory",
    default="./downloaded_data",
    type=click.Path(exists=True, file_okay=False),
    help="Directory in which to look for or download GOES data.",
)
@click.option(
    "--persist_directory",
    default="./labeled_data",
    type=click.Path(exists=True, file_okay=False),
    help="Directory in which to persist wildfires.",
)
@click.option("--pbs", is_flag=True, help="If running using a PBS cluster.")
@click.option("--num_jobs", default=1, type=int, help="Number of jobs to submit.")
def goes_threshold(
    start, end, satellite, region, goes_directory, persist_directory, pbs, num_jobs,
):
    """Label wildfires in GOES Level 1b data.

    Usage: `predict goes-threshold 2019-01-01 2019-01-02`

    If using PBS, then additional configuration can be set in the file located at
    `os.environ["PBS_CONFIG_FILE"]`
    """
    _logger.info(
        """Labeling wildfires from GOES data with the threshold model.
    Satellite: %s
    Region: %s
    Start Time: %s
    End Time: %s
    GOES Directory: %s
    Persist Directory: %s
    PBS: %s
    Number of Processes: %s
    Number of Jobs: %s""",
        satellite,
        region,
        start,
        end,
        goes_directory,
        persist_directory,
        pbs,
        os.cpu_count(),
        num_jobs,
    )

    # only parallel across local hardware
    filepaths = goes_level_1.utilities.list_local_files(
        local_directory=goes_directory,
        satellite=satellite,
        region=region,
        start_time=start,
        end_time=end,
    )
    if not filepaths:
        raise ValueError("No local files found...")

    scan_filepaths = goes_level_1.utilities.group_filepaths_into_scans(filepaths)

    _logger.info("Processing %s scans...", len(scan_filepaths))

    cluster_kwargs = {"n_workers": num_jobs}
    threshold_model.label_wildfires(
        scan_filepaths=scan_filepaths,
        persist_directory=persist_directory,
        satellite=satellite,
        region=region,
        start=start,
        end=end,
        pbs=pbs,
        **cluster_kwargs,
    )
    _logger.info("Job completed.")


@predict.command
def goes_deep():
    """Not yet implemented."""
    pass
