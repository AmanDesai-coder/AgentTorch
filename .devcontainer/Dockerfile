# Below copied from Copilot
# Use the official Ubuntu 22.04 LTS base image
FROM ubuntu:22.04

# Set the environment variables to avoid interaction while installing packages
ENV DEBIAN_FRONTEND=noninteractive

# Update the package list and install Python 3.8 and virtualenv
RUN apt-get update && \
    apt-get install -y python3.8 python3.8-venv python3-pip && \
    pip3 install virtualenv
