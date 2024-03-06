# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install system dependencies for PyODBC
RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg \
    g++ \
    unixodbc-dev \
    curl

# Add Microsoft repo for Microsoft ODBC Driver for SQL Server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Install Microsoft ODBC Driver for SQL Server
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# # Install odbc packages and the .deb file using dpkg
# RUN apt-get update && apt-get install -y unixodbc && apt-get install -y odbcinst libkrb5-3
# RUN DEBIAN_FRONTEND=noninteractive ACCEPT_EULA=Y dpkg -i msodbcsql18_18.3.2.1-1_amd64.deb

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV AZURE_SQL_CONNECTIONSTRING="Driver={ODBC Driver 18 for SQL Server};Server=tcp:workout-buddy.database.windows.net,1433;Database=workout-buddy;Uid=azureuser;Pwd=2024Workout-buddy;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

# Run app.py when the container launches
CMD ["python", "main.py"]