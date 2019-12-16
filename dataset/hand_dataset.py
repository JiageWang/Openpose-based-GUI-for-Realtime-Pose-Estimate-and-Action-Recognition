import os
import random
import numpy as np
from torch.utils.data import Dataset, DataLoader


class HandDataset(Dataset):
    def __init__(self, path, transform=None, train=True, train_percent=0.7):
        super().__init__()
        random.seed(10)
        self.root = path
        self.transform = transform
        self.is_trian = train
        self.train_percent = train_percent
        self.class_to_idx = self._find_classes()
        self.train_samples, self.valid_samples = self._make_samples()

    def _make_samples(self):
        train_samples = []
        valid_samples = []
        for folder in os.listdir(self.root):
            for npy in os.listdir(os.path.join(self.root, folder, "hand")):
                npy_file = os.path.join(self.root, folder, "hand", npy)
                if random.random() < self.train_percent:
                    train_samples.append((npy_file, folder))
                else:
                    valid_samples.append((npy_file, folder))

        return train_samples, valid_samples

    def _find_classes(self):
        classes = [d for d in os.listdir(self.root) if os.path.isdir(os.path.join(self.root, d))]
        classes.sort()
        class_to_idx = {classes[i]: i for i in range(len(classes))}
        return class_to_idx

    def __len__(self):
        if self.is_trian:
            return len(self.train_samples)
        else:
            return len(self.valid_samples)

    def __getitem__(self, item):
        if self.is_trian:
            sample = self.train_samples[item][0]
            hand_label = self.class_to_idx[self.train_samples[item][1]]
        else:
            sample = self.valid_samples[item][0]
            hand_label = self.class_to_idx[self.valid_samples[item][1]]
        hands_keypoints = np.load(sample)[:, 0, :, :]

        # 单手
        # if np.sum(hands_keypoints[0, :, 2]) > np.sum(hands_keypoints[1, :, 2]):
        #     hands_keypoints = hands_keypoints[0, :, :2]
        # else:
        #     hands_keypoints = hands_keypoints[1, :, :2]

        # 双手
        if random.random()>0.5:
            hands_keypoints = hands_keypoints[0, :, :2]
        else:
            hands_keypoints = hands_keypoints[1, :, :2]

        hands_keypoints[:, 0] = hands_keypoints[:, 0] / 640
        hands_keypoints[:, 1] = hands_keypoints[:, 1] / 480
        if self.transform:
            hands_keypoints = self.transform(hands_keypoints)

        return hands_keypoints, hand_label

    @property
    def num_classes(self):
        return len(self.class_to_idx)


if __name__ == "__main__":
    dataset1 = HandDataset(r"E:\BaiduNetdiskDownload\dataset", train=True)
    dataset2 = HandDataset(r"E:\BaiduNetdiskDownload\dataset", train=False)
    dataloader1 = DataLoader(dataset1, 1, shuffle=True)
    dataloader2 = DataLoader(dataset2, 1, shuffle=True)
    print(next(iter(dataloader1)))
    print(next(iter(dataloader2)))
