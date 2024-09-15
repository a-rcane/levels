FROM python:3.10

WORKDIR /app

# Copy the requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Reinstall numpy to avoid binary incompatibility
RUN pip install --upgrade --force-reinstall numpy==1.24.4

# Install the rest of the requirements with no cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY app /app/app

# Set the command to run your application
CMD ["python", "app/main.py"]
