FROM tetherlessworld/whyis-deps:master

COPY / /apps/whyis
WORKDIR /apps/whyis
# Remove any existing venv
RUN rm -fr venv

COPY /docker/docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
