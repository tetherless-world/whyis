FROM tetherlessworld/whyis-deps:master

# Copy files as root
COPY /apache.conf /etc/apache2/sites-available/000-default.conf
COPY /docker/image/whyis/celeryd /etc/default/celeryd
COPY /docker/image/whyis/docker-entrypoint.sh /

# Do the remainder as the whyis user
COPY --chown=whyis:whyis / /apps/whyis
# Remove any existing venv
RUN rm -fr /apps/whyis/venv

WORKDIR /apps/whyis/whyis-java
RUN sudo -u whyis mvn clean compile assembly:single -PwhyisProfile

ENTRYPOINT ["/docker-entrypoint.sh"]
WORKDIR /apps/whyis
