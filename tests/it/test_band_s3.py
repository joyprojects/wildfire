import datetime

from wildfire import goes


def test_get_goes_band():
    satellite = "noaa-goes17"
    region = "M1"
    band = 7
    scan_time_utc = datetime.datetime(2019, 10, 1, 10, 5)
    actual = goes.get_goes_band(
        satellite=satellite, region=region, band=band, scan_time_utc=scan_time_utc
    )
    assert isinstance(actual, goes.GoesBand)
    assert actual.band == band
    assert actual.region == region
    assert actual.satellite == satellite
    assert (actual.scan_time_utc - scan_time_utc).total_seconds() < 60
