ARG WHYIS_IMAGE_TAG=latest
FROM tetherlessworld/whyis-deps:$WHYIS_IMAGE_TAG

# Copy files as root

# Apache configuration
COPY /apache.conf /apache.conf
RUN sed '1d' /apache.conf > /etc/apache2/sites-available/000-default.conf
RUN rm /apache.conf

# Celery configuration
COPY /docker/image/whyis/celeryd /etc/default/celeryd

# Entrypoint
COPY /docker/image/whyis/docker-entrypoint.sh /

# Do the remainder as the whyis user
COPY --chown=whyis:whyis / /apps/whyis

WORKDIR /apps/whyis/static
RUN npm install
RUN npm run build

WORKDIR /apps/whyis/whyis-java
RUN sudo -u whyis mvn -q clean compile assembly:single -PwhyisProfile

CMD ["tail", "-f", "/dev/null"]
ENTRYPOINT ["/docker-entrypoint.sh"]
WORKDIR /apps/whyis
