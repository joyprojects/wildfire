class GoesSequence:
    def __init__(self, scans):
        # verify input
        self.scans = scans  # to dictionary by scan time
        # fisrt scan time
        # last scan time

    def __getitem__(self, key):
        return self.scans[key]

    def __iter__(self):
        yield self.scans.items()

    def _verify_input(self):
        raise NotImplementedError

    def plot_video(self, channel):
        raise NotImplementedError

    def to_netcdf(self):
        raise NotImplementedError


def get_goes_sequence(satellite, region, channel, start_time_utc, end_time_utc):
    raise NotImplementedError
