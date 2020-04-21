import os, sys
import logging

import torch
import torch.nn as nn
from torch.utils import data
from torch.utils.tensorboard import SummaryWriter

import torchvision

import dataloader
import networks

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

model_path = '/nobackupp10/tvandal/wildfire/.tmp/models/noaa-wildfire-bigger-dropout/'
#data_path = '/nobackupp10/tvandal/wildfire/.tmp/training-data/'
data_path = '/nobackupp10/tvandal/wildfire/.tmp/training-data/abi-noaal1b-F/'

def normalize_image(x):
    mx = torch.max(x)
    mn = torch.min(x)
    x = (x - mn) / (mx - mn)
    return x


class CNNTrainer(nn.Module):
    def __init__(self, params):
        super(CNNTrainer, self).__init__()
        self.params = params

        # load model
        #self.net = networks.BasicCNNClassifier(params['hidden'])
        self.net = networks.BiggerCNNClassifier(params['hidden'])

        # define optimizer
        self.global_step = 0.
        self.optimizer = torch.optim.Adam(self.net.parameters(), lr=params['lr'])

        # define a loss
        self.cross_entropy = nn.BCELoss()

        # set checkpoint file
        model_path = params['model_path']
        self.checkpoint_filename = os.path.join(model_path, 'checkpoint.torch')
        if not os.path.exists(model_path):
            os.makedirs(model_path)

        # Summary writer for tensorboard
        self.tfwriter = SummaryWriter(os.path.join(params['model_path'], 'classifier.tfsummary'))

    def gen_update(self, x, y, log=False):
        # make prediction
        yhat = self.net(x)

        # compute loss
        h = y.shape[2]
        pad = (h-yhat.shape[2]) // 2
        y_sub = y[:,:,pad:-pad,pad:-pad]
        loss = self.cross_entropy(yhat, y_sub)

        # minimize loss and update weights 
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        if log:
            _logger.info(f"Step: {self.global_step},  Loss: {loss.item()}")

            self.tfwriter.add_scalar("loss/cross_entropy", loss, global_step=self.global_step)

            grid_inputs = torchvision.utils.make_grid(x[:4,[1,2,0]])
            grid_labels = torchvision.utils.make_grid(y[:4,:,pad:-pad,pad:-pad])
            grid_predictions = torchvision.utils.make_grid(yhat[:4])

            self.tfwriter.add_image("inputs", normalize_image(grid_inputs), global_step=self.global_step)
            self.tfwriter.add_image("labels", grid_labels, global_step=self.global_step)
            self.tfwriter.add_image("predictions", grid_predictions, global_step=self.global_step)

            prediction = yhat > 0.5
            correct = torch.sum(prediction == y_sub)
            acc = correct.float() / y_sub.numel()
            self.tfwriter.add_scalar("accuracy", acc, global_step=self.global_step)

            for c in range(0, x.shape[1]):
                self.tfwriter.add_histogram(f"inputs/channel_{c+1}", x[:,c], global_step=self.global_step)

        self.global_step += 1

    def save_checkpoint(self):
        state = {'state_dict': self.net.state_dict(),
                 'optimizer': self.optimizer.state_dict(),
                 'global_step': self.global_step}
        torch.save(state, self.checkpoint_filename)

    def load_checkpoint(self):
        checkpoint_file = self.checkpoint_filename
        if not os.path.isfile(checkpoint_file):
            _logger.info("Checkpoint does not exists: %s" % checkpoint_file)
            return
        checkpoint = torch.load(checkpoint_file)
        _logger.info("checkpoint_file: %s" % checkpoint_file)
        self.global_step = checkpoint['global_step']
        self.net.load_state_dict(checkpoint['state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])

def train(model_path=model_path,
          data_path=data_path,
          total_steps=20000,
          batch_size=32,
          lr=1e-3,
          hidden=16,
          log_step=100,
          save_step=1000):

    training_params = dict(batch_size=batch_size,
                           lr=lr, model_path=model_path, hidden=hidden)

    # set device
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    # set trainer
    trainer = CNNTrainer(training_params)
    trainer.net = trainer.net.to(device)
    trainer.load_checkpoint()

    # load wildfire iterator
    #wildfires = dataloader.WildfireThreshold(data_path)
    wildfires = dataloader.get_wildfire_dataset(data_path)
    data_params = {'batch_size': batch_size, 'shuffle': True,
                   'num_workers': 20, 'pin_memory': True}
    training_generator = data.DataLoader(wildfires, **data_params)

    while trainer.global_step < total_steps:
        for batch_idx, (inputs, labels) in enumerate(training_generator):
            '''
            Inputs need to be normalized per band with global mean and std
            '''
            step = trainer.global_step
            log = True if (step % log_step == 0) else False
            trainer.gen_update(inputs.to(device), labels.to(device), log=log)

            if (step % save_step == 0):
                trainer.save_checkpoint()


if __name__ == "__main__":
    train()
