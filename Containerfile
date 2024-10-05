FROM python:3.12-bookworm
ENV PIP_ROOT_USER_ACTION=ignore

# Add build scripts (firmware/bin) to PATH
# RUN git clone --no-checkout --depth 1 https://github.com/meshtastic/firmware.git /meshtastic && \
#     git -C /meshtastic config core.sparseCheckout true && \
#     echo "bin/*" > /meshtastic/.git/info/sparse-checkout && \
#     git -C /meshtastic checkout master
# ENV PATH="/meshtastic/bin:$PATH"

# Install build dependencies
RUN apt update && apt install -y \
    build-essential \
    cppcheck libbluetooth-dev libgpiod-dev libyaml-cpp-dev && \
    # Install DRA (GitHub Releases downloader)
    # wget 'https://github.com/devmatteini/dra/releases/download/0.6.2/dra_0.6.2-1_amd64.deb' && \
    # dpkg --install dra_0.6.2-1_amd64.deb && rm dra_0.6.2-1_amd64.deb && \
    apt clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN python -m pip install --upgrade pip && \
    pip install -U --no-build-isolation --no-cache-dir "setuptools<72" && \
    pip install -U platformio adafruit-nrfutil --no-build-isolation && \
    pip install -U poetry --no-build-isolation && \
    pip install -U meshtastic --pre --no-build-isolation

# Upgrade PlatformIO
RUN pio upgrade

# COPY entrypoint.sh /entrypoint.sh
# ENTRYPOINT [ "/entrypoint.sh" ]

COPY entrypoint.py /entrypoint.py
ENTRYPOINT [ "/entrypoint.py" ]