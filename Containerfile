FROM python:3.12-bookworm
ENV PIP_ROOT_USER_ACTION=ignore

# Install build dependencies
RUN apt update && apt install -y \
    build-essential \
    cppcheck libbluetooth-dev libgpiod-dev libyaml-cpp-dev && \
    apt clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install -U --no-build-isolation --no-cache-dir "setuptools<72" && \
    pip install -U --no-build-isolation -r requirements.txt && \
    pip install -U platformio adafruit-nrfutil --no-build-isolation && \
    pip install -U poetry --no-build-isolation && \
    pip install -U meshtastic --pre --no-build-isolation

# Upgrade PlatformIO
RUN pio upgrade

COPY entrypoint.py /entrypoint.py
ENTRYPOINT [ "/entrypoint.py" ]
CMD [ "master" ]