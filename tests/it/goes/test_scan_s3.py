import datetime

from wildfire import goes


def test_get_goes_scan():
    satellite = "noaa-goes17"
    region = "M1"
    scan_time_utc = datetime.datetime(2019, 10, 1, 10, 5)
    actual = goes.get_goes_scan(
        satellite=satellite, region=region, scan_time_utc=scan_time_utc
    )
    assert isinstance(actual, goes.GoesScan)
    assert actual.region == region
    assert actual.satellite == satellite
    assert (actual.scan_time_utc - scan_time_utc).total_seconds() < 60


def test_get_next_goes_scan(all_bands_wildfire):
    original = goes.GoesScan(bands=all_bands_wildfire)
    actual = original.next()
    assert isinstance(actual, goes.GoesScan)
    assert actual.scan_time_utc == original.scan_time_utc + datetime.timedelta(minutes=1)


def test_get_previous_goes_scan(all_bands_wildfire):
    original = goes.GoesScan(bands=all_bands_wildfire)
    actual = original.previous()
    assert isinstance(actual, goes.GoesScan)
    assert actual.scan_time_utc == original.scan_time_utc - datetime.timedelta(minutes=1)
