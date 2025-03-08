# RunAI setup & hello world!

In this tutorial we will setup our runai account and submit our first job🐤!

## Configuring RunAI

In this section, we will configure our RunAI project, so we can start running jobs on the cluster.

### Login into RunAI portal

The first time you log into Run.AI, you will need to do it through the [King's RunAI portal](https://kcl.run.ai). Use the password and username that are included in the email you received from IT. It will ask you to change the password, write down this password as it would be the one you will use to setup the project in the cluster. Make sure you do this step first!

### Configuring your project

Once you have the new password, connect to the cluster via `ssh` following the [previous tutorial](../1-Setup-cluster-connection/README.md) with your usual credentials. Once in the cluster execute the following commands:

```shell
runai login
runai config project <project-name>
```

where the project name is the your default project. Following the logic of the previous tutorial it is usually the first letter of your name and your whole surname. So, if *John Doe* has a project in the cluster it will be `jdoe`.

Also, when you run the `runai login` command it will tell you to introduce your `username` which is your King's email and the `password` which is the newly setup one on the previous step. If everything has been done correctly, you should be able to execute the second part of this tutorial.

## What does RunAI do?

[runai](https://www.run.ai/) manages workflows on our cluster! `runai`:

- Allocates GPUs
- Runs [Docker](https://www.docker.com/) containers to keep software on the cluster clean!
- Logs status online [kcl.run.ai](http://kcl.run.ai)

> [!NOTE]
> Also refer to the official [runai Documentation](https://docs.run.ai/latest/)

## Getting started

We will now run our first `Docker` container through `runai`. We will use the
official [hello-world](https://hub.docker.com/_/hello-world) `Docker` image. This container, will simply
print `Hello from Docker!`. To find a more comprehensive guide to creating your own Docker container, go
to [Setup Docker container](../3-Setup-Docker-container/README.md).

> [!NOTE]
> Make sure you can connect to the cluster: [1-Setup-cluster-connection](../1-Setup-cluster-connection).


`ssh` into the cluster and run:

```shell
runai submit my-first-job -i hello-world -g 0
```

Couple of thing to notice

- `-i hello-world` specifies the image we wish to run
- `-g 0` uses **zero** GPUs, hold on cowboy 🤠!

> [!TIP]
> Use `--help` to access documentation:
>
> ```shell
> runai submit --help
> ```

You can now observe the status of your job using

```shell
runai describe job my-first-job
```

To acccess the terminal output of your job, do

```shell
runai logs my-first-job
```

You should see `Hello from Docker!`, success 🎉🎉🎉!

To clean up after, run:

```shell
runai delete job my-first-job
```
