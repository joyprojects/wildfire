"""Utilities for getting and interacting with GOES-16/17 satellite data."""
from .band import GoesBand, read_netcdf
from .scan import GoesScan, read_netcdfs
