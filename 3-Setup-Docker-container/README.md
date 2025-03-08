# Docker container creation

This tutorial covers the basic concepts of how to create your own Docker container and get it running for your
*runai* project.

**Steps:**

1. **Create a folder:** Within your home directory, create a folder to store your Dockerfile and related files for
container creation.

2. **Create a Dockerfile:** Use your preferred editor to create a Dockerfile specifying the desired software available
in your container. Here's a recommended approach:

   * Start by pulling an existing container (e.g., Nvidia TensorFlow container).
   * Install any supplementary programs required.

**Basic template:**

```dockerfile
FROM nvcr.io/nvidia/tensorflow:22.11-tf2-py3

ARG USER_ID
ARG GROUP_ID
ARG USER

RUN echo "Building with user: "$USER", user ID: "$USER_ID", group ID: "$GROUP_ID

RUN addgroup --gid $GROUP_ID $USER
RUN adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID $USER
WORKDIR /nfs/home/$USER

# (Optional): If you have additional files the Dockerfile needs to read, place them in the same folder. Before 
# using them in a command, explicitly copy them into the current directory e.g. arequirements.txt containing packages 
# to install using pip.

COPY requirements.txt .
RUN pip3 install -r requirements.txt
```

> [!TIP]
> If you are using multiple consecutive `RUN` statements in your dockerfile, you can chain them together using `&&` This
> reduces both the memory size and build time of the subsequent dockerfile.
> 
> E.g., for the previous together file:
```dockerfile
      RUN addgroup --gid $GROUP_ID $USER && adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID $USER
```

3. **Build and push the image:** Create a bash script containing the following commands to build and push your image to
the registry (assuming the script is in the same directory as your Dockerfile named Dockerfile):

```bash
#!/bin/bash

read -p "Enter image name: [default: "${USER}"] " image_name
if [ -z ${image_name} ]; then
image_name=${USER}
fi

# Create a tag or name for the image
docker_tag="aicregistry:5000/"${image_name}
export GROUP_ID=$(id -g)
export USER_ID=$USER
echo "Docker tag: "${docker_tag}

# Build the image using your Dockerfile and arguments
echo "Building the image..."
echo "docker build -f Dockerfile . --tag ${docker_tag} --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) --build-arg USER=${USER} --progress=plain --no-cache"
docker build -f Dockerfile . --tag ${docker_tag} --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) --build-arg USER=${USER} --progress=plain --no-cache

# Push the built image to aicregistry
docker push ${docker_tag}
```

Run this bash script to build and push the image.

4. **Verify image creation:** Use `docker images` to confirm successful image creation.

5. **Run a job with your custom image:** You can now use your custom image just like a standard container by specifying
its name in the `--image` argument of the `runai` command.

