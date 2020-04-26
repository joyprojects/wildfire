import xarray as xr

from wildfire.data import goes_level_1
from wildfire.data.goes_level_2 import utilities


def test_match_level_1(goes_level_2):
    actual = utilities.match_level_1(
        level_2=xr.load_dataset(goes_level_2["level_2"]),
        level_1_directory=goes_level_2["level_1_directory"],
    )
    assert isinstance(actual, goes_level_1.GoesScan)
    assert actual == goes_level_1.read_netcdfs(goes_level_2["level_1"])
