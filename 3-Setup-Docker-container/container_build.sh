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
echo "Building the image..."
echo docker build -f Dockerfile . --tag ${docker_tag} --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) --build-arg USER=${USER} --progress=plain --no-cache
# Build the image using your Dockerfile and arguments
docker build -f Dockerfile . --tag ${docker_tag} --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) --build-arg USER=${USER} --progress=plain --no-cache
docker push ${docker_tag}
docker images | head -n 1
docker images | grep ${docker_tag}
