"""Wrapper around a group of goes data."""
from . import downloader, scan


def factory(  # pylint: disable=bad-continuation
    satellite, regions, channels, start, end, local_directory=scan.LOCAL_DIRECTORY
):
    s3_objects = downloader.query_s3(
        satellite=satellite, regions=regions, channels=channels, start=start, end=end
    )
    filepaths = [obj.key for obj in s3_objects]
    return GoesSequence(filepaths=filepaths, local_directory=local_directory)


class GoesSequence:
    def __init__(self, filepaths, local_directory):
        raise NotImplementedError

    def plot_time_series(self):
        # for channel, region in dataset plot animation
        # should accept a stepsize
        raise NotImplementedError

    def plot_individual_scans(self):
        # probably should just thoughtfully create the col x row of the figure and then
        # use the GoesScan.plot() method
        raise NotImplementedError

    def get(self):
        raise NotImplementedError

    def _process(self):
        raise NotImplementedError

    def _check_local(self):
        # probably will use glob and then filter all the filepaths that are not local
        raise NotImplementedError

    def _to_reflectance_factor(self):
        raise NotImplementedError

    def _to_brightness_temperature(self):
        raise NotImplementedError

    def _to_2km_resolution(self):
        raise NotImplementedError

    def _filter_bad_pixels(self):
        raise NotImplementedError
