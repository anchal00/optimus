# Use a base image with Python
FROM python:3.9-alpine

# Set the working directory inside the container
WORKDIR /app

COPY . .

# Install the current package
RUN pip install --no-cache-dir .

# Command to run the application
ENTRYPOINT [ "optimus", "-r"]
