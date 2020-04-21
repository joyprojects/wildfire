import os
import glob
import numpy as np

import torch
from torch.utils.data import Dataset, ConcatDataset

import xarray as xr

# Pytorch Dataset iterator
class WildfireThreshold(Dataset):
    def __init__(self, example_directory):
        super(WildfireThreshold, self).__init__()
        self.filelist = glob.glob(os.path.join(example_directory, "*.torch"))

    def __len__(self):
        return len(self.filelist)

    def __getitem__(self, idx):
        example = torch.load(self.filelist[idx])
        inputs = example['inputs'].astype(np.float32)
        label = example['label'].astype(np.float32)
        inputs[np.isnan(inputs)] = 0.
        return np.transpose(inputs, (2,0,1)), label[np.newaxis]

class WildfireNOAA(Dataset):
    def __init__(self, example_file):
        super(WildfireNOAA, self).__init__()
        self.file = example_file
        self.ds = xr.open_dataset(self.file)
        
    def __len__(self):
        return self.ds['abi'].shape[0]
    
    def __getitem__(self, idx):
        inputs = self.ds['abi'].values[idx] # H, W, C
        label = self.ds['fire_temp'].values[idx].astype(np.float32) # H, W
        inputs[np.isnan(inputs)] = 0.
        inputs[np.abs(inputs) > 1e5] = 0.
        label[np.isnan(label)] = 0.
        label[label > 0.] = 1.
        label[label <= 0.] = 0. 
        # C, H, W
        return np.transpose(inputs, (2,0,1)), label[np.newaxis]
        

def get_wildfire_dataset(example_directory):
    files = glob.glob(os.path.join(example_directory, '*.nc'))
    datasets = [WildfireNOAA(f) for f in files]
    return ConcatDataset(datasets)