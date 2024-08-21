# Use a base image with Python
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

COPY . .

# Install the current package
RUN pip install .

# Command to run the application
ENTRYPOINT [ "optimus", "-r"]
