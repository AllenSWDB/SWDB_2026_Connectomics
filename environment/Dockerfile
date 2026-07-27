# hash:sha256:5898f4f76d6bdd5dc85f04abfe46d722fa023824a883f71345dbf1101c9058d0
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/py-r:python3.12.4-R4.4.2-1.2204.0-JupyterLab4.3.0-RStudiorstudio-server-2024.09.0-375-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_ASKPASS
COPY git-ask-pass /

RUN pip3 install -U --no-cache-dir \
    caveclient==8.2.1 \
    matplotlib==3.11.1 \
    ossify==0.2.4 \
    scipy==1.18.0 \
    seaborn==0.13.2 \
    standard-transform==2.0.0
