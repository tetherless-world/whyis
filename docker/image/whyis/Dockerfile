FROM tetherlessworld/whyis-deps:master

COPY / /apps/whyis
# Remove any existing venv
RUN rm -fr /apps/whyis/venv
RUN chown -R whyis.whyis /apps/whyis

COPY /apache.conf /etc/apache2/sites-available/000-default.conf
COPY /resources/celeryd /etc/default/celeryd

WORKDIR /apps/whyis/whyis-java
RUN sudo -u whyis mvn clean compile assembly:single -PwhyisProfile

COPY /docker/image/whyis/docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
WORKDIR /apps/whyis
