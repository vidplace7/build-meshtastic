#!/bin/bash

# Web UI
if [ "$INCLUDE_WEB_UI" = "true" ]; then
    # Pull web ui
    dra download --select build.tar meshtastic/web --output /tmp/webui.tar

    # Unpack web ui
    tar -xf /tmp/webui.tar -C data/static
    rm /tmp/webui.tar
fi

# Remove debug flags for release
if [ "$REMOVE_DEBUG_FLAGS" != "" ]; then
    for INI_FILE in $REMOVE_DEBUG_FLAGS; do
        sed -i '/DDEBUG_HEAP/d' ${INI_FILE}
    done
fi

# Run the Build
$BUILD_SCRIPT_PATH $BOARD

# Pull OTA firmware
if [ "$OTA_FIRMWARE_SOURCE" != "" ] && [ "$OTA_FIRMWARE_TARGET" != "" ]; then
    dra download --select $OTA_FIRMWARE_SOURCE --output $OTA_FIRMWARE_TARGET
fi

# Get release version string when running in GitHub Actions
if [ "$GITHUB_ACTIONS" = "true" ]; then
    echo "version=$(buildinfo.py long)" > $GITHUB_OUTPUT
fi
