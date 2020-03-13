#!/usr/bin/env python3
import os, sys
from mpi4py import MPI
import argparse
import json

import datetime as dt

import logging
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from wildfire import wildfire
from wildfire.goes import utilities

_logger = logging.getLogger(__name__)

# Open MPI communiciation
comm = MPI.COMM_WORLD
rank = comm.Get_rank() # process rank
size = comm.Get_size() # number of processes 
name = MPI.Get_processor_name()

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
WILDFIRE_FILENAME = "wildfires_{satellite}_{region}_s{start}_e{end}_c{created}.json"


# first process gets file paths to pass out to worker nodes
if rank == 0:
    parser = argparse.ArgumentParser()
    parser.add_argument("--satellite", default='noaa-goes17', type=str)
    parser.add_argument("--region", default='M1', type=str)
    parser.add_argument("--start", default='2019-10-31T22:00:00', type=str)
    parser.add_argument("--end", default='2019-10-31T23:00:00', type=str)
    parser.add_argument("--goes_directory", default='../downloaded_data', type=str)
    parser.add_argument("--wildfires_directory", default='../labeled_wildfires', type=str)
    args = parser.parse_args()

    start_time = dt.datetime.strptime(args.start, DATETIME_FORMAT)
    end_time = dt.datetime.strptime(args.end, DATETIME_FORMAT)

    filepaths = utilities.list_local_files(local_directory=args.goes_directory,
                                           satellite=args.satellite,
                                           region=args.region,
                                           start_time=start_time,
                                           end_time=end_time
                                          )
    filepaths = utilities.group_filepaths_into_scans(filepaths=filepaths)
else:
    filepaths = None


# send filepaths to each process
filepaths = comm.bcast(filepaths, root=0)


n_scans = len(filepaths)
_logger.info(f"Number of scans locally: {n_scans}")

collect_fires = []
# loop through scans
for i, scan_files in enumerate(filepaths):
    # split by process
    if i % size == rank:
        try:
            scan_fires = wildfire.parse_scan_for_wildfire(scan_files) # dict
            if scan_fires is not None:
                collect_fires.append(scan_fires)
        except (OSError, ValueError) as error_message:
            _logger.warning(
                "\nSkipping malformed goes_scan comprised of %s.\nError: %s",
                scan_files,
                error_message,
            )


# send all fires to root node
all_fires = comm.gather(collect_fires, root=0)

if rank == 0:
     # make a large list of all fires
    all_fires = [fire for rank_fires in all_fires for fire in rank_fires]

    wildfires_filepath = os.path.join(
        args.wildfires_directory,
        WILDFIRE_FILENAME.format(
            satellite=args.satellite,
            region=args.region,
            start=start_time.strftime(DATETIME_FORMAT),
            end=end_time.strftime(DATETIME_FORMAT),
            created=dt.datetime.utcnow().strftime(DATETIME_FORMAT),
        ),
    )
    _logger.info("Persisting wildfires to %s" % wildfires_filepath)
    with open(wildfires_filepath, "w+") as buffer:
        json.dump(dict(enumerate(all_fires)), buffer)
