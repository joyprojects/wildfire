import datetime

from wildfire.goes import sequence, scan


def test_sequence_init(all_bands):
    goes_scan = scan.GoesScan(all_bands)

    actual = sequence.GoesSequence(scans=[goes_scan])
    assert list(actual.keys) == [goes_scan.scan_time_utc]
    assert actual[goes_scan.scan_time_utc] == goes_scan
    assert actual.first_scan_utc == goes_scan.scan_time_utc
    assert actual.last_scan_utc == goes_scan.scan_time_utc
