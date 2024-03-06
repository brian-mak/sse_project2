# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . /usr/src/app

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

ARG AZURE_CONNECTION_STRING
ENV AZURE_CONNECTION_STRING=$AZURE_CONNECTION_STRING

# Connect to Repo
LABEL org.opencontainers.image.source=https://github.com/lem123ic/sse_project2 

# Run app.py when the container launches
CMD ["flask", "run"]