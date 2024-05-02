from jupyter/base-notebook
USER root

RUN apt update
RUN apt install --yes git
RUN apt install --yes gcc


COPY fix-permissions /usr/local/bin/fix-permissions
RUN chmod a+rx /usr/local/bin/fix-permissions

ENV CONDA_DIR=/opt/conda \
    SHELL=/bin/bash \
    NB_USER=$NB_USER \
    NB_UID=$NB_UID \
    NB_GID=$NB_GID \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8
ENV PATH=$CONDA_DIR/bin:$PATH \
    HOME=/home/$NB_USER \
    CONDA_VERSION="${conda_version}" \
    MINIFORGE_VERSION="${miniforge_version}"

USER $NB_UID

RUN conda install --quiet --yes \
    'pvlib' \
    'netCDF4'  \
    'siphon'  \
    'pandas' \
    'awscli' \
    'flake8' \
    'python-dotenv' \
    'seaborn' \
    'awswrangler' && \
    conda clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

USER $NB_UID

WORKDIR $HOME
