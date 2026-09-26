FROM python:3.10-slim

# Security Metadata
LABEL maintainer="keylogger-monitor"
LABEL version="2.0.0"
LABEL description="Keylogger Monitor - Hardened Forensic Security Container"
LABEL security.hardened="true"

WORKDIR /app

# Install minimal OS dependencies for input capture
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-xlib \
    x11-utils \
    && rm -rf /var/lib/apt/lists/*

# Create unprivileged system user for isolated execution
RUN useradd -m -u 1000 monitoruser

# Install python dependencies
RUN pip install --no-cache-dir pynput

# Copy source code with non-root ownership
COPY --chown=monitoruser:monitoruser src/ ./src/
COPY --chown=monitoruser:monitoruser tests/ ./tests/
COPY --chown=monitoruser:monitoruser config.example.json ./config.json

# Switch to non-root user
USER monitoruser

# Container runtime healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import pynput; print('healthy')" || exit 1

CMD ["python", "src/workkeylogger.py"]