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

## Fair use of CPU resources

Run:ai is designed to allocated GPU resources fairly, but CPU resources are not managed in the same way. It is up to 
users to submit jobs with appropriate limits on CPU and CPU memory resources. A single job can use up the available 
resources on a node and prevent all the other jobs from running, even if the GPU resources are available.

Use the [--cpu-limit](https://docs.run.ai/v2.16/Researcher/cli-reference/runai-submit/#-cpu-limit-double) 
and [--memory-limit](https://docs.run.ai/v2.16/Researcher/cli-reference/runai-submit/#-memory-limit-string) flags in 
your `runai submit` command to set these limits. As a rule of thumb, divide the CPU and memory resources of the node by 
the number of GPUs and set your limits according to how many GPUs you requested.

Occasionally, you may need to run a CPU-only job on the server. Keep an eye on the general usage on the cluster and on 
the node you are using and adjust your limits. It may help to break your processing into separate jobs; that way you can 
submit as many as the node can handle and wait until they complete before submitting more.

### Memory leaks

In the Run:ai interface, monitor the CPU memory usage of your job. These appear in the "Metrics" charts shown above, 
below the GPU metrics. If the memory use is climbing monotonically, you 
have a memory leak. This job risks crashing by running out of memory, being killed by the system, or even bringing down 
the node it is running on. The `--memory-limit` flag should at least limit the consequences to the job itself. If you 
see this happening, inspect your code for steps where memory use can accumulate (e.g. objects growing inside a loop). 
Try clearing those variables once they are no longer needed. Using the garbage collector in Python might help.

## Fair use of disk storage

Storage on the `/nfs` storage device is limited and frequently close to full. Please minimise your use of storage. The 
following guidelines should help:

* Avoid duplicating files.
  * If you need to reorganise or rename files for a specific use, consider using links instead of copies.
* Do not store working / temporary files.
  * Either delete these or, better still, process files inside your Docker container so they disappear when the job ends.
* Regularly clean up.
  * Do you really need `run3_final`, `run3_final_final`, `run3_final_final_final`?
* Compress when you can.
  * The `/nfs` storage has compression built in, but explicit compression still saves space.
  * Archiving a set of thousands of tiny files to a `.tar.gz` can reduce the overhead beyond just total size used.
* Use a project directory, not your home directory.
  * This avoids each team member having their own copies of the same files.
  * If you "get hit by a bus", having your work organised with the intent of sharing it will make it easier for your
colleagues to pick up where you left off.
* Consider archiving large datasets.
  * If you are no longer using a specific dataset, consider moving it off `/nfs`.

## Fair use of disk I/O

The entire cluster runs on a single storage system. If too many processes are trying to read and write from the disk at 
once then the system will slow down for everyone. Try to optimise your code to avoid repeated reads from the same file. 
Some modules / data loaders will allow you to explicitly cache data in memory.

This is where we enter slightly controversial territory. Some sysadmins have observed that VScode and possibly Pycharm 
spawn hundreds of background processes, some of which are constantly checking the filesystem for changes. It has been 
reported that adding a script to delete `.vscode` processes improved IO performances. Moreover before this change was 
made, after a system reboot performance was seen to drop as more instances of VScode were launched. Here are some 
suggestions that might minimise this impact:

* Do not leave projects open if you are not working on them.
* Consider running your VScode / Pycharm host on the server inside a Run:ai job rather than directly on the headnode.
  * If you are not sure where your remote host is running, it is probably on the headnode. 
* Consider mounting `/nfs` with sshfs instead of connecting to a VScode / Pycharm host.
  * This also risks overuse of disk IO but Pycharm at least seems to be aware when it is on a network volume and might 
reduce its polling frequency.
* Consider using a local copy of your project for development and syncing changes to the cluster via git / Github / Gitlab.
  * This is possibly the least convenient point, but it completely avoids using the cluster storage for development.
  * Also, it is good discipline to know how to code using git.
  * You can still do small debugging steps locally, especially if your local machine has a GPU.
