# DGX cluster guidelines

The most important aspect of fair and effective use of the GPU cluster is to balance and maximize GPU compute
utilization. This is vital, not just for fair usage amongst your colleagues, but also for improving the speed of your
own work. In addition, it would handle the reduction in efficiency inherited from the scheduler and from the
fragmentation of hardware resources, as we have many users running small training sessions on the cluster.

GPU compute utilization refers to the percentage of a GPU's processing power actively used at a given time. This **DOES
NOT** refer specifically to the GPU memory (VRAM)  utilization. The important message is that the higher the GPU compute
utilization, the faster the job will get done. You should be aiming to have >90% compute utilization.

### Check the tutorials at [General code optimization](/3-General-code-optimization/README.md) for how to maximise GPU utilization.

---

## The issue visualized

The below image shows a typical issue on the cluster. Almost all of the 71 gpus are allocated, yet their compute
utilization is 35%. If the average compute utilization were 90% then the exact same workload could be done on just 28
GPUs instead of 71, and they would each be done faster too.

![gpu_utilization.png](assets/gpu_utilization.png)

---

## How to check GPU utilization

There are multiple ways to check your GPU compute utilization, both on your local pc and on the DGX cluster.

### On a local machine

On local machines the following command will show a GPU summary every 1 seconds (The key metric
being `VOLATILE GPU-Util`):

```shell
nvidia-smi -l 1
```

---

### On the DGX cluster

For checking job utilization on the cluster a nice GUI representation is shown via the RunAI dashboard. Simply follow
`Workloads` -> `<your job name>` -> `metrics` -> `GPU compute utilization`

### You can find the workloads in the bar on the left:

![workloads_location1.png](assets/workloads_location1.png)

### You need to then find your job (in this case it is `david-train`) and then click on the `show details` button in the top

right:
![workloads_location2.png](assets/workloads_location2.png)

### Finally under the metrics tab you can see the system resource usage:

![workloads_location3.png](assets/workloads_location3.png)

### Third party alternatives which allow easy tracking and visualization of desired metrics, also automatically monitor resource usage too (Free to use). Such examples are [Weights & Biases](https://wandb.ai/site), [neptune.ai](https://neptune.ai/).

---

