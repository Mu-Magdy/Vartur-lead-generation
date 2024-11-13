# Use the RapidFort image as the base
FROM rapidfort/python-chromedriver:latest-arm64

# Set environment variables
ENV PYTHON_VERSION=3.11.6

# Install dependencies required to build Python from source
RUN apt-get update && apt-get install -y \
    wget \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libffi-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    liblzma-dev \
    && rm -rf /var/lib/apt/lists/*

# Download, extract, and compile Python 3.11
RUN wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz \
    && tar xzf Python-${PYTHON_VERSION}.tgz \
    && cd Python-${PYTHON_VERSION} \
    && ./configure --enable-optimizations \
    && make -j$(nproc) \
    && make altinstall \
    && cd .. \
    && rm -rf Python-${PYTHON_VERSION}*

# Set Python 3.11 as the default Python version
RUN update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.11 1

# Install pip for Python 3.11
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Copy requirements and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN python3.11 -m pip install --no-cache-dir -r /app/requirements.txt

# Set the working directory and copy the application code
WORKDIR /app
COPY . .

# Ensure that the necessary environment variables are set
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

# Create Streamlit configuration
RUN mkdir -p /root/.streamlit
RUN echo "\
[server]\n\
enableCORS = false\n\
enableXsrfProtection = false\n\
" > /root/.streamlit/config.toml

# Start Xvfb, Chromium, and Streamlit
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose the port Streamlit runs on
EXPOSE 8501

# Set the entrypoint to the start script
CMD ["/app/start.sh"]
