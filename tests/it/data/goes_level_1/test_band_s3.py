import datetime
import tempfile

from wildfire.data.goes_level_1 import band


def test_get_goes_band_local():
    satellite = "noaa-goes17"
    region = "M1"
    channel = 5
    scan_time = datetime.datetime(2019, 1, 1, 1, 1)

    with tempfile.TemporaryDirectory() as temporary_directory:
        actual = band.get_goes_band(
            satellite=satellite,
            region=region,
            channel=channel,
            scan_time_utc=scan_time,
            local_directory=temporary_directory,
        )
        assert isinstance(actual, band.GoesBand)
        assert actual.band_id == channel
        assert actual.region == region
        assert actual.satellite == "G17"
        assert actual.scan_time_utc.strftime("%Y-%j-%H:%M") == scan_time.strftime(
            "%Y-%j-%H:%M"
        )
