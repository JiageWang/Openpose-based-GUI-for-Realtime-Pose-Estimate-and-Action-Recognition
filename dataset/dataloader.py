import os
import sys

import cv2
import numpy as np
import torch
from torchvision.datasets import ImageFolder
from torch.utils.data import Dataset, DataLoader

class_to_idx = {"normal": 0}


class HandDataset(Dataset):
    def __init__(self, path, transform=None):
        super().__init__()
        self.root = path
        self.transform = transform
        self.class_to_idx = self._find_classes()
        self.samples = self._make_samples()

    def _make_samples(self):
        samples = []
        for folder in os.listdir(self.root):
            for npy in os.listdir(os.path.join(self.root, folder, "hand")):
                npy_file = os.path.join(self.root, folder, "hand", npy)
                samples.append((npy_file, folder))
        return samples

    def _find_classes(self):
        classes = [d for d in os.listdir(self.root) if os.path.isdir(os.path.join(self.root, d))]
        classes.sort()
        class_to_idx = {classes[i]: i for i in range(len(classes))}
        return class_to_idx

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, item):
        sample = self.samples[item][0]
        data = np.load(sample)[:, 0, :, :]
        if np.sum(data[0, :, 2]) > np.sum(data[1, :, 2]):
            data = data[0, :, :2]
        else:
            data = data[1, :, :2]

        # # 数据增强
        # x_min = data[:, 0].min()
        # y_min = data[:, 1].min()
        # x_move = np.random.randint(int(x_min))
        # y_move = np.random.randint(int(y_min))

        data[:, 0] = data[:, 0] / 640
        data[:, 1] = data[:, 1] / 480
        if self.transform:
            data = self.transform(data)

        label = self.class_to_idx[self.samples[item][1]]

        return data, label


if __name__ == "__main__":
    dataset = HandDataset(r"C:\Users\Administrator\Desktop\train")
    dataloader = DataLoader(dataset, 10, shuffle=True)

    for data, label in dataloader:
        data = data.view(data.shape[0], -1)
        print(data.shape)
