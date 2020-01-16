"""Label wildfires in GOES-R Satellite data."""
import logging
import os

from wildfire.goes import band, scan, utilities
from wildfire.threshold_model import model

_logger = logging.getLogger(__name__)


def label_local_files(filepaths):
    """Label local GOES satellite data matching parameters with wildfires."""
    _logger.info("Labelling local wildfires...")
    _logger.info("Grouping files into scans...")
    scans = utilities.group_filepaths_into_scans(filepaths=filepaths)

    _logger.info("Processing %d scans with %d workers...", len(scans), os.cpu_count())
    wildfires = utilities.imap_function(function=_process_scan, function_args=scans)
    wildfires = list(filter(None, wildfires))
    _logger.info("Found %d wildfires.", len(wildfires))
    return wildfires


def _process_scan(filepaths):
    goes_scan = scan.read_netcdfs(
        filepaths=filepaths, transform_func=band.filter_bad_pixels
    )
    if model.has_wildfire(goes_scan=goes_scan):
        return {
            "scan_time_utc": goes_scan.scan_time_utc.strftime("%Y-%m-%dT%H:%M:%S%f"),
            "region": goes_scan.region,
            "satellite": goes_scan.satellite,
        }
    return None
