# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY ./api /usr/src/app

# Install odbc packages and the .deb file using dpkg
RUN apt-get update && apt-get install -y unixodbc && apt-get install -y odbcinst
RUN DEBIAN_FRONTEND=noninteractive ACCEPT_EULA=Y dpkg -i msodbcsql18_18.3.2.1-1_amd64.deb

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

ARG AZURE_SQL_CONNECTIONSTRING
ARG AUTH0_CLIENT_ID
ARG AUTH0_CLIENT_SECRET
ARG AUTH0_DOMAIN
ARG APP_SECRET_KEY
ARG FORUM_API
ARG RAPID_API_KEY
ARG YOUTUBE_API_KEY
ARG OPENAI_KEY
ARG EDAMAM_API_ID
ARG EDAMAM_API_KEY
ENV AZURE_SQL_CONNECTIONSTRING=$AZURE_SQL_CONNECTIONSTRING
ENV AUTH0_CLIENT_ID=$AUTH0_CLIENT_ID
ENV AUTH0_CLIENT_SECRET=$AUTH0_CLIENT_SECRET
ENV AUTH0_DOMAIN=$AUTH0_DOMAIN
ENV APP_SECRET_KEY=$APP_SECRET_KEY
ENV FORUM_API=$FORUM_API
ENV RAPID_API_KEY=$RAPID_API_KEY
ENV YOUTUBE_API_KEY=$YOUTUBE_API_KEY
ENV OPENAI_KEY=$OPENAI_KEY
ENV EDAMAM_API_ID=$EDAMAM_API_ID
ENV EDAMAM_API_KEY=$EDAMAM_API_KEY


# Connect to Repo
LABEL org.opencontainers.image.source https://github.com/brian-mak/sse_project2 

# Run app.py when the container launches
CMD ["flask", "run"]