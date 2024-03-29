FROM ubuntu:20.04
RUN apt-get update && apt-get install -y software-properties-common gcc

ARG __version__

RUN apt-get update && apt-get install -y \
    python3.8-distutils \
    python3.8-dev \
    python3-pip \
    python3.8-venv \
    curl \
#    libdb5.3-dev \
    default-jdk-headless
RUN python3.8 -m venv /opt/venv
RUN /opt/venv/bin/pip install wheel requests gunicorn
COPY dist/whyis-$__version__.tar.gz /opt/whyis-$__version__.tar.gz
RUN /opt/venv/bin/pip install /opt/whyis-$__version__.tar.gz
WORKDIR '/app'
CMD [ "/opt/venv/bin/whyis", "run", "-h", "0.0.0.0" ]
