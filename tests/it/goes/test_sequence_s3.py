import datetime

from wildfire import goes


def test_get_goes_sequence():
    satellite = "noaa-goes17"
    region = "M1"
    start_time_utc = datetime.datetime(2019, 10, 1, 10, 5)
    end_time_utc = datetime.datetime(2019, 10, 1, 11, 4)
    actual = goes.get_goes_sequence(
        satellite=satellite,
        region=region,
        start_time_utc=start_time_utc,
        end_time_utc=end_time_utc,
        max_scans_per_hour=2,
    )
    assert isinstance(actual, goes.GoesSequence)
    assert actual.region == region
    assert actual.satellite == satellite
    assert actual.first_scan_utc >= start_time_utc
    assert actual.last_scan_utc <= end_time_utc
    assert len(actual) == 2
