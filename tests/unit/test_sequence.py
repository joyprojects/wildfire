import datetime

from wildfire import goes


def test_sequence(all_bands):
    goes_scan = goes.GoesScan(all_bands)

    actual = goes.GoesSequence(scans=[goes_scan])
    assert actual.first_scan_utc == goes_scan.scan_time_utc
    assert actual.last_scan_utc == goes_scan.scan_time_utc
    assert actual[goes_scan.scan_time_utc] == goes_scan
    assert list(actual.keys) == [goes_scan.scan_time_utc]
    assert len(actual) == 1
