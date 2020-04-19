from wildfire.data import goes_level_1
from wildfire.data.goes_level_2 import utilities


def test_match_level_1(l2_wildfire):
    actual = utilities.match_level_1(
        level_2=l2_wildfire["l2"], level_1_directory=l2_wildfire["l1_directory"]
    )
    assert isinstance(actual, goes_level_1.GoesScan)
    assert actual == l2_wildfire["l1"]
