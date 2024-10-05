#!/usr/bin/env python3

import os
import subprocess
import requests
import tarfile
import sys

inputs = {
    'arch': os.getenv('INPUT_ARCH'),
    'board': os.getenv('INPUT_BOARD'),
    'build-script-path': os.path.normpath(os.getenv('INPUT_BUILD-SCRIPT-PATH')),
    'remove-debug-flags': str(os.getenv('INPUT_REMOVE-DEBUG-FLAGS', '')).split(),
    'ota-firmware-source': os.getenv('INPUT_OTA-FIRMWARE-SOURCE', ''),
    'ota-firmware-target': os.getenv('INPUT_OTA-FIRMWARE-TARGET', ''),
    'include-web-ui': bool(os.getenv('INPUT_INCLUDE-WEB-UI', False))
}

env = {
    'GITHUB_ACTIONS': bool(os.getenv('GITHUB_ACTIONS')),
    'XDG_CACHE_HOME': os.path.normpath(os.getenv('XDG_CACHE_HOME'))
}

def gh_latest_release(owner, repo):
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/releases/latest")
    r_j = r.json()
    if r.status_code == 200:
        return r_j
    else:
        raise Exception(f"Failed to fetch latest release from {owner}/{repo}")

def download_file(url, dest):
    print(f"Downloading {url} to {dest}")
    r = requests.get(url, stream=True)
    with open(dest, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    return dest

def extract_tar(tar_file, extract_to, remove_src=False):
    print(f"Extracting {tar_file} to {extract_to}")
    with tarfile.open(tar_file, 'r') as tar:
        tar.extractall(extract_to, filter='fully_trusted')

    if remove_src == True:
        print(f"..Cleaning up {tar_file}")
        os.remove(tar_file)
        return 
    else:
        return tar_file

# ==============

# Fix cache permissions
if os.path.exists(env['XDG_CACHE_HOME']):
    os.system(f'chmod -R 777 {env['XDG_CACHE_HOME']}')

# Workaround for the "safe.directory" issue
os.system("git config --system --add safe.directory /github/workspace")

# Web UI
if inputs['include-web-ui'] == True:
    mt_web = gh_latest_release('meshtastic', 'web')
    for asset in mt_web['assets']:
        if asset['name'] == 'build.tar':
            # Download build.tar
            download_file(asset['browser_download_url'], 'build.tar')
            # Extract build.tar
            extract_tar('build.tar','data/static', remove_src=True)

# Remove debug flags for release
if len(inputs['remove-debug-flags']) > 0:
    for flag in inputs['remove-debug-flags']:
        os.system(f"sed -i /DDEBUG_HEAP/d {flag}")

# Run the Build
sys.stdout.flush()
r_build = subprocess.run([inputs['build-script-path'], inputs['board']], check=True)

# Pull OTA firmware
if inputs['ota-firmware-source'] != '' and inputs['ota-firmware-target'] != '':
    ota_fw = gh_latest_release('meshtastic', 'firmware-ota')
    for asset in ota_fw['assets']:
        if asset['name'] == inputs['ota-firmware-source']:
            # Download firmware.bin
            download_file(asset['browser_download_url'], inputs['ota-firmware-target'])

# When running in GitHub Actions
if env['GITHUB_ACTIONS']:
    # Hack! - Add checked-out firmware/bin to the python module path
    sys.path.append(os.path.abspath('bin'))
    from readprops import readProps # type: ignore
    # /Hack!

    # Get release version string
    verObj = readProps("version.properties")
    version_str = verObj['long']
    # Write version string to GitHub Actions output
    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
        print(f'version={version_str}', file=fh)

    # Fix cache permissions
    os.system(f'chmod -R 777 {env['XDG_CACHE_HOME']}')
