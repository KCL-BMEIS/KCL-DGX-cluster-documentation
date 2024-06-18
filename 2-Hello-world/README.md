# Hello World!

In this tutorial we will submit our first job🐤!

## Overview

[runai](https://www.run.ai/) manages workflows on our cluster! `runai`:

- Allocates GPUs
- Runs [Docker](https://www.docker.com/) containers to keep software on the cluster clean!
- Logs status online [kcl.run.ai](http://kcl.run.ai)

> [!NOTE]
> Also refer to the official [runai Documentation](https://docs.run.ai/latest/)

## Getting Started

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
