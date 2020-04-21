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

    
class BiggerCNNClassifier(nn.Module):
    def __init__(self, input_dim):
        super(BiggerCNNClassifier, self).__init__()
        self.model = nn.Sequential(nn.Conv2d(input_dim, 512, 5, padding=0, stride=1),
                                   nn.ReLU(),
                                   nn.Dropout(p=0.25),
                                   nn.Conv2d(512, 512, 3, padding=0, stride=1),
                                   nn.ReLU(),
                                   nn.Dropout(p=0.25),
                                   nn.Conv2d(512, 1, 3, padding=0, stride=1),
                                   nn.Sigmoid())

    def forward(self, x):
        return self.model(x)
