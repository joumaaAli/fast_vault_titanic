# First stage: build the application
FROM python:3.9 as builder

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file to install dependencies
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir --upgrade-strategy eager -r requirements.txt
RUN pip install fastapi uvicorn

# Copy the rest of the application code into the container
COPY . .

# Second stage: create the final image with only the necessary runtime environment
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies and application code from the builder stage
COPY --from=builder /app /app

# Expose the port the app runs on
EXPOSE 8001

# Command to run the application
CMD ["python", "-m", "fastapi", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
