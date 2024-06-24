import os
import tempfile
import warnings

import torch
import torchvision.datasets as datasets
import torchvision.transforms.v2 as transforms
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader
from torch.utils.data.distributed import DistributedSampler


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
    num_epochs = 3
    use_amp = True
    batch_size = 128

    torch.backends.cudnn.benchmark = True
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.autograd.set_detect_anomaly(False)
    torch.autograd.profiler.profile(enabled=False)
    torch.autograd.profiler.emit_nvtx(enabled=False)

    network_dtype = torch.float16 if use_amp else torch.float32

    train_transforms = transforms.Compose([
        transforms.RandomAffine(degrees=15, translate=(0.1, 0.1), scale=(0.9, 1.1), shear=10),
        transforms.ToDtype(dtype=network_dtype, scale=True),
    ])

    ddp_init()
    print0('======= Printing must be performed on Rank 0 when using DDP ======')  # Note the "special" function used
    print0(f'======= DDP example is on rank {get_rank()}')

    training_data = datasets.FashionMNIST(
        root="data",
        train=True,
        download=True,
        transform=transforms.PILToTensor(),
    )

    my_dataloader = DataLoader(
        training_data,
        batch_size=batch_size,
        pin_memory=True,
        shuffle=False,
        sampler=DistributedSampler(training_data)
        # Each gpu gets a subset of the data. https://pytorch.org/docs/stable/data.html#torch.utils.data.Sampler
    )

    model = ExampleModel().to(get_rank(), memory_format=torch.channels_last)  # Sending the model to each GPU

    #  Compiling models is a bit spotty in terms of reliability, so it's recommended to wrap the compile procedure.
    try:
        model = torch.compile(model, mode='max-autotune') #  max-autotone can be very slow, if desired try 'default'
        print0('Successful model compilation, carrying on with training.')
    except Exception as e:
        if get_rank() == 0:
            warnings.warn('Tried and failed to compile pytorch model, continuing in standard mode.')

    ddp_model = DDP(model, device_ids=[get_rank()])  # This is the model that will get optimized

    loss_fn = torch.nn.CrossEntropyLoss().to(get_rank())
    optimizer = torch.optim.SGD(ddp_model.parameters(), lr=1e-4)  # Note: which model parameters are used

    scaler = torch.cuda.amp.GradScaler(enabled=use_amp)
    best_loss = torch.inf
    model_save_path = os.path.join(tempfile.mkdtemp(), 'ddp_model.pth')  # Just a temporary save path (Will be deleted)

    for epoch in range(num_epochs):
        epoch_loss = 0
        with torch.cuda.amp.autocast(dtype=network_dtype, enabled=use_amp):
            for imgs, labels in my_dataloader:
                # Sending data to the respective gpus and using channels last format
                imgs = imgs.to(get_rank(), memory_format=torch.channels_last)

                # Note: Need at least a rank 4 tensor for channels last format. So for using semantic labelmaps, you
                # would be able to use this.
                labels = labels.to(get_rank())

                imgs = train_transforms(imgs)  # Being processed on the gpu

                outputs = ddp_model(imgs)
                loss = loss_fn(outputs, labels)
                epoch_loss += loss.item()

                optimizer.zero_grad(set_to_none=True)
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()

            if get_rank() == 0:  # Only want a single gpu saving the model
                if best_loss > loss.item():  # Best practise says this should be the validation loss, but it's a tutorial.
                    best_loss = loss.item()
                    torch.save(ddp_model.module.state_dict(), model_save_path)

        print0(f'Epoch {epoch} loss: {epoch_loss / len(my_dataloader)}')

    print0(f'Finished training and now showing how loading the model works')

    del model, ddp_model  # Making sure we aren't just using weights already in memory
    torch.distributed.barrier()  # Makes all the gpus wait until they reach here
    if get_rank() == 0:  # Only want a single gpu saving and loading the model
        print0('Initializing fresh model')
        model = ExampleModel().to(get_rank())
        ddp_model = DDP(model, device_ids=[get_rank()])

        print0('Now loading model')

        #  When training, the DDP models have an added attribute 'module' which would need to be removed using the below
        #  line of code if you want to run a loaded model.
        #  When loading, you want the map_location to be 'cpu' so that it can be sent out to all the gpus afterwards.
        state_dict = torch.load(model_save_path, map_location='cpu')
        ddp_model = ddp_model.module if hasattr(ddp_model, "module") else ddp_model
        remove_prefix = '_orig_mod.'
        state_dict = {k[len(remove_prefix):] if k.startswith(remove_prefix) else k: v for k, v in state_dict.items()}

        ddp_model.load_state_dict(state_dict)

        os.remove(model_save_path)  # Removing the temporary save folder

    print0('====== DDP example has successfully been completed')
    torch.distributed.destroy_process_group()  # To properly end the DDP process


if __name__ == "__main__":
    main()
