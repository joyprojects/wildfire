import logging

import click

from wildfire.goes import downloader

DATETIME_FORMATS = ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


@click.group()
def download():
    pass


@download.command()
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
    "--persist_directory",
    default="./downloaded_data",
    type=click.Path(exists=True, file_okay=False),
    help="Directory in which to look for or download GOES data.",
)
def goes_level_1(start, end, satellite, region, persist_directory):
    """Download GOES Level 1b data from Amazon S3.

    Usage: `download goes-level-1 2019-01-01 2019-02-01`
    """
    _logger.info(
        """Downloading available GOES satellite data. Parameters:
    Satellite: %s
    Regions: %s
    Channels: %s
    Start Time: %s
    End Time: %s""",
        satellite,
        region,
        list(range(1, 17)),
        start,
        end,
    )
    downloader.download_files(
        local_directory=persist_directory,
        satellite=satellite,
        region=region,
        start_time=start,
        end_time=end,
    )
    _logger.info("Success.")


@download.command()
def goes_level_2():
    pass


@download.command()
def modis():
    pass
