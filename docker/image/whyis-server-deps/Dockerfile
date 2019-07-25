ARG WHYIS_IMAGE_TAG=latest
FROM tetherlessworld/whyis-ubuntu:$WHYIS_IMAGE_TAG

RUN puppet module install\
	puppet-python --version 3.0.1

COPY /docker/image/whyis-server-deps/install.pp /
COPY /requirements/ /requirements
RUN puppet apply /install.pp &&\
	rm -rf /install.pp\
	/requirements

# Remove pip cache
RUN rm -fr /root/.cache
