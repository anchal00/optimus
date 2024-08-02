# Use a base image with Python
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the required Python packages
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Install the current package
RUN pip install .

# Command to run the application
ENTRYPOINT [ "optimus", "-r"]
