# Hello World!
In this tutorial we will submit our first job 🐤! 

## Overview
[runai](https://www.run.ai/) manages workflows on our cluster! `runai`:

- Allocates GPUs
- Runs [Docker](https://www.docker.com/) containers to keep software on the cluster clean!
- Logs status online [kcl.run.ai](http://kcl.run.ai)

> [!NOTE]
> Also refer to the official [runai Documentation](https://docs.run.ai/latest/)

## Getting Started
We will now run our first Docker container through `runai`. We will use the official [hello-world](https://hub.docker.com/_/hello-world) Docker image. This container, will simply print `Hello from Docker!`.

> [!NOTE]
> Make sure you can connect to the cluster: [1-Setup-cluster-connection](../1-Setup-cluster-connection).

> [!TIP]
> Use `--help` to access documentation:
>
> ```shell
> runai submit --help
> ```

`ssh` into the cluster and run:
```shell
runai submit my-first-job -i hello-world -g 0
```

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
