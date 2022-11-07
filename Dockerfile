FROM python:3.9

# NOTE: Make sure ./eagleproject is mounted to 
# /app before running this image.
WORKDIR /app

# Volumes aren't available during build.
# So, copying the requirements.txt file temporarily.
# This requires rebuilding the image every time
# there's a change in dependencies.
COPY ./eagleproject/requirements.txt ./requirements.txt

# Install requirements
RUN pip install -r requirements.txt

# Install psql
RUN set -ex; \
    curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - ; \
    echo "deb http://apt.postgresql.org/pub/repos/apt/ bullseye-pgdg main 14" > /etc/apt/sources.list.d/pgdg.list; \
    mkdir -p /etc/postgresql-common/createcluster.d/; \
    echo "create_main_cluster = false" > /etc/postgresql-common/createcluster.d/no-main-cluster.conf; \
    apt-get update -y; \
    apt-get install -y --no-install-recommends postgresql-client-14; \
    apt-get clean;

EXPOSE 8000

# ENTRYPOINT ["/bin/sh", "-c" , "./entrypoint.sh && python manage.py runserver 8000"]
