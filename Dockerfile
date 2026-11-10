# Use Python 3.12 as the base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /datalake

# Prevent Python from generating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Display Python logs immediately
ENV PYTHONUNBUFFERED=1

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY src/ ./src/

# Make the src directory available for Python imports
ENV PYTHONPATH=/datalake/src

# Start the ETL application
CMD ["python", "-m", "opendatalake"]