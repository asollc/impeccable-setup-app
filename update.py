#!/usr/bin/env python3
"""
Auto-updater for Impeccable Setup App.
Checks GitHub for a new version and updates if available.
Safe for Windows: stages update and applies via separate batch.
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
    url = f"https://api.github.com/repos/{REPO}/releases/latest"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "impeccable-setup-app"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
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
    
    # On Windows, we can't overwrite running files, so stage the update
    # in SYSTEM TEMP (never inside app_dir to avoid nesting bugs)
    if os.name == "nt":
        print("Downloading update...")
        zip_url = f"https://github.com/{REPO}/archive/refs/tags/v{remote}.zip"
        
        app_dir = Path(__file__).parent
        
        # Clean up ALL old staging dirs inside app_dir (from buggy versions)
        for _ in range(5):
            found = list(app_dir.rglob(".update_staged"))
            if not found:
                break
            # Deepest first
            for p in sorted(found, key=lambda x: len(str(x)), reverse=True):
                try:
                    shutil.rmtree(p)
                except:
                    pass
        
        # Stage in system temp, versioned by remote version
        stage_base = Path(tempfile.gettempdir()) / "impeccable_updates"
        stage_base.mkdir(exist_ok=True)
        stage_dir = stage_base / f"v{remote}"
        if stage_dir.exists():
            shutil.rmtree(stage_dir, ignore_errors=True)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "update.zip"
            try:
                urllib.request.urlretrieve(zip_url, zip_path)
            except Exception as e:
                print(f"Download failed: {e}")
                return False
            
            print("Staging update...")
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(tmpdir + "/extracted")
            
            extracted = Path(tmpdir) / "extracted"
            subdirs = [d for d in extracted.iterdir() if d.is_dir()]
            if len(subdirs) == 1:
                extracted = subdirs[0]
            
            # Copy to staging
            if stage_dir.exists():
                shutil.rmtree(stage_dir)
            shutil.copytree(extracted, stage_dir)
            
            # Create apply script
            apply_bat = app_dir / "apply_update.bat"
            apply_content = f"""@echo off
echo Applying update to {remote}...
echo From: {stage_dir}
echo To: {app_dir}
xcopy /E /Y "{stage_dir}" "{app_dir}\\"
if errorlevel 1 (
    echo ERROR: Copy failed with code %errorlevel%
    pause
    exit /b 1
)
rmdir /S /Q "{stage_dir}"
del "%~f0"
echo Update complete! Version {remote} installed.
"""
            apply_bat.write_text(apply_content)
        
        print(f"\nUpdate downloaded. Run apply_update.bat to install version {remote}.")
        print("The current operation will continue with the old version.")
        return False  # Don't block current operation
    else:
        # Unix: can overwrite in place
        print("Downloading...")
        zip_url = f"https://github.com/{REPO}/archive/refs/tags/v{remote}.zip"
        app_dir = Path(__file__).parent
        
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "update.zip"
            urllib.request.urlretrieve(zip_url, zip_path)
            
            print("Installing update...")
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(tmpdir + "/extracted")
            
            extracted = Path(tmpdir) / "extracted"
            subdirs = [d for d in extracted.iterdir() if d.is_dir()]
            if len(subdirs) == 1:
                extracted = subdirs[0]
            
            for item in extracted.rglob("*"):
                if item.is_file():
                    rel = item.relative_to(extracted)
                    dest = app_dir / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest)
            
            VERSION_FILE.write_text(remote)
        
        print(f"Updated to version {remote}!")
        return True


if __name__ == "__main__":
    check_and_update()
