import os, sys
import logging

import torch
import torch.nn as nn
from torch.utils import data

import dataloader
import networks

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

model_path = '/nobackupp10/tvandal/wildfire/.tmp/models/first_model/'
data_path = '/nobackupp10/tvandal/wildfire/.tmp/training-data/'
def train(model_path=model_path,
          data_path=data_path,
          epochs=5,
          batch_size=10,
          lr=1e-3):

    # set checkpoint file
    checkpoint_filename = os.path.join(model_path, 'checkpoint.flownet.pth.tar')
    if not os.path.exists(model_path):
        os.makedirs(model_path)

    # set device
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    # load model
    net = networks.BasicCNNClassifier(16)

    # define optimizer
    optimizer = torch.optim.Adam(net.parameters(), lr=lr)

    # define a loss
    bce_loss = nn.BCELoss()

    # load wildfire iterator
    wildfires = dataloader.WildfireThreshold(data_path)
    data_params = {'batch_size': batch_size, 'shuffle': True,
                   'num_workers': 20, 'pin_memory': True}
    training_generator = data.DataLoader(wildfires, **data_params)

    step = 0
    for epoch in range(0, epochs):
        for batch_idx, (inputs, labels) in enumerate(training_generator):
            '''
            Inputs need to be normalized per band with global mean and std
            '''
            # make prediction
            yhat = net(inputs)

            # compute loss 
            loss = bce_loss(yhat, labels)

            # optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            _logger.info(f"Epoch: {epoch}, Batch: {batch_idx}, Loss: {loss.item()}")



    state = {'epoch': epoch, 'state_dict': net.state_dict(),
             'optimizer': optimizer.state_dict()}
    torch.save(state, checkpoint_filename)


if __name__ == "__main__":
    train()
