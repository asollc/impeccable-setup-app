#!/usr/bin/env python3
"""
Auto-updater for Impeccable Setup App.
Checks GitHub for a new version and updates if available.
"""

import json
import os
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path


REPO = "asollc/impeccable-setup-app"
VERSION_FILE = Path(__file__).parent / "VERSION"


def get_local_version():
    try:
        return VERSION_FILE.read_text().strip()
    except:
        return "0.0.0"


def get_remote_version():
    """Get the latest version from GitHub."""
    url = f"https://api.github.com/repos/{REPO}/releases/latest"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "impeccable-setup-app"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            # Tag format: v1.0.0, strip the v
            tag = data.get("tag_name", "v0.0.0")
            return tag.lstrip("v"), data
    except Exception as e:
        print(f"Update check failed: {e}")
        return None, None


def version_tuple(v):
    return tuple(int(x) for x in v.split(".") if x.isdigit())


def check_and_update():
    local = get_local_version()
    print(f"Current version: {local}")
    
    remote, release_data = get_remote_version()
    if not remote:
        print("Could not check for updates. Continuing...")
        return False
    
    print(f"Latest version: {remote}")
    
    if version_tuple(remote) <= version_tuple(local):
        print("Already up to date.")
        return False
    
    print(f"\nUpdate available: {local} -> {remote}")
    print("Downloading...")
    
    # Find the zip asset
    assets = release_data.get("assets", [])
    zip_url = None
    for asset in assets:
        if asset["name"].endswith(".zip"):
            zip_url = asset["browser_download_url"]
            break
    
    if not zip_url:
        print("No zip asset found in release.")
        return False
    
    # Download to temp
    app_dir = Path(__file__).parent
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / "update.zip"
        urllib.request.urlretrieve(zip_url, zip_path)
        
        print("Installing update...")
        # Extract over the current directory
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(tmpdir + "/extracted")
        
        # Copy new files over (preserve the update script itself during copy)
        extracted = Path(tmpdir) / "extracted"
        for item in extracted.rglob("*"):
            if item.is_file():
                rel = item.relative_to(extracted)
                dest = app_dir / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest)
        
        # Update version file
        VERSION_FILE.write_text(remote)
    
    print(f"Updated to version {remote}!")
    return True


if __name__ == "__main__":
    check_and_update()
