FROM debian:bookworm

RUN apt update && apt install -y --no-install-recommends gnupg

RUN echo "deb http://archive.raspberrypi.org/debian/ bookworm main" > /etc/apt/sources.list.d/raspi.list \
  && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 82B129927FA3303E

RUN apt update && apt -y upgrade

RUN apt update && apt install -y --no-install-recommends \
  gcc \
  procps \
  build-essential \
  ffmpeg \
  v4l-utils \
  usbutils \
  python3-venv \
  python3-pip \
  python3-picamera2 \
  python3-dev \
  python3-prctl \
  libatlas-base-dev \
  libopenjp2-7\
  curl \
  wget \
  pkg-config \
  libhdf5-dev && \
  apt-get clean && \
  apt-get autoremove && \
  rm -rf /var/cache/apt/archives/* && \
  rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------------------------------------------
# Build and run application
# ------------------------------------------------------------------------------------------------

WORKDIR /IoTCountingApp

COPY requirements.txt .

# create a virtual python environment and install dependencies
RUN python3 -m venv --system-site-packages /venv && \
  /venv/bin/pip install --no-cache-dir -r requirements.txt && \
  /venv/bin/pip cache purge && \
  rm -rf /root/.cache/pip


COPY . /IoTCountingApp/

COPY entrypoint /entrypoint
RUN chmod +x /entrypoint

COPY ./restart_server /restart_server
RUN sed -i 's/\r$//g' /restart_server
RUN chmod +x /restart_server

EXPOSE ${APP_PORT}

ENTRYPOINT ["/entrypoint"]

CMD ["python3", "app.py"]