# hash:sha256:73d1c8661ba989cf6d680f1e660fbb5348889ee7c9d33ea475414770dd59783e
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/code-server-python-extensions-pack:code-server4.129.0python3.12.4codeocean-mcp-serveruvpyreflyetc

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

RUN pip3 install -U --no-cache-dir \
    caveclient==8.2.1 \
    cloud-volume==12.14.2 \
    hdmf==6.1.0 \
    hdmf-zarr==0.13.0 \
    matplotlib==3.11.1 \
    nwbwidgets==0.11.3 \
    ossify==0.2.4 \
    pynwb==4.1.0 \
    scipy==1.18.0 \
    seaborn==0.13.2 \
    standard-transform==2.0.0
