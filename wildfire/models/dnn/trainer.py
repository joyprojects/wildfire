"""Trainer for wildfire deep neural network."""
import logging
import os

import torch
import torch.nn as nn
from torch.utils import data, tensorboard

import torchvision

from . import dataloader

_logger = logging.getLogger(__name__)


def normalize_image(x):
    maximum = torch.max(x)
    minimum = torch.min(x)
    return (x - minimum) / (maximum - minimum)


class Trainer(nn.Module):
    # pylint: disable=too-many-instance-attributes,abstract-method
    def __init__(self, model, learning_rate, batch_size, persist_directory):
        super(Trainer, self).__init__()

        self.model = model
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.persist_directory = persist_directory

        # define optimizer
        self.global_step = 0.0
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)

        # define a loss function
        self.cross_entropy = nn.BCELoss()

        # set a checkpoint file
        if not os.path.exists(self.persist_directory):
            os.makedirs(self.persist_directory)
        self.checkpoint_filename = os.path.join(
            self.persist_directory, "checkpoint.torch"
        )

        # summary writer for tensorboard
        self.tfwriter = tensorboard.SummaryWriter(
            os.path.join(self.persist_directory, "classifier.tfsummary")
        )

    def update(self, x_input, y_target, log=False):
        # make prediction
        y_predicted = self.model(x_input)

        # compute loss
        pad = (y_target.shape[2] - y_predicted.shape[2]) // 2
        y_sub = y_target[:, :, pad:-pad, pad:-pad]
        loss = self.cross_entropy(y_predicted, y_sub)

        # minimize loss and update weights
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        if log:
            _logger.info("Step: %s,  Loss: %s", self.global_step, loss.item())

            self.tfwriter.add_scalar(
                "loss/cross_entropy", loss, global_step=self.global_step
            )

            grid_inputs = torchvision.utils.make_grid(x_input[:4, [1, 2, 0]])
            grid_labels = torchvision.utils.make_grid(y_sub[:4])
            grid_predictions = torchvision.utils.make_grid(y_predicted[:4])

            self.tfwriter.add_image(
                "inputs", normalize_image(grid_inputs), global_step=self.global_step
            )
            self.tfwriter.add_image("labels", grid_labels, global_step=self.global_step)
            self.tfwriter.add_image(
                "predictions", grid_predictions, global_step=self.global_step
            )

            prediction = y_predicted > 0.5
            correct = torch.sum(prediction == y_sub)
            acc = correct.float() / y_sub.numel()
            self.tfwriter.add_scalar("accuracy", acc, global_step=self.global_step)

            for c in range(0, x_input.shape[1]):
                self.tfwriter.add_histogram(
                    f"inputs/channel_{c+1}", x_input[:, c], global_step=self.global_step
                )

        self.global_step += 1

    def persist_checkpoint(self):
        torch.save(
            {
                "state_dict": self.model.state_dict(),
                "optimizer": self.optimizer.state_dict(),
                "global_step": self.global_step,
            },
            self.checkpoint_filename,
        )

    def load_checkpoint(self):
        if os.path.exists(self.checkpoint_filename):
            checkpoint = torch.load(self.checkpoint_filename)
            _logger.info("checkpoint_file: %s", self.checkpoint_filename)
            self.global_step = checkpoint["global_step"]
            self.model.load_state_dict(checkpoint["state_dict"])
            self.optimizer.load_state_dict(checkpoint["optimizer"])
        else:
            _logger.info("No checkpoint exists yet at %s", self.checkpoint_filename)


def run(
    model,
    persist_directory,
    training_data_directory,
    total_steps=20_000,
    batch_size=32,
    learning_rate=1e-3,
    log_step=100,
    save_step=1_000,
):
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    trainer = Trainer(
        model=model,
        learning_rate=learning_rate,
        batch_size=batch_size,
        persist_directory=persist_directory,
    )
    trainer.model = trainer.model.to(device)
    trainer.load_checkpoint()

    data_generator = data.DataLoader(
        dataloader.get_wildfire_dataset(training_data_directory),
        batch_size=batch_size,
        shuffle=True,
        num_workers=20,
        pin_memory=True,
    )

    while trainer.global_step < total_steps:
        for _, (inputs, labels) in enumerate(data_generator):
            # inputs need to be normalized per band with global mean and std
            log = trainer.global_step % log_step == 0
            trainer.update(inputs.to(device), labels.to(device), log=log)

            if trainer.global_step % save_step == 0:
                trainer.persist_checkpoint()
