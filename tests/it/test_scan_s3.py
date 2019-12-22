from wildfire.goes import scan


def test_read_nc():
    actual = scan.read_nc(
        filepath="s3://noaa-goes17/ABI-L1b-RadM/2019/001/00/OR_ABI-L1b-RadM1-M3C01_G17_s20190010000270_e20190010000327_c20190010000358.nc"
    )
    assert isinstance(actual, scan.GoesScan)
