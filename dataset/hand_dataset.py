import os
import numpy as np
from torch.utils.data import Dataset, DataLoader


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
        hands_keypoints = np.load(sample)[:, 0, :, :]
        if np.sum(hands_keypoints[0, :, 2]) > np.sum(hands_keypoints[1, :, 2]):
            hands_keypoints = hands_keypoints[0, :, :2]
        else:
            hands_keypoints = hands_keypoints[1, :, :2]

        hands_keypoints[:, 0] = hands_keypoints[:, 0] / 640
        hands_keypoints[:, 1] = hands_keypoints[:, 1] / 480
        if self.transform:
            hands_keypoints = self.transform(hands_keypoints)

        hand_label = self.class_to_idx[self.samples[item][1]]

        return hands_keypoints, hand_label


if __name__ == "__main__":
    dataset = HandDataset(r"C:\Users\Administrator\Desktop\train")
    dataloader = DataLoader(dataset, 10, shuffle=True)

    for data, label in dataloader:
        data = data.view(data.shape[0], -1)
        print(data.shape)
