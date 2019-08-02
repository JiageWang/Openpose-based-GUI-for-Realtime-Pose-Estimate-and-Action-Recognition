import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from tensorboardX import SummaryWriter

from dataset.hand_dataset import HandDataset


class Model(nn.Module):
    """
    定义了一个简单的三层全连接神经网络，每一层都是线性的
    """

    def __init__(self, in_dim, n_hidden1, out_dim):
        super().__init__()
        self.layer1 = nn.Linear(in_dim, n_hidden1)
        self.layer2 = nn.Linear(n_hidden1, out_dim)

    def forward(self, x):
        # x = self.layer1(x)
        # x = F.relu(x)
        # x = self.layer2(x)
        # x = F.relu(x)
        # x = self.layer3(x)
        x = F.relu(self.layer1(x))
        x = self.layer2(x)
        return x


def valid(epoch):
    global best_valid_acc
    global model
    model = model.eval()
    num_correct = 0
    for inputs, targets in test_dataloader:
        # 前向传播
        inputs, targets = inputs.cuda(), targets.cuda()
        inputs = inputs.view(inputs.shape[0], -1)
        outputs = model(inputs)
        # print(outputs)
        # 统计正确个数
        _, preds = torch.max(outputs.data, 1)
        num_correct += torch.sum(preds == targets.data).item()
    acc_epoch = num_correct / len(test_dataset)
    writer.add_scalar("test_acc", acc_epoch, epoch)
    print('test_acc : %.4f' % acc_epoch)
    # 保存模型
    if acc_epoch > 0.8 and acc_epoch > best_valid_acc:
        torch.save(model.state_dict(), 'model@acc%.3f.pth' % acc_epoch)
        best_valid_acc = acc_epoch


def train(epoch):
    global model
    model = model.train()
    num_correct = 0
    total_loss = 0
    for inputs, targets in train_dataloader:
        # 前向传播
        inputs, targets = inputs.cuda(), targets.cuda()
        inputs = inputs.view(inputs.shape[0], -1)
        outputs = model(inputs)
        # 计算损失
        loss = criterion(outputs, targets)
        total_loss += loss.item() * inputs.size(0)
        # 统计正确个数
        _, preds = torch.max(outputs.data, 1)
        num_correct += torch.sum(preds == targets.data).item()
        # 优化
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    loss_epoch = total_loss / len(train_dataloader)
    writer.add_scalar("train_loss", loss_epoch, epoch)
    acc_epoch = num_correct / len(train_dataset)
    writer.add_scalar("train_acc", acc_epoch, epoch)
    print('loss : %.4f | train_acc : %.4f' % (loss_epoch, acc_epoch), end=" | ")


def inference():
    global model
    model.load_state_dict(torch.load("model@acc0.909.pth"))
    model = model.eval()
    for inputs, targets in test_dataloader:
        # 前向传播
        inputs, targets = inputs.cuda(), targets.cuda()
        inputs = inputs.view(inputs.shape[0], -1)
        outputs = model(inputs)
        print(torch.max(outputs, 1)[1])
        print(targets)


if __name__ == "__main__":
    model = Model(42, 28, 4)
    model = model.cuda()
    for layer in model.modules():
        if isinstance(layer, nn.Linear):
            torch.nn.init.normal_(layer.weight.data, 0, 0.5)

    train_dataset = HandDataset(r"C:\Users\Administrator\Desktop\train")
    train_dataloader = DataLoader(train_dataset, 10, shuffle=True)
    test_dataset = HandDataset(r"C:\Users\Administrator\Desktop\test")
    test_dataloader = DataLoader(test_dataset, 10, shuffle=True)
    optimizer = torch.optim.SGD(model.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()
    writer = SummaryWriter("logs/")
    best_valid_acc = 0

    for i in range(10000):
        print("epoch ", i, end=" | ")
        train(i)
        valid(i)

    # inference()
