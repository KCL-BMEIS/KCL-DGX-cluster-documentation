# RunAI Centre DGX Cluster - School of BMEIS

## Introduction

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
`isd-helpdesk@kcl.ac.uk`

---

## Users of the cluster must follow the recommended guidelines described in `DGX cluster guidelines.md`

---

## How to access the headnodes

You will need to login to aicheadnode.isd.kcl.ac.uk to submit jobs.

The headnodes are accessible directly from any of the (wired) School networks in St Thomas or Becket House. If using
Wi-Fi or if working from home, you will need to use the school ssh gateway (bouncer.isd.kcl.ac.uk) as a jump host to
access the headnodes.

**IMPORTANT:** Because of the multi-headnode setup, you will need to add the following lines to your `.ssh/config` file
in your client machine when accessing the headnode at the address aicheadnode:

```
Host aicheadnode*
  StrictHostKeyChecking no
  UserKnownHostsFile=/dev/null
```

This will prevent the ssh client from complaining because the name aicheadnode is load-balancing via DNS and is in fact
accessing randomly one of the 3 headnode servers.

If you do not have one already, you can request an account on bouncer sending an email to isd-it@kcl.ac.uk or to
isd-helpdesk@kcl.ac.uk. Please copy your supervisor in CC when doing so.

The new version of the cluster, expanded to 8 nodes in December 2022, has 3 headnodes instead of one, to redistribute
the users evenly and reducing the workload on each headnode server.

* You will need to use the name aicheadnode.isd.kcl.ac.uk to connect (which resolves to all 3 addresses, so you will
  randomly access one of the headnode servers).
* Your home folder is centralised and stored on the NetApp storage system, so it does not really matter which of the 3
  headnode servers you login to.

**IMPORTANT:** the only exception is when you are connecting to the cluster for the first time or if you need to change
the password for your account on the cluster. We have restricted the change password functionality to only one of the
nodes: h1.isd.kcl.ac.uk (a.k.a. headnode1.isd.kcl.ac.uk), to make the synchronisation of the password file across the
three nodes easier to manage. So, if you need to change your account's password, you will need to login to
h1.isd.kcl.ac.uk and use the passwd command. If you try to change your password while logged in on h2 or h3, you will
receive a message telling you to do it on h1 (headnode1).

**Examples:**

**Accessing from a computer connected to one of the BMEIS (wired) networks:**

```
ssh <your cluster username>@aicheadnode
or run
ssh <your cluster username>@aicheadnode.isd.kcl.ac.uk
```

**Accessing from a computer at home or outside the BMEIS network:**

```
ssh -J <your bouncer username>@bouncer.isd.kcl.ac.uk <your_cluster_username>@aicheadnode
```

**Note:** If you already had an account on the cluster before the cluster expansion/redeployment, your credentials
should have been kept and you should be able to login as before, regardless if you were using a password or were
accessing via


## Setting Up the Environment for RunAI

After logging in to the cluster headnode for the first time, you'll need to configure the environment for the RunAI scheduler. Here are the commands:

```
runai login -> When prompted, authenticate with your RunAI portal account details.
runai config project DGX_username -> Replace `DGX_username` with your username on the cluster nodes.
```

## Access to Worker Nodes (DGXs)

Following the upgrade, access to the DGX (worker nodes) has been disabled for users. This is because it's not required and can cause problems. To use the cluster and submit jobs, you only need access to one of the headnodes. Refer to the instructions in the previous section.

## The Registry

The registry is now distributed across all three headnodes, increasing the cluster's high availability. Use the hostname `aicregistry` with port 5000 to access the registry from the headnode where you're logged in.

## Running a Job Using a Standard Nvidia Container

Begin by pulling the desired container. Here are some examples of pulling PyTorch and TensorFlow containers:

```
# TensorFlow version 1
docker pull nvcr.io/nvidia/tensorflow:22.11-tf2-py3

# TensorFlow version 2
docker pull nvcr.io/nvidia/tensorflow:22.11-tf2-py3

# PyTorch version 1
docker pull nvcr.io/nvidia/pytorch:22.11-py3
```

For further documentation and a comprehensive list of other available Nvidia containers, refer to [here](link to Nvidia container documentation).

You can now run a job using a Docker image built with this container by using the RunAI submission system. The main arguments are outlined below, along with an example:

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

In this example, `run_tester.sh` is a bash script that might contain additional commands like `python3`. To run the script, we call `bash`, hence it's included in the `--command` option.

**General Tips:**

* It's recommended to always include `-v /nfs:/nfs` and `--run-as-user` in your commands.
* Refer to the RunAI submit documentation for further information.

## Job Monitoring/Listing/Deletion

Once you've submitted a job, you can view its details using:

```
runai describe job <JobName>
```

This will show the job's queuing status and any submission errors. Refer to the official man page on `runai describe` for more details.

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

1. **Submit an interactive job:** Submit an interactive job specifically for running TensorBoard on your desired directory using a specific port. Utilize the `--interactive` and `--gpu 0` flags during submission.

**Note:** This interactive job is solely for TensorBoard, not your actual training job. Submit training jobs separately.

2. **Access the interactive job:** Use the command `runai bash <JOBNAME>` to access the interactive job.

3. **Find the host IP:** Within the interactive job, run `hostname -i` to determine the host IP address.

4. **Run the SSH tunnel locally:** On your local machine, run the following command to establish an SSH tunnel:

```
ssh -N -f -L <LOCALPORT>:<HOSTNAME>:<DGXPORT> <USER>@h1 (replace with h1, h2 or h3 according to the previous command output). The ports can be any two (different) numbers.
```

5. **Run TensorBoard in the interactive job:** Inside the interactive job, execute the following command (adjust accordingly):

```
tensorboard --logdir <LOGDIR> --port <DGXPORT>
```

6. **View TensorBoard logs:** Finally, navigate to `http://localhost:<LOCALPORT>` in your web browser to view the TensorBoard logs.

**Simplifying Steps:**

Steps 1, 3, and 5 can be consolidated by creating a bash script containing both `hostname -i` and `tensorboard --logdir <LOGDIR> --port <DGXPORT>`. This way, you only need to check the job logs to obtain the host IP.

## Running Jobs with Custom Containers

This section guides you through creating and utilizing your custom Docker image for running jobs.

**Steps:**

1. **Create a folder:** Within your home directory, create a folder to store your Dockerfile and related files for container creation.

2. **Create a Dockerfile:** Use your preferred editor to create a Dockerfile specifying the desired software available in your container. Here's a recommended approach:

   * Start by pulling an existing container (e.g., Nvidia TensorFlow container).
   * Install any supplementary programs required.

   **Basic Template:**

   ```dockerfile
   FROM nvcr.io/nvidia/tensorflow:22.11-tf2-py3

   ARG USER_ID
   ARG GROUP_ID
   ARG USER

   RUN addgroup --gid $GROUP_ID $USER
   RUN adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID $USER
   WORKDIR /nfs/home/$USER
   EXPOSE 8888
   ```

3. **Place additional files (optional):** If you have additional files the Dockerfile needs to read, place them in the same folder. Before using them in a command, explicitly copy them into the current directory.

   ```
   # Example: requirements.txt containing packages to install using pip
   COPY requirements.txt.
   RUN pip3 install -r requirements.txt
   ```

4. **Build and push the image:** Create a bash script containing the following commands to build and push your image to the registry (assuming the script is in the same directory as your Dockerfile named Dockerfile):

   ```bash
   #!/bin/bash

   # Create a tag or name for the image
   docker_tag="your_image_name:tag"

   # Build the image using your Dockerfile and arguments
   docker build . -f Dockerfile \
     --tag ${docker_tag} --network=host \
     --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) --build-arg USER=${USER}

   docker push ${docker_tag}
   ```

   Run this script to build and push the image.

5. **Verify image creation:** Use `docker images` to confirm successful image creation.

6. **Run a job with your custom image:** You can now use your custom image just like a standard container by specifying its name in the `--image` argument of the `runai` command.

## How to Check Job Failures

This section explains how to identify the underlying error causing job failures and prevent them from getting stuck in a loop.

**Steps:**

1. **Get your job name:** Utilize the following command to list all jobs under your username:

   ```
   runai list --project <User Name>
   ```

   Replace `<User Name>` with your actual username.

2. **Grab all pods:** Following these steps will help you

## Next steps...

Once you are familiar on how to run and manage jobs in the cluster, in order to achieve a fair use of the system, it is recommended to consider the suggested changes in the fair use [guidelines](DGX_fair_use_guidelines.md).