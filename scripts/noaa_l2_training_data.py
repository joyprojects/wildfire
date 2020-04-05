import os, sys
from datetime import datetime
import glob

import xarray as xr
import numpy as np
from mpi4py import MPI
#import h5py

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from wildfire import wildfire
from wildfire.goes import utilities, scan

# Open MPI communiciation
comm = MPI.COMM_WORLD
rank = comm.Get_rank() # process rank
size = comm.Get_size() # number of processes 
name = MPI.Get_processor_name()

# 2019-09-07T01:50:13.1Z
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

year = 2019
dayofyear = '*'
hour = '*'
satellite = 'noaa-goes16'

patch_size = 32

fire_path = '/nobackupp10/tvandal/data/goes16/ABI-L2-FDCF/{}/{}/{}/'
ABI_directory = '/nex/datapool/geonex/public/GOES16/NOAA-L1B/'

training_directory = '/nobackupp10/tvandal/wildfire/.tmp/training-data/abi-noaal1b-F/'

if not os.path.exists(training_directory):
    os.makedirs(training_directory)

def extract_patches_2d(arr, height, width, stride):
    '''
    Given a Tensor of shape (H, W, ...) extract patches of 
    size (height, width) with stride
    '''
    assert len(arr.shape) >= 2
    H, W = arr.shape[:2]
    ih = np.arange(0,H,stride)
    iw = np.arange(0,W,stride)
    patches = []
    for i in ih:
        i = min(i, H-height)
        for j in iw:
            j = min(j, W-width)
            patches.append(arr[i:i+height, j:j+height][np.newaxis])
    return np.concatenate(patches)


def get_file_examples(fire_file):
    '''
    Given a NOAA L2 Fire file, match with corresonding ABI scan
    Return patches where fires exist
    '''
    ds_fire = xr.open_dataset(fire_file)

    start_time = ds_fire.attrs['time_coverage_start'].split('.')[0]
    start_time = datetime.strptime(start_time, DATETIME_FORMAT)
    abi_files = utilities.list_local_files(ABI_directory, satellite, 'F', start_time)
    abi_scan = scan.read_netcdfs(local_filepaths=abi_files)
    abi_scan_2km = abi_scan.rescale_to_2km() 
    
    rads = []
    band16 = abi_scan_2km['band_16']
    x_2km = band16.dataset.x.values
    y_2km = band16.dataset.y.values
    for band, s in abi_scan_2km.iteritems():
        rads.append(s.normalize())
        rads[-1] = rads[-1].assign_coords(x=x_2km, y=y_2km)
        
    scan_rads = xr.concat(rads, 'band')
    
    alldata = np.concatenate([scan_rads.values, ds_fire.Temp.values[np.newaxis]], 0)
    alldata = np.transpose(alldata, (1,2,0))
    alldata_patches = extract_patches_2d(alldata, patch_size, patch_size, patch_size)

    fire_idxs = np.any(np.isfinite(alldata_patches[:,:,:,-1]), axis=(1,2))
    alldata_fire_patches = alldata_patches[fire_idxs]
    return alldata_fire_patches

if rank == 0:
    fire_files = glob.glob(fire_path.format(year, dayofyear, '*') + '*.nc')
    n = len(fire_files) // (size-1)
    fire_files = [fire_files[i:i+n] for i in range(0, len(fire_files), n)]
    print(len(fire_files))
else:
    fire_files = None

fire_files = comm.scatter(fire_files, root=0)
collect_examples = []
for f in fire_files[:10]: #@TODO remove
    examples = get_file_examples(f)
    collect_examples.append(examples)

examples = np.concatenate(collect_examples, axis=0)

inputs = examples[:,:,:,:16].astype(np.float32)
labels = examples[:,:,:,16].astype(np.float32)

example_file = os.path.join(training_directory, '%03i.nc' % rank)
dsout = xr.Dataset({"abi": xr.DataArray(inputs), 
                    "fire_temp": xr.DataArray(labels)})
dsout.to_netcdf(example_file)
print(f"Rank: {rank} -- Saved examples to file: {example_file}")
