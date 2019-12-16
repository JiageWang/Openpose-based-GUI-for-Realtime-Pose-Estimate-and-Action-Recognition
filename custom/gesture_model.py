import cv2
import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.transforms import ToTensor


class Model(nn.Module):
    """
    定义了一个简单的三层全连接神经网络，每一层都是线性的
    """

    def __init__(self, in_dim, n_hidden1, out_dim):
        super().__init__()
        self.layer1 = nn.Linear(in_dim, n_hidden1)
        self.layer2 = nn.Linear(n_hidden1, out_dim)

    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = self.layer2(x)
        return x


class GestureModel(object):
    def __init__(self, path):
        self.gesture_model = self.get_gesture_model(path)
        self.idx_to_gesture = {0: 'eight', 1: 'five', 2: 'handssors', 3: 'normal', 4: 'ten'}
        # self.idx_to_gesture = {0: 'zero', 1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6:'six', 7:'seven', 8:'eight', 9:'nine'}
        self.gesture_threshold = 0.57

    def __call__(self, hand):
        hand = hand[:, :2]
        hand[:, 0] /= 640
        hand[:, 1] /= 480
        hand = ToTensor()(hand)
        if torch.cuda.is_available():
            hand = hand.cuda()
        hand = hand.view(1, -1)
        out = self.gesture_model(hand)
        out = F.softmax(out, 1)
        value, index = torch.max(out, 1)
        if value.item() > self.gesture_threshold:
            return self.idx_to_gesture[index.item()]
        else:
            return None

    @staticmethod
    def get_gesture_model(weights_path):
        model = Model(42, 32, 5)
        if torch.cuda.is_available():
            model.load_state_dict(torch.load(weights_path))
            model = model.cuda()
        else:
            model.load_state_dict(torch.load(weights_path, map_location=lambda storage, loc: storage))
        model.eval()
        return model

    @staticmethod
    def hand_bbox(hand):
        if np.sum(hand[:, 2]) > 21*0.5:
            rect = cv2.boundingRect(np.array(hand[:, :2]))
            return rect
        else:
            return None


def gesture_recognition(self):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result, keypoints = func(*args, **kwargs)
            if self.hand_on and self.setting_widget.gesture_on():
                hands = keypoints[1]
                for hand in hands:
                    gesture = self.gesture_model(hand)
                    x, y, w, h = self.gesture_model.hand_bbox(hand)
                    cv2.rectangle(result, (x, y), (x + w, y + h), (255, 255, 255))
                    cv2.putText(result, gesture, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))
            return result, keypoints
        return wrapper

    return decorator
