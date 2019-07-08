FROM tetherlessworld/whyis-deps:master

# Delete the /apps/whyis installed by whyis-deps
RUN rm -fr /apps/whyis
COPY / /apps/whyis
WORKDIR /apps/whyis
# Remove any existing venv
RUN rm -fr venv

COPY /docker/docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
