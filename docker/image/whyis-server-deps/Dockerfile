FROM tetherlessworld/whyis-ubuntu

RUN puppet module install\
	puppet-python --version 3.0.1
RUN puppet module install\
	puppetlabs-apt --version 7.0.1
RUN puppet module install\
	puppet-nodejs --version 7.0.1

COPY /docker/image/whyis-server-deps/install.pp /
COPY /requirements/ /requirements
RUN puppet apply /install.pp &&\
	rm -rf /install.pp\
	/requirements

