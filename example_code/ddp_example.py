import os
import tempfile

import torch
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader
from torch.utils.data.distributed import DistributedSampler
from torchvision import datasets
from torchvision.transforms import transforms


class ExampleModel(torch.nn.Module):
    def __init__(self):
        super(ExampleModel, self).__init__()
        self.net1 = torch.nn.Linear(784, 10)
        self.relu = torch.nn.ReLU()

    def forward(self, x):
        x = torch.flatten(x, start_dim=1)
        x = self.net1(x)
        x = self.relu(x)
        return x


def ddp_init():
    """
    Initialize the distributed data parallel with the relevant information needed.
    This has been verified to work on the KCL dgx cluster.
    :return:
    """

    if 'MASTER_ADDR' not in os.environ:
        os.environ['MASTER_ADDR'] = 'localhost'
    if 'MASTER_PORT' not in os.environ:
        os.environ['MASTER_PORT'] = '1234'
    if 'RANK' not in os.environ:
        os.environ['RANK'] = '0'
    if 'LOCAL_RANK' not in os.environ:
        os.environ['LOCAL_RANK'] = '0'
    if 'WORLD_SIZE' not in os.environ:
        os.environ['WORLD_SIZE'] = '1'

    backend = 'gloo' if os.name == 'nt' else 'nccl'
    torch.distributed.init_process_group(backend=backend, init_method='env://')
    torch.cuda.set_device(int(os.environ.get('LOCAL_RANK', '0')))


def get_rank():
    """
    Simple function to get the rank of the current process.
    """
    return torch.distributed.get_rank() if torch.distributed.is_initialized() else 0


def print0(*args, **kwargs):
    """
    A simple wrapper around print for distributed training. E.g., print0('any standard print message you want')
    """

    if get_rank() == 0:
        print(*args, **kwargs)


def main():
    ddp_init()
    print0(
        '======= To get a printout when using distributed training you need to make sure that it is performed on rank 0.')
    print0(f'======= DDP example is on rank {get_rank()}')

    training_data = datasets.FashionMNIST(
        root="data",
        train=True,
        download=True,
        transform=transforms.ToTensor()
    )

    my_dataloader = DataLoader(
        training_data,
        batch_size=32,
        pin_memory=True,
        shuffle=False,  # This must be False as the sampler is doing that job
        sampler=DistributedSampler(training_data)
        # Must use this to so each gpu gets a subset of the data. https://pytorch.org/docs/stable/data.html#torch.utils.data.Sampler
    )

    model = ExampleModel().to(get_rank())  # sending the model to each GPU
    ddp_model = DDP(model, device_ids=[get_rank()])  # This is the model that will get optimized

    loss_fn = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(ddp_model.parameters(), lr=1e-3)

    optimizer.zero_grad(set_to_none=True)

    best_loss = torch.inf
    model_save_path = os.path.join(tempfile.mkdtemp(), 'ddp_model.pth')  # just a temporary save path (Will be deleted)

    for epoch in range(3):
        epoch_loss = 0
        for imgs, labels in my_dataloader:
            imgs, labels = imgs.to(get_rank()), labels.to(get_rank())  # sending selected data to the respective gpus

            outputs = ddp_model(imgs)
            loss = loss_fn(outputs, labels)
            epoch_loss += loss.item()

            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()

        if best_loss > loss.item():
            best_loss = loss.item()
            torch.save(ddp_model.module.state_dict(), model_save_path)

        print0(f'Epoch {epoch} loss: {epoch_loss / len(my_dataloader)}')

    print0(f'Finished training and now showing how loading the model works')

    del model, ddp_model  # Making sure we aren't just using weights already in memory

    print0('Initializing fresh model')
    model = ExampleModel().to(get_rank())
    ddp_model = DDP(model, device_ids=[get_rank()])

    print0('Now loading model')

    #  When training, the DDP models have an added attribute 'module' which would need to be removed using the below
    #  line of code if you want to run a loaded model.
    ddp_model = ddp_model.module if hasattr(ddp_model, "module") else ddp_model

    #  When loading, you want the map_location to be 'cpu' so that it can then be sent out to all the gpus afterwards.
    ddp_model.load_state_dict(torch.load(model_save_path, map_location='cpu'))
    os.remove(model_save_path)  # Removing the temporary save folder

    print0('====== DDP example has successfully been completed')
    torch.distributed.destroy_process_group()  # To properly end the DDP process


if __name__ == "__main__":
    main()
