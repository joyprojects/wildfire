import datetime

from wildfire.goes import band


def test_from_netcdf_s3(s3_bucket_key):
    actual = band.from_netcdf(
        filepath=f"s3://{s3_bucket_key['bucket']}/{s3_bucket_key['key']}"
    )
    assert isinstance(actual, band.GoesBand)


def test_get_goes_band():
    satellite = "noaa-goes17"
    region = "M1"
    channel = 7
    scan_time_utc = datetime.datetime(2019, 10, 1, 10, 5)
    actual = band.get_goes_band(
        satellite=satellite, region=region, band=channel, scan_time_utc=scan_time_utc
    )
    assert isinstance(actual, band.GoesBand)
    assert actual.band == channel
    assert actual.region == region
    assert actual.satellite == satellite
    assert (actual.scan_time_utc - scan_time_utc).total_seconds() < 60
