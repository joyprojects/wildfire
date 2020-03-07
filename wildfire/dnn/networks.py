import torch
import torch.nn as nn

class BasicCNNClassifier(nn.Module):
    def __init__(self, input_dim):
        super(BasicCNNClassifier, self).__init__()
        self.model = nn.Sequential(nn.Conv2d(input_dim, 16, 3, padding=1, stride=1),
                                   nn.ReLU(),
                                   nn.Conv2d(16, 8, 1, padding=0, stride=1),
                                   nn.ReLU(),
                                   nn.Conv2d(8, 1, 3, padding=1, stride=1),
                                  nn.Sigmoid())

    def forward(self, x):
        return self.model(x)
