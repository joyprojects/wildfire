import datetime
import os
import tempfile

from wildfire import goes


def test_sequence(all_bands_wildfire):
    goes_scan = goes.GoesScan(all_bands_wildfire)

    actual = goes.GoesSequence(scans=[goes_scan])
    assert actual.first_scan_utc == goes_scan.scan_time_utc
    assert actual.last_scan_utc == goes_scan.scan_time_utc
    assert actual.region == goes_scan.region
    assert actual.satellite == goes_scan.satellite
    assert actual[goes_scan.scan_time_utc] == goes_scan
    assert list(actual.keys) == [goes_scan.scan_time_utc]
    assert len(actual) == 1
    with tempfile.TemporaryDirectory() as temp_directory:
        filepaths = actual.to_netcdf(directory=temp_directory)
        for filepath in filepaths:
            assert os.path.exists(filepath)
