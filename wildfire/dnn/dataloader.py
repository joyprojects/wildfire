import os
import glob
import numpy as np

import torch
from torch.utils.data import Dataset

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
        return np.transpose(inputs, (2,0,1)), label[np.newaxis]

