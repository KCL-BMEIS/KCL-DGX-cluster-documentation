# Cluster connection

This first tutorial covers the basic concepts to connect to the cluster for the first time and the steps to configure your *runai* project.

## A few things to consider before starting

When you are trying to access any system in the *KCL network*, you are required to be connected to the School's network via Ethernet cable. This means that trying to make a direct connection via `ssh` with a computer outside the school network will require a *bouncer* account inside the School's network. If you are planning to connect to the cluster or your school system outside the school, you must ask IT for a bouncer account.

> **BOUNCER:** To ask for a bouncer account you should send an email to [*bmeis-it@kcl.ac.uk*](mailto:bmeis-it@kcl.ac.uk). Don't forget to CC your supervisor in the email. Your bouncer account should have the following structure `<bouncer-user>@bouncer.isd.kcl.ac.uk`, where `<bouncer-user>` is usually formed by the first character of your name and surname and the year the account was created. For example, if **John Doe** ask for an account in **2024**, his username will be **jd24**.


## Connecting for the first time

The first time you connect to the cluster, you should connect to an specific node. This first connection requires you to change the temporary password and it is very important to follow the steps precisely, as failing to do so will require waiting longer for an account reset.

1. Connect to the *headnode1* in the cluster. To do so, open a terminal and run the following command:
```shell
ssh <cluster-user>@h1.isd.kcl.ac.uk
```
Note: If you are outside the School you will need the bouncer to connect to the cluster through a Proxy.
```shell
ssh -J <bouncer-user>@bouncer.isd.kcl.ac.uk <cluster-user>@h1.isd.kcl.ac.uk
```

Once you enter the temporary password for the first time, the program will ask you to write a new permanent password. Remember this password as it is the one we will use for now for the next steps.


## Configuring future and passworldless connections

### Creating the config file

All the files related to *openssh* are located in the folder `${HOME}/.ssh` for both Linux and Windows OS. The most important file inside this folder is the `config` file. This file contains the information of different hosts and the options we want to use when connecting to them. If the file does not exist we can create this file using a text editor such as `nano`, `vim`, `touch` or your common IDE. A common *config* file with the necessary options to establish the connection with the *aicheadnode* can be found in [here](config). If you are using this sample file, remember to substitute the missing parts with your username for both the bouncer and the aicheadnode.


### Generating ssh key pairs

One of the most interesting things with *openssh* is that we can use keys to identify ourselves when we are trying to initialize a connection with a remote system. In this way we do not need to use the password every time as the host will automatically identify us as a known user. If you want to know more about **ssh keys** you can read a basic introduction in [here](https://www.ssh.com/academy/ssh-keys). The steps to generate the keys are very simple and similar in both Linux and Windows. We just need to run the following commands on the terminal:

```shell
ssh-keygen
```

Note that by default `openssh` will create a pair of *rsa keys* with the name `id_rsa`, unless specified in the config file. It will use this pair to establish the connection with the remote host. For your first experience with the cluster, we recommend keeping the key file name to default, as we are working in the local School network.


### Stablishing the passworldless connection

Now that we have our pair of keys we need to copy our id into the clusters `authorized-keys` file, so it can identify our system without needing a password. Depending on your OS, the commands you will use will be different:

> **Linux**: To copy your identity file in Linux the procedure is straightforward. As we kept the original name for the keys, open a terminal and run the command below: 

```shell
ssh-copy-id -i ~/.ssh/id_rsa.pub aicheadnode
```

> **Windows**: In Windows the command `ssh-copy-id` does not exist, therefore we need to write the command from scratch. This command basically appends the key to the `authorized-keys` file on the remote system. Therefore, the solution for Windows using a Powershell command line is:

```shell
cat ~/.ssh/id_rsa.pub | ssh aicheadnode "cat >> ~/.ssh/authorized_keys"
```

### Testing the connection and troubleshooting

Finally, you can test the passwordless connection by connecting to the cluster via `ssh` command as follows:

```shell
ssh aicheadnode
```

Congratulations! You can now access the cluster without any passwords, as we are an authorized user on the host. Remember that if **you change your keys, you will need to repeat this process.**

Sometimes if we are outside the School's network, we may be asked for the password of our bouncer account. To solve this problem repeat the previous steps to copy the public key onto the bouncers `authorized-keys` file and we will be granted passwordless access even under the proxy connection.
