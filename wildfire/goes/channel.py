class GoesChannel:
    def __init__(self, dataset):
        self.dataset = dataset
        # scan time
        # satellite
        # region

    def plot(self):
        raise NotImplementedError

    def normalize(self):
        raise NotImplementedError

    def process(self):
        raise NotImplementedError

    def to_lat_lon(self):
        raise NotImplementedError

    def filter_good_pixels(self):
        raise NotImplementedError

    def to_netcdf(self):
        raise NotImplementedError

    def build_local_path(self):
        raise NotImplementedError

    def build_s3_path(self):
        raise NotImplementedError


def get_goes_channel(satellite, region, channel, scan_time_utc):
    raise NotImplementedError


def from_netcdf(filepath):
    raise NotImplementedError
