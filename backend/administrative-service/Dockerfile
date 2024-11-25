FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY . .

# Set Flask environment variables
ENV FLASK_APP=app
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 5000

# Start the Flask application
CMD ["flask", "run"]
