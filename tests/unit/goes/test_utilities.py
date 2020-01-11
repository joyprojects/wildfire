import datetime

import numpy as np
import scipy.stats as st

from wildfire.goes import utilities


def test_parse_filename():
    filepath = "/ABI-L1b-RadM/2019/300/20/OR_ABI-L1b-RadM1-M6C14_G17_s20193002048275_e20193002048332_c20193002048405.nc"
    actual = utilities.parse_filename(filename=filepath)
    assert actual[0] == "M1"
    assert actual[1] == 14
    assert actual[2] == "noaa-goes17"
    assert actual[3] == datetime.datetime(2019, 10, 27, 20, 48, 27, 500000)


def test_normalize():
    x = np.array([1, 2, 3, 4, 5])
    actual = utilities.normalize(data=x)
    expected = st.zscore(x)
    np.testing.assert_array_equal(actual, expected)


def test_create_time_range():
    start = datetime.datetime(2019, 1, 1, 0, 0)
    end = datetime.datetime(2019, 1, 1, 0, 59)
    actual = utilities.create_time_range(start=start, end=end, minutes=1)

    assert isinstance(actual, list)
    assert isinstance(actual[0], datetime.datetime)
    assert actual == sorted(actual)
    assert actual[0] == start
    assert actual[-1] == end
    assert len(actual) == 60


def _timer(index):
    # This is used by test_pool_function(), unhappily we have to define it here until we
    # learn more about the problem.
    time.sleep(1)
    return index


def test_pool_function():
    num_cores = multiprocessing.cpu_count()
    if num_cores > 1:
        started_at = datetime.datetime.utcnow()
        utilities.pool_function(_timer, list(range(num_cores)), num_workers=num_cores)
        actual = (datetime.datetime.utcnow() - started_at).total_seconds()
        np.testing.assert_almost_equal(actual, 1, decimal=0)
