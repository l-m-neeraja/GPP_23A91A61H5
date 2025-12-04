# --------------------------
# Stage 1: Builder
# --------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

# Copy dependency file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# --------------------------
# Stage 2: Runtime
# --------------------------
FROM python:3.11-slim

ENV TZ=UTC
WORKDIR /app

# Install system dependencies (cron + timezone)
RUN apt-get update && \
    apt-get install -y cron tzdata && \
    ln -fs /usr/share/zoneinfo/UTC /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source
COPY . .

# Setup cron job
RUN chmod 0644 cronjob.txt && crontab cronjob.txt

# Create volume mount points
RUN mkdir -p /data && chmod 755 /data
RUN mkdir -p /cron && chmod 755 /cron

EXPOSE 8080

# Start cron + API
CMD cron && uvicorn app:app --host 0.0.0.0 --port 8080
