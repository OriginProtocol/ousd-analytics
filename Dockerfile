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

EXPOSE 8000

# # Copy start script
# COPY ./entrypoint.sh /app/run.sh
# RUN ["chmod", "+x", "/app/run.sh"]

# Run Migrations and then start server
# ENTRYPOINT ["/bin/sh", "-c" , "ls"]
ENTRYPOINT ["/bin/sh", "-c" , "python manage.py migrate && python manage.py runserver"]