# How to optimize GPU utilization

This tutorial covers the basic concepts for achieving maximum GPU compute utilization during deep learning training.
This can be achieved in a number of ways, and can be broadly broken down into a few broad categories.

---

## 1. Make the most of the PyTorch dataloader:

> [!NOTE]
> In rare cases, some of these options may produce slightly worse speed. It is best to do a few timed epochs as a sanity
> check to see training rate before and after these changes.


The built-in PyTorch
dataloader, [torch.utils.data.DataLoader](https://pytorch.org/docs/stable/data.html#torch.utils.data.DataLoader), has a
number of arguments you can define in order to improve the throughput of data being loaded.

This includes:

- Setting `batch_size` to as high as possible before reaching an OOM error (VRAM too full to fit all data). This
  maximizes the time the GPU spends on performing computations before having to wait for more data to be loaded.
- Setting `num_workers` > 0 to use multiple cpu cores for loading data. This is to minimize the time spent by the GPU
  waiting idly for the CPU to transfer data to it for processing. You must use the `--cpu-limit` option when launching
  in runai to not overload the system.
- Raising value of `prefetch_factor`.
- Setting `pin_memory=True`.
- Setting `persistent_workers=True`.

A good default dataloader may look like this:

```python
from torch.utils.data import DataLoader

my_dataloader = DataLoader(my_dataset,
                           batch_size=my_max_batchsize,
                           num_workers=my_max_cpu_count,  # Must use with --cpu-limit option in the runai command
                           prefetch_factor=4,
                           pin_memory=True,
                           persistent_workers=True)
```

---

## 2. No brainer code tweaks

There are a number of easy changes you can use to greatly improve training speed of your models, while changing
absolutely nothing about how your network trains/ how you debug. The recommendation would be to always aim to use these
suggested options.

These include:

- Using `model.zero_grad(set_to_none=True)` instead of `model.zero_grad()`
- Disable bias for convolutions directly followed by a batch norm i.e. `torch.nn.Conv2d(..., bias=False, ....)`
- Using `torch.backends.cudnn.benchmark = True` to automatically find the fastest convolution algorithm.
- Create tensors directly on the target device e.g. Instead of calling `torch.rand(size).cuda()` instead
  use `torch.rand(size, device='cuda')`
- Setting `torch.backends.cuda.matmul.allow_tf32 = True` and `torch.backends.cudnn.allow_tf32 = True`. This allows
  PyTorch to use the tensor processing cores on newer GPU architectures for matrix multiplication and convolutions.
- Disabling gradient calculation for validation or inference using `torch.no_grad()`. Typically, gradients aren’t needed
  for validation or inference. As a rule of thumb, if you do not need to backpropagate your loss, you can usually disable
  it. When using this function, you can decide on how to use it depending on your needs. If you do not need the gradient
  tracking for the entire function, think about wrapping the function in the decorator:
-

```python
@torch.no_grad()
def evaluate(model, dataloader):
# Your code here
```

On the other hand, if you just need to stop the gradient calculation in a specific section of the code use it under
the `with` operator:

-

```python
def my_function(model, dataloader):
    # Your code with gradient

    with torch.no_grad():
# Code with no gradient tracking

# Gradient calculation is back on
```

- Consider replacing a manual implementation of the attention mechanism
  with `torch.nn.functional.scaled_dot_product_attention`. It calculates exactly the same thing but uses tricks under
  the
  hood to perform a much more efficient calculation, while better utilizing your hardware.

---

## 3. Code tweaks to think about

There are also a number of code tweaks which you can implement cautiously.

These include:

- Using `torch.nn.parallel.DistributedDataParallel` instead of `torch.nn.DataParallel`. This is recommended best
   practice by PyTorch themselves and offers much better performance/scaling. A simple example of how to
  use `torch.nn.parallel.DistributedDataParallel` is shown in [`ddp_example.py`](example_code/ddp_example.py). Further
  documentation can be
  found [here](https://pytorch.org/docs/stable/generated/torch.nn.parallel.DistributedDataParallel.html#torch.nn.parallel.DistributedDataParallel).
  You can also initialize this type of training with Elastic Launch using the *torchrun*. You can find the
  documentation and how to use `torchrun` in [here](https://pytorch.org/docs/stable/elastic/run.html). In addition,
  there is an official beginner tutorial on Distributed
  Training [here](https://pytorch.org/tutorials/beginner/ddp_series_fault_tolerance.html).

- Performing data augmentations on the gpu, instead of the cpu. By default, PyTorch will perform the selected data
  augmentations on the cpu instead of the gpu, and this is a particular performance drain for computationally expensive
  augmentations e.g. warping 3d data. The data can be moved to the GPU, and a custom augmentation function can be coded
  using PyTorch to then automatically perform the computation on the gpu. A simple example of how to perform GPU-based
  data augmentations can be found in `gpu_data_augmentations.py`.
- Enabling channels_last memory format for vision models if there are no hard coded operations on exact tensor
  dimensions in your code e.g. `my_data = my_data.to(memory_format=torch.channels_last)`. Take care to also make sure
  that your model is also in the same channels format e.g. `my_model = my_model.to(memory_format=torch.channels_last)`.
  Further details can be found [here](https://pytorch.org/tutorials/intermediate/memory_format_tutorial.html).
- Disabling debugging APIs. When you are finished coding/debuggin a model, you don't need all the background activity of
  PyTorch checking everything is ok for debugging purposes. These options can be disabled
  using `torch.autograd.set_detect_anomaly(False)`, `torch.autograd.profiler.profile(enabled=False)`
  and `torch.autograd.profiler.emit_nvtx(enabled=False)`.
- Using torch automatic mixed precision. Most models can train/inference perfectly well in a reduced level of numerical
  precision, in theory, doubling your compute speed while halving your memory consumption. Care should be taken to make
  sure your model is stable before relying fully on automatic mixed precision. It can be used as a context manager
  e.g. `with torch.autocast(device_type="cuda"):`. A simple example of how to automatic mixed precision is shown
  in `amp_example.py`. Further documention can be found [here](https://pytorch.org/docs/stable/amp.html#torch.autocast).
- Trying to compile your PyTorch model when you are finished debugging. This is often prone to failure and should be
  wrapped in a try statement; however, it can greatly improve speed. It can
  be initiated using `my_model = torch.compile(my_model)`. This only works on `torch >= 2.0.0`.

---

# Putting it all together

A barebones example template script using all the recommendations can be found in `simple_example.py`. Another script
based upon `simple_recommendations_example.py` which has some more complexity added for better quality of life
is `fancy_recommendations_example.py`
