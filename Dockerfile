FROM python:3.13-slim-bookworm

# Set correct timezone
RUN ln -sf /usr/share/zoneinfo/America/Los_Angeles /etc/localtime

# Create generic ftva_data user
RUN useradd -c "generic app user" -d /home/appuser -s /bin/bash -m appuser

# Switch to application directory, creating it if needed
WORKDIR /home/appuser/project

# Make sure appuser owns app directory, if WORKDIR created it:
# https://github.com/docker/docs/issues/13574
RUN chown -R appuser:appuser /home/appuser

# Change context to appuser user for remaining steps
USER appuser

# Copy application files to image, and ensure appuser user owns everything
COPY --chown=appuser:appuser . .

# Include local python bin into appuser user's path, mostly for pip
ENV PATH=/home/appuser/.local/bin:${PATH}

# Make sure pip is up to date, and don't complain if it isn't yet
RUN pip install --upgrade pip --disable-pip-version-check

# Install requirements for this application
RUN pip install --no-cache-dir -r requirements.txt --user --no-warn-script-location