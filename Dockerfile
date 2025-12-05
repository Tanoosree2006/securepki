# ---------- Stage 1: builder ----------
FROM python:3.12-slim AS builder
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /build

# Create venv and install deps
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ---------- Stage 2: runtime ----------
FROM python:3.12-slim AS runtime
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install cron + tzdata and set timezone to UTC
RUN apt-get update && apt-get install -y --no-install-recommends \
      cron tzdata \
 && ln -snf /usr/share/zoneinfo/UTC /etc/localtime \
 && echo "UTC" > /etc/timezone \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Bring venv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" TZ=UTC

# App code
COPY . /app

# Mount points for volumes
RUN mkdir -p /app/data /cron && chmod 755 /app /cron

# ---- Cron configuration (via file in /etc/cron.d) ----
# Make sure your local file cron/2fa-cron contains ONE LF-terminated line like:
# * * * * * root cd /app && /opt/venv/bin/python scripts/log_2fa_cron.py >> /cron/last_code.txt 2>&1
COPY cron/2fa-cron /etc/cron.d/securepki
RUN chmod 0644 /etc/cron.d/securepki

# ------------------------------------------------------

EXPOSE 8080

# Start cron, then run FastAPI (uvicorn from the same venv)
CMD ["/bin/sh","-c","/usr/sbin/cron && exec /opt/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8080"]
