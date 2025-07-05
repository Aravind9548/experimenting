# Dockerfile (in backend/)
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy backend code
COPY . .

# Copy React build into backend folder
COPY build ./build


# Expose port and run
EXPOSE 5000
CMD ["python", "app.py"]
