# Use a specific version of the Ubuntu base image for consistency
# FROM python:3.8-slim

# # Avoid prompts from apt during installation
# ARG DEBIAN_FRONTEND=noninteractive

# # Install prerequisites, including Python, pip, and tools for msodbcsql18
# RUN apt-get update && apt-get install -y gnupg2 wget software-properties-common unixodbc-dev gcc g++ \
#     && wget -qO- https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
#     # Directly add the repository for msodbcsql18
#     && echo "deb [arch=amd64,arm64,ppc64el] https://packages.microsoft.com/ubuntu/20.04/prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/mssql-release.list \
#     && apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
#     && apt-get install -y python3-pip python3-dev \
#     # Clean up
#     && apt-get clean && rm -rf /var/lib/apt/lists/*

FROM --platform=linux/amd64 public.ecr.aws/docker/library/python:3.9.10-slim-buster

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

# Copy the rest of the application's code
COPY . /app

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

ARG AZURE_SQL_CONNECTIONSTRING
ARG APP_SECRET_KEY
ARG AUTH0_CLIENT_ID
ARG AUTH0_CLIENT_SECRET
ARG AUTH0_DOMAIN
ARG RAPID_API_KEY
ARG YOUTUBE_API_KEY
ARG OPENAI_KEY
ARG EDAMAM_API_ID
ARG EDAMAM_API_KEY
ARG FIND_PARTNER_API
ENV AZURE_SQL_CONNECTIONSTRING="Driver={ODBC Driver 18 for SQL Server};Server=tcp:workout-buddy.database.windows.net,1433;Database=workout-buddy;Uid=azureuser;Pwd=2024Workout-buddy;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
ENV APP_SECRET_KEY="1h78wTV9oQcrMcQASCrpiYNoOP3Bzqsa"
ENV AUTH0_CLIENT_ID="N8RDsF6lIOoyYCy8T6C2doistDhvE4cY"
ENV AUTH0_CLIENT_SECRET="0jmY8y27Jkidi41rknSRjomW_rAMXKhf7fghADFYMgaFFnpef15RJy67IfVfkvMo"
ENV AUTH0_DOMAIN="dev-m6bye4zj5oeofurg.us.auth0.com"
ENV RAPID_API_KEY="9ede2c0d5emsh11b19ac6345dfa4p1d949fjsnc2352cae16c3"
ENV YOUTUBE_API_KEY="AIzaSyBPCeLjkgZOkSw3HotxraxH2kRDUavONug"
ENV OPENAI_KEY="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"
ENV EDAMAM_API_ID="d897a7c2"
ENV EDAMAM_API_KEY="5e73be6c4476511610a2a6e3b8046781"
ENV FIND_PARTNER_API="http://find-partner-api-server-dns.dpdjeeg7acaza5gc.uksouth.azurecontainer.io:5000/"

# Command to run the application
CMD ["flask", "run", "--debug", "--host=0.0.0.0", "--port=5000"]