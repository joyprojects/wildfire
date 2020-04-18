"""Methods for downloading, parsing, and analyzing GOES Level 1 data.

GOES-16 CONUS
https://s3.console.aws.amazon.com/s3/buckets/noaa-goes16/ABI-L1b-RadC/?region=us-east-1&tab=overview

GOES-16 Full
https://s3.console.aws.amazon.com/s3/buckets/noaa-goes16/ABI-L1b-RadF/?region=us-east-1&tab=overview

GOES-16 Mesoscale
https://s3.console.aws.amazon.com/s3/buckets/noaa-goes16/ABI-L1b-RadM/?region=us-east-1&tab=overview

GOES-17 CONUS
https://s3.console.aws.amazon.com/s3/buckets/noaa-goes17/ABI-L1b-RadC/?region=us-east-1&tab=overview

GOES-17 Full
https://s3.console.aws.amazon.com/s3/buckets/noaa-goes17/ABI-L1b-RadF/?region=us-east-1&tab=overview

GOES-17 Mesoscale
https://s3.console.aws.amazon.com/s3/buckets/noaa-goes17/ABI-L1b-RadM/?region=us-east-1&tab=overview
"""
from .band import get_goes_band, GoesBand, read_netcdf
from .scan import get_goes_scan, GoesScan, read_netcdfs
