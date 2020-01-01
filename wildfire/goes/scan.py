class GoesScan:
    def __init__(self, channels):
        # verify input
        self.channels = channels  # parse to dictionary by band number
        # scan time
        # satellite
        # region

    def __getitem__(self, key):
        return self.channels[key]

    def __iter__(self):
        yield self.channels.items()

    def _verify_input(self):
        raise NotImplementedError

    def scale_to_500m(self):
        raise NotImplementedError

    def to_netcdf(self):
        raise NotImplementedError

    def next(self):
        raise NotImplementedError

    def previous(self):
        raise NotImplementedError

    def plot(self):
        raise NotImplementedError

    @property
    def channels(self):
        return self.channels.keys()


def get_goes_scan(satellite, region, scan_time_utc):
    raise NotImplementedError


def from_netcdfs(paths):
    raise NotImplementedError
