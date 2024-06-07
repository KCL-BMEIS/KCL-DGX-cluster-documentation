import torch
import torchvision.transforms.v2 as transforms
from torch.utils.data import DataLoader
from torchvision import datasets


class ExampleModel(torch.nn.Module):
    def __init__(self):
        super(ExampleModel, self).__init__()
        self.net1 = torch.nn.Linear(784, 128)
        self.relu = torch.nn.ReLU()

    def forward(self, x):
        x = torch.flatten(x, start_dim=1)
        x = self.net1(x)
        x = self.relu(x)
        return x


class CustomGaussianBlur(object):
    """ Simple wrapping function around standard Gaussian Blurr to print out the device which is being used

    """

    def __init__(self, kernel_size):
        assert isinstance(kernel_size, (int, tuple))
        self.kernel_size = kernel_size

    def __call__(self, image):
        image = transforms.functional.gaussian_blur(image, [self.kernel_size, self.kernel_size])
        print(f'Performing gaussian blur on {image.device}')
        return image


def main():
    epochs = 3
    batch_size = 1024

    training_data = datasets.FashionMNIST(
        root="data",
        train=True,
        download=True,
        transform=transforms.ToTensor(),  # must call this first to get data in format that dataloader can handle

    )

    my_dataloader = DataLoader(
        training_data,
        batch_size=batch_size,
        pin_memory=True,
        shuffle=False,
        num_workers=0,
    )

    train_transforms = transforms.Compose([
        CustomGaussianBlur(11),  # a simple function which prints out the device that is performing the gaussian blur
    ])

    model = ExampleModel().to('cuda')

    loss_fn = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=1e-3)

    optimizer.zero_grad(set_to_none=True)

    opt = torch.optim.SGD(model.parameters(), lr=0.001)

    for epoch in range(epochs):
        print(f'Epoch {epoch}/{epochs}')
        for idx, (data_batch, target) in enumerate(my_dataloader):
            data_batch, target = data_batch.to('cuda'), target.to('cuda')

            data_batch = train_transforms(data_batch)  # this is where the gaussian blur is being performed (on the gpu)

            output = model(data_batch)
            loss = loss_fn(output, target)

            loss.backward()
        opt.step()
        opt.zero_grad(set_to_none=True)


if __name__ == "__main__":
    main()
