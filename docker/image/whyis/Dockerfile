ARG WHYIS_IMAGE_TAG=latest

FROM maven:3.6-jdk-8 as build-java
WORKDIR /apps/whyis/whyis-java
COPY /whyis-java /apps/whyis/whyis-java
RUN mvn -q clean compile assembly:single -PwhyisProfile

FROM node:12-alpine as build-js
COPY static /static
WORKDIR /static
RUN npm install
RUN npm run build

# Deploy image from here
FROM tetherlessworld/whyis-deps:$WHYIS_IMAGE_TAG

# Apache configuration
COPY /puppet/files/etc/apache2/sites-available/000-default.conf /apache.conf
RUN sed '1d' /apache.conf > /etc/apache2/sites-available/000-default.conf
RUN rm /apache.conf

# Celery configuration
COPY /docker/image/whyis/celeryd /etc/default/celeryd

# Entrypoint
COPY /docker/image/whyis/docker-entrypoint.sh /
COPY /docker/image/load-whyis-data.sh /

# Copy the remainder as the whyis user
COPY --chown=whyis:whyis / /apps/whyis
COPY --from=build-java --chown=whyis:whyis /apps/whyis/jars /apps/whyis/jars
COPY --from=build-js --chown=whyis:whyis /static/js/whyis_vue_bundle.js* /apps/whyis/static/js/

CMD ["tail", "-f", "/dev/null"]
ENTRYPOINT ["/docker-entrypoint.sh"]
WORKDIR /apps/whyis
