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
