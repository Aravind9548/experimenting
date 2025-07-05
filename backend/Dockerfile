# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy all project files into the container
COPY . .

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose the port Flask runs on
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the application
CMD ["flask", "run"]
