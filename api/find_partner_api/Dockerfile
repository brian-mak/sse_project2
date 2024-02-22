# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . /usr/src/app

# Update package repositories and install ODBC driver
RUN apt-get update && apt-get install -y unixodbc unixodbc-dev odbc-postgresql

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV AZURE_SQL_CONNECTIONSTRING=Driver={ODBC Driver 18 for SQL Server};Server=tcp:fitness-planner.database.windows.net,1433;Database=Fitness Planner;Uid=CloudSA063070df;Pwd=!Gy59dt#b:rF.TS;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30 

# Connect to Repo
LABEL org.opencontainers.image.source=https://github.com/lem123ic/sse_project2 

# Run app.py when the container launches
CMD ["flask", "run"]