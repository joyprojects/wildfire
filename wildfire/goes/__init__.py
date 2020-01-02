"""Utilities for getting and interacting with GOES-16/17 satellite data."""
from .band import get_goes_band, GoesBand, read_netcdf
from .scan import get_goes_scan, GoesScan, read_netcdfs
from .sequence import get_goes_sequence, GoesSequence
