import os

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
    '''
    Initialize the distributed data parallel with the relevant information needed. This has been verified to work on the KCL dgx cluster.
    :return:
    '''

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
    '''
    Simple function to get the rank of the current process.
    '''
    return torch.distributed.get_rank() if torch.distributed.is_initialized() else 0


def print0(*args, **kwargs):
    '''
    A simple wrapper around print for distributed training. e.g. print0('any standard print message you want')
    '''

    if get_rank() == 0:
        print(*args, **kwargs)


def main():
    ddp_init()
    print0('======= To get a printout when using distributed training you need to make sure that it is performed on rank 0.')
    print0(f'====== DDP example is on rank {get_rank()}')

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
        shuffle=False,
        sampler=DistributedSampler(training_data)
        # You need to use this to make sure each gpu gets a subset of the data. Read more at https://pytorch.org/docs/stable/data.html#torch.utils.data.Sampler
    )

    model = ExampleModel().to(get_rank())  # sending the model to each GPU
    ddp_model = DDP(model, device_ids=[get_rank()])  # This is the model that will get optimized

    loss_fn = torch.nn.MSELoss()
    optimizer = torch.optim.SGD(ddp_model.parameters(), lr=1e-3)

    optimizer.zero_grad(set_to_none=True)

    single_batch_imgs, single_batch_labels = next(iter(my_dataloader))
    single_batch_imgs, single_batch_labels = single_batch_imgs.to(get_rank()), single_batch_labels.to(
        get_rank())  # sending selected data to respective gpus

    single_batch_labels = torch.nn.functional.one_hot(single_batch_labels, num_classes=10).to(get_rank())

    outputs = ddp_model(single_batch_imgs)

    loss_fn(outputs, single_batch_labels.float()).backward()
    optimizer.step()

    torch.distributed.destroy_process_group()

    print0('====== DDP example has successfully been completed')


if __name__ == "__main__":
    main()
