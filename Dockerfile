# Use the official Python slim image for a smaller footprint
FROM python:3.13-slim

# Prevent Python from writing .pyc files to disk and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
# (Note: This installs all dependencies including playwright, 
# but does NOT download the heavy browser binaries since the API doesn't need them)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code (including the src folder and data folder)
COPY . .

# Expose the port that FastAPI will run on
EXPOSE 8000

# Start the FastAPI server using Uvicorn
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
