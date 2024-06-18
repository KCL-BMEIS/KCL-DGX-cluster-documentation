# RunAI Centre DGX Cluster - School of BMEIS

## Introduction

> [!WARNING]
> This cluster is **`ONLY`** for KCL BMEIS members. Non-members will not be granted
access, for any reason.

The School of BMEIS AI cluster is a system made of the following components:

* 3 x Dell PowerEdge headnodes running Ubuntu (currently 20.04)
* 2 x Nvidia DGX2 work nodes with 16 GPUs each
* 4 x Nvidia DGX A100 worker nodes with 8 GPUs each
* A NetApp AFF800 all-flash storage with 512TB of space

The DGX1, DGX2 and NetApp AFF8000 are 3+ years old (as of December 2022) and out of support, but they are still working
fine.
The 4 DGX A100 nodes are new and will be supported for 5 years.

The job scheduler is RunAI, a submission system based on Kubernetes, which is a system for deploying and managing
containerised applications.

Users wanting to use the cluster and submit jobs need to access one of the headnodes via ssh. To do this, new starters
need an account on the cluster. This can be requested by their supervisors sending an email to `isd-it@kcl.ac.uk` or to
`isd-helpdesk@kcl.ac.uk`.

---

## Users of the cluster must follow the recommended guidelines described in [DGX_fair_use_guidelines.md](./DGX_fair_use_guidelines.md)

---

## Tutorials

1. [Setup Cluster Connection](1-Setup-cluster-connection/README.md)

   This tutorial covers the basic about the ssh connection with the cluster. Internal and external device connections
   are considered, using a bouncer. It helps to stablish a passwordless authentication using ssh-keys.

2. [Hello World!](2-Hello-world/README.md)

   This tutorial lets you run your first job on the cluster through runai!

3. [Setup Docker container](3-Setup-Docker-container/README.md)

   This tutorial explains the creation of custom Docker containers.

4. [General code optimization](4-General-code-optimization/README.md)

   This is for tutorials which show how to best utilize the cluster.

## Setting Up the Environment for RunAI

After logging in to the cluster headnode for the first time, you'll need to configure the environment for the RunAI
scheduler. Here are the commands:

```
runai login -> When prompted, authenticate with your RunAI portal account details.
runai config project DGX_username -> Replace `DGX_username` with your username on the cluster nodes.
```

## Access to Worker Nodes (DGXs)

Following the upgrade, access to the DGX (worker nodes) has been disabled for users. This is because it's not required
and can cause problems. To use the cluster and submit jobs, you only need access to one of the headnodes. Refer to the
instructions in the previous section.

## The Registry

The registry is now distributed across all three headnodes, increasing the cluster's high availability. Use the
hostname `aicregistry` with port 5000 to access the registry from the headnode where you're logged in.

## Running a Job Using a Standard Nvidia Container

Begin by pulling the desired container. Here are some examples of pulling PyTorch and TensorFlow containers:

```
# PyTorch version 2
docker pull nvcr.io/nvidia/pytorch:24.05-py3

# TensorFlow version 1
docker pull nvcr.io/nvidia/tensorflow:22.11-tf2-py3

# TensorFlow version 2
docker pull nvcr.io/nvidia/tensorflow:24.05-tf2-py3

```

For further documentation and a comprehensive list of other available containers visit [Dockerhub](https://hub.docker.com/).

You can now run a job using a Docker image built with this container by using the RunAI submission system. The main
arguments are outlined below, along with an example:

**Main Submission Arguments:**

* `runai submit --name <Job Name>`: Specifies the name of your job.
* `--image -i <Docker Image>`: Defines the Docker image to use.
* `--run-as-user`: Runs the job with your user privileges.
* `--gpu -g <Number Of GPUs>`: Sets the number of GPUs to allocate to the job.
* `--project -p <Username/Project Name>`: Assigns the job to your project.
* `--volume -v <Directory:Mount Name>`: Mounts a volume from the cluster to the container.
* `--command -- <Command To Run>`: Specifies the command to execute within the container.

**Example for user "pedro":**

```
runai submit --name tester \
  --image nvcr.io/nvidia/tensorflow:22.11-tf2-py3 \
  --run-as-user \
  --gpu 1 \
  --project pedro \
  -v /nfs:/nfs \
  --command -- bash /nfs/home/pedro/tester/run_tester.sh 'train'
```

In this example, `run_tester.sh` is a bash script that might contain additional commands like `python3`. To run the
script, we call `bash`, hence it's included in the `--command` option.

**General Tips:**

* It's recommended to always include `-v /nfs:/nfs` and `--run-as-user` in your commands.
* Refer to the RunAI submit documentation for further information.

## Job Monitoring/Listing/Deletion

Once you've submitted a job, you can view its details using:

```
runai describe job <JobName>
```

This will show the job's queuing status and any submission errors. Refer to the official man page on `runai describe`
for more details.

To check on a running job (similar to running it locally), use:

```
runai logs <JobName>
```

See the official man page on `runai logs` for more information.

To view a list of currently pending or running jobs, use:

```
runai list
```

Refer to the official man page on `runai list` for details.

To delete a job, use:

```
runai delete job <JobName>
```

See the official man page on `runai delete` for more information.

## Checking Job Logs Using TensorBoard

This section explains how to view logs from a running job using TensorBoard.

**Steps:**

1. **Submit an interactive job:** Submit an interactive job specifically for running TensorBoard on your desired
   directory using a specific port. Utilize the `--interactive` and `--gpu 0` flags during submission.

**Note:** This interactive job is solely for TensorBoard, not your actual training job. Submit training jobs separately.

2. **Access the interactive job:** Use the command `runai bash <JOBNAME>` to access the interactive job.

3. **Find the host IP:** Within the interactive job, run `hostname -i` to determine the host IP address.

4. **Run the SSH tunnel locally:** On your local machine, run the following command to establish an SSH tunnel:

```
ssh -N -f -L <LOCALPORT>:<HOSTNAME>:<DGXPORT> <USER>@h1 (replace with h1, h2 or h3 according to the previous command output). The ports can be any two (different) numbers.
```

5. **Run TensorBoard in the interactive job:** Inside the interactive job, execute the following command (adjust
   accordingly):

```
tensorboard --logdir <LOGDIR> --port <DGXPORT>
```

6. **View TensorBoard logs:** Finally, navigate to `http://localhost:<LOCALPORT>` in your web browser to view the
   TensorBoard logs.

**Simplifying Steps:**

Steps 1, 3, and 5 can be consolidated by creating a bash script containing both `hostname -i`
and `tensorboard --logdir <LOGDIR> --port <DGXPORT>`. This way, you only need to check the job logs to obtain the host
IP.


## How to Check Job Failures

This section explains how to identify the underlying error causing job failures and prevent them from getting stuck in a
loop.

**Steps:**

1. **Get your job name:** Utilize the following command to list all jobs under your username:

   ```
   runai list --project <User Name>
   ```

   Replace `<User Name>` with your actual username.

2. **Grab all pods:** Following these steps will help you

## Next steps...

Once you are familiar on how to run and manage jobs in the cluster, in order to achieve a fair use of the system, it is
recommended to consider the suggested changes in the fair use [guidelines](DGX_fair_use_guidelines.md).