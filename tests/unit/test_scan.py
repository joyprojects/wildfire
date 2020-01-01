import datetime

import pytest

from wildfire.goes import scan


def test_scan_init(all_bands):
    actual = scan.GoesScan(bands=all_bands)
    assert actual.region == "M1"
    assert actual.satellite == "noaa-goes17"
    assert actual.scan_time_utc == datetime.datetime(2019, 10, 27, 20, 0, 27, 500000)
    assert list(actual.keys) == [f"band_{idx}" for idx in range(1, 17)]


def test_scan_init_bad_args(all_bands):
    too_many_bands = all_bands + [all_bands[0]]
    with pytest.raises(ValueError) as error_message:
        scan.GoesScan(bands=too_many_bands)
        assert "Too many bands" in error_message

    too_few_bands = all_bands[:15]
    with pytest.raises(ValueError) as error_message:
        scan.GoesScan(bands=too_few_bands)
        assert "Missing bands" in error_message

    all_bands[15].attrs[
        "dataset_name"
    ] = "OR_ABI-L1b-RadM1-M6C01_G16_s20193002000275_e20193002000332_c20193002000379.nc"
    with pytest.raises(ValueError) as error_message:
        scan.GoesScan(bands=all_bands)
        assert "must have same" in error_message
