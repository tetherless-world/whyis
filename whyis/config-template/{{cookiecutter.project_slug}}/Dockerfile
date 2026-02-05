FROM tetherlessworld/whyis:latest
RUN apt-get update
COPY . /app
COPY ./install_files/system-docker.conf /app/system.conf
RUN /opt/venv/bin/pip install -r /app/requirements.txt
WORKDIR '/app'
CMD [ "/bin/bash" ]