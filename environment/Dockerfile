# hash:sha256:dc53b62f3ae75375184a78ab2b7218cd08b533b71563b649f2a8ae30d2384237
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/py-r:python3.12.4-R4.4.2-1.2204.0-JupyterLab4.3.0-RStudiorstudio-server-2024.09.0-375-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

RUN pip3 install -U --no-cache-dir \
    caveclient==8.2.1 \
    cloud-volume \
    hdmf==6.1.0 \
    hdmf-zarr==0.13.0 \
    matplotlib==3.11.1 \
    nwbwidgets==0.11.3 \
    ossify==0.2.4 \
    pynwb==4.1.0 \
    scipy==1.18.0 \
    seaborn==0.13.2 \
    standard-transform==2.0.0
