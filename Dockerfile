# this Dockerfile can be used to compile any third party softwares
# if the source code is stored locally, first copy this Dockerfile into the source code directory
# if the source code is stored in the github, we simply need this Dockerfile

# specify base os
FROM ubuntu:18.04

LABEL maintainer="Kai Zhang"

# specify that the following instructions will be run in a non-interactive way
ARG DEBIAN_FRONTEND=non-interactive

# install all package dependencies
# RUN apt-get update && apt-get install -y git build-essential cmake
RUN apt-get update && apt-get install python3 python3-pip python3-numpy python3-scipy
RUN pip install -U pip
# package for dealing with .ply files
RUN pip install plyfile
# install GDAL
RUN apt-get update && apt-get install gdal python-gdal

# the docker image filesystem has exactly the same structure as that of a linux system
# pull the source code from the github
# RUN git clone <github repo address>

# copy all the files inside the current host directory into that working directory
# what will be copied can be controlled by a .Dockerignore
# compile the source code inside the working directory

COPY . /texture_mapping

# build the software
# RUN cd /<source code folder name> && make -j4 all

# or cmake
# RUN cd /<source code folder name> && mkdir build && cd build && cmake .. && make -j4

# specify a working directory inside the docker image filesystem
WORKDIR /texture_mapping

# provide an entry point
# ENTRYPOINT["/<source code folder name>/entry_point.sh"]

# or execute some command
# CMD["bash"]
