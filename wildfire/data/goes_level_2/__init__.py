"""Methods for downloading, parsing, and analyzing GOES Level 2 Wildfire data.

Full Scans of Fire for GOES-17
https://s3.console.aws.amazon.com/s3/buckets/noaa-goes17/ABI-L2-FDCF/?region=us-east-1&tab=overview

CONUS Scans of Fire for GOES-17
https://s3.console.aws.amazon.com/s3/buckets/noaa-goes17/ABI-L2-FDCC/?region=us-east-1&tab=overview

Full Scans of Fire for GOES-16
https://s3.console.aws.amazon.com/s3/buckets/noaa-goes16/ABI-L2-FDCF/?region=us-east-1&tab=overview

CONUS Scans of Fire for GOES-16
https://s3.console.aws.amazon.com/s3/buckets/noaa-goes16/ABI-L2-FDCC/?region=us-east-1&tab=overview
"""
from .utilities import *
