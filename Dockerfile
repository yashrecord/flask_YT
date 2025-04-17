# Use the slimmer Python 3.9 image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies and build tools
RUN apt-get update && \
    apt-get install -y ffmpeg build-essential libssl-dev libffi-dev python3-dev && \
    apt-get clean

# Create non-root user
RUN useradd -m -u 1000 user

# Copy requirements file
COPY requirements.txt /app/

# Install Python dependencies with additional options
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# Copy application files and set ownership
COPY . /app/
RUN chown -R user:user /app

# Switch to non-root user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Set environment variable
ENV FLASK_ENV=production

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:app"]