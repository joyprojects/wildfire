import datetime
import tempfile

from wildfire.data.goes_level_1 import scan


def test_get_goes_scan_local():
    satellite = "noaa-goes17"
    region = "M1"
    scan_time = datetime.datetime(2019, 1, 1, 1, 1)

    with tempfile.TemporaryDirectory() as temporary_directory:
        actual = scan.get_goes_scan(
            satellite=satellite,
            region=region,
            scan_time_utc=scan_time,
            local_directory=temporary_directory,
        )
        assert isinstance(actual, scan.GoesScan)
        assert actual.region == region
        assert actual.satellite == "G17"
        assert actual.scan_time_utc.strftime("%Y-%j-%H:%M") == scan_time.strftime(
            "%Y-%j-%H:%M"
        )
