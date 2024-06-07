import torch


def make_model(in_size, out_size, num_layers):
    layers = []
    for _ in range(num_layers - 1):
        layers.append(torch.nn.Linear(in_size, in_size))
        layers.append(torch.nn.ReLU())
    layers.append(torch.nn.Linear(in_size, out_size))
    return torch.nn.Sequential(*tuple(layers)).cuda()


if __name__ == '__main__':

    batch_size = 256
    in_size = 4096
    out_size = 4096
    num_layers = 12
    num_batches = 50
    epochs = 3

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    torch.set_default_device(device)

    # Creates data in default precision.
    # You don't need to manually change inputs' ``dtype`` when enabling mixed precision.
    data = [torch.randn(batch_size, in_size) for _ in range(num_batches)]
    targets = [torch.randn(batch_size, out_size) for _ in range(num_batches)]

    loss_fn = torch.nn.MSELoss().cuda()  # not all loss functions will allow you to use mixed precision, but it is
    # defined automatically

    use_amp = True

    net = make_model(in_size, out_size, num_layers)
    opt = torch.optim.SGD(net.parameters(), lr=0.001)
    scaler = torch.cuda.amp.GradScaler(enabled=use_amp)

    for epoch in range(epochs):
        print('Training model')
        for input, target in zip(data, targets):
            with torch.autocast(device_type=device, dtype=torch.float16, enabled=use_amp):
                output = net(input)
                # output is float16 because linear layers ``autocast`` to float16.
                assert output.dtype is torch.float16

                loss = loss_fn(output, target)
                # loss is float32 because ``mse_loss`` layers ``autocast`` to float32.
                assert loss.dtype is torch.float32
                scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
            opt.zero_grad(set_to_none=True)

    print('Successfully finished')
