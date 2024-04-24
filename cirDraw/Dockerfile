# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Define environment variable
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && apt-get clean

# Install Python dependencies
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn

# Copy the current directory contents into the container at /usr/src/app
COPY . /usr/src/app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Set the default command to execute
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "flappyBirdLeaderBoard.wsgi:application"]