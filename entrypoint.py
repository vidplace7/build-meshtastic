#!/usr/bin/env python3

import os
import subprocess
import requests
import tarfile
import sys
import shutil
import argparse

from git import Repo

# Parse arguments
# Handle CLI and GitHub Actions inputs
parser = argparse.ArgumentParser(description="")
parser.add_argument('git_ref', type=str,
                    default="master",
                    help='The tag or branch to clone from the repository.')
parser.add_argument('--git_dir', type=str, required=False,
                    # Use the GITHUB_WORKSPACE environment variable when running in GitHub Actions
                    # Otherwise, use the 'firmware' directory (local testing)
                    default=os.getenv('GITHUB_WORKSPACE', 'firmware'),
                    help='The directory to clone the meshtastic repository to.')
parser.add_argument('--arch', type=str, required=True,
                    help='The architecture to build for.')
parser.add_argument('--board', type=str, required=True,
                    help='The board to build for.')
parser.add_argument('--build_script_path', type=str, required=True,
                    help='The path to the build script.')
parser.add_argument('--remove_debug_flags', type=list, required=False,
                    default=str(os.getenv('INPUT_REMOVE-DEBUG-FLAGS', '')).split(),
                    help='The debug flags to remove from the build.')
parser.add_argument('--ota_firmware_source', type=str, required=False,
                    default=os.getenv('INPUT_OTA-FIRMWARE-SOURCE', ''),
                    help='The source path to download the OTA firmware.')
parser.add_argument('--ota_firmware_target', type=str, required=False,
                    default=os.getenv('INPUT_OTA-FIRMWARE-TARGET', ''),
                    help='The target path to save the OTA firmware.')
parser.add_argument('--include_web_ui', type=bool, required=False,
                    default=bool(os.getenv('INPUT_INCLUDE-WEB-UI', False)),
                    help='Whether to include the web UI in the build.')
args = parser.parse_args()

env = {
    'GITHUB_ACTIONS': bool(os.getenv('GITHUB_ACTIONS')),
    'XDG_CACHE_HOME': os.path.normpath(os.getenv('XDG_CACHE_HOME', ''))
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

# Clone the Meshtastic repo
if env['GITHUB_ACTIONS'] == False:
    if os.path.exists(args.git_dir):
        shutil.rmtree(args.git_dir)
gh_repo = "meshtastic/firmware"
print(f"Cloning {gh_repo} {args.git_ref} to {args.git_dir}/")
meshtastic_repo = Repo.clone_from("https://github.com/meshtastic/firmware.git", ".firmware", single_branch=True, branch=args.git_ref, recursive=True)
shutil.copytree(".firmware", args.git_dir, dirs_exist_ok=True)
shutil.rmtree(".firmware")
print(f"..Cloned {gh_repo} {args.git_ref} to {args.git_dir}/")

if env['GITHUB_ACTIONS']:
    # Fix cache permissions
    if os.path.exists(env['XDG_CACHE_HOME']):
        os.system(f'chmod -R 777 {env['XDG_CACHE_HOME']}')

    # Workaround for the "safe.directory" issue
    os.system("git config --system --add safe.directory /github/workspace")

# Web UI
if args.include_web_ui == True:
    mt_web = gh_latest_release('meshtastic', 'web')
    for asset in mt_web['assets']:
        if asset['name'] == 'build.tar':
            # Download build.tar
            download_file(asset['browser_download_url'], 'build.tar')
            # Extract build.tar
            extract_tar('build.tar','data/static', remove_src=True)

# Remove debug flags for release
if len(args.remove_debug_flags) > 0:
    for flag in args.remove_debug_flags:
        os.system(f"sed -i /DDEBUG_HEAP/d {flag}")

# Apply custom changes (if any)
if os.path.exists('.custom'):
    shutil.copytree(".custom/firmware", args.git_dir, dirs_exist_ok=True)
    shutil.rmtree('.custom')

# Run the Build
sys.stdout.flush()  # Fix subprocess output buffering issue
build_abspath = os.path.abspath(os.path.join(args.git_dir, args.build_script_path))
r_build = subprocess.run(
    [build_abspath, args.board],
    cwd=args.git_dir, check=True)

# Pull OTA firmware
if args.ota_firmware_source != '' and args.ota_firmware_target != '':
    ota_fw = gh_latest_release('meshtastic', 'firmware-ota')
    for asset in ota_fw['assets']:
        if asset['name'] == args.ota_firmware_source:
            # Download firmware.bin
            download_file(asset['browser_download_url'], args.ota_firmware_target)

# When running in GitHub Actions
if env['GITHUB_ACTIONS']:
    # Hack! - Add checked-out firmware/bin to the python module path
    sys.path.append(os.path.join(args.git_dir, 'bin'))
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
