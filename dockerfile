# Dockerfile
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy your application code
COPY . .

# Command to run the Streamlit app
CMD ["streamlit", "run", "main.py"]
