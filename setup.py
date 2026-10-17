#!/usr/bin/env python3
"""
Impeccable Live Mode Setup App
Quickly set up live mode for any website project.

Usage:
  python setup.py /path/to/project
  python setup.py /path/to/project.zip

What it does:
1. Detects the framework (Vite, Next.js, etc.)
2. Creates .impeccable/live/config.json
3. Scans for design tokens and generates DESIGN.md
4. Creates a PRODUCT.md template
5. Copies impeccable scripts
6. Prints ready-to-run instructions
"""

import json
import os
import re
import shutil
import sys
import zipfile
from pathlib import Path


def detect_framework(project_root):
    """Detect the framework from package.json and file structure."""
    pkg_path = project_root / "package.json"
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text())
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            scripts = pkg.get("scripts", {})
            
            if "next" in deps:
                # Check for App Router vs Pages
                if (project_root / "app" / "layout.tsx").exists() or (project_root / "app" / "layout.js").exists():
                    return "nextjs-app"
                return "nextjs-pages"
            if "nuxt" in deps or "@nuxt/kit" in deps:
                return "nuxt"
            if "@sveltejs/kit" in deps:
                return "sveltekit"
            if "@tanstack/react-start" in deps:
                return "tanstack-start"
            if "@tanstack/react-router" in deps:
                return "tanstack-router"
            if "astro" in deps:
                return "astro"
            if "vite" in deps:
                return "vite-spa"
        except:
            pass
    
    # Fallback: check file structure
    if (project_root / "src" / "routes" / "__root.tsx").exists():
        return "tanstack-start"
    if (project_root / "index.html").exists():
        return "vite-spa"
    
    return "unknown"


def get_live_config(framework):
    """Get live config for the framework."""
    configs = {
        "vite-spa": (["index.html"], "</body>", "html"),
        "tanstack-router": (["index.html"], "</body>", "html"),
        "nextjs-app": (["app/layout.tsx"], "</body>", "jsx"),
        "nextjs-pages": (["pages/_document.tsx"], "</body>", "jsx"),
        "nuxt": (["app.vue"], "</body>", "html"),
        "sveltekit": (["src/app.html"], "</body>", "html"),
        "tanstack-start": (["src/routes/__root.tsx"], "<Scripts", "jsx"),
        "astro": (["src/layouts/Layout.astro"], "</body>", "html"),
    }
    if framework in configs:
        files, insert_before, comment_syntax = configs[framework]
        return {
            "files": files,
            "insertBefore": insert_before,
            "commentSyntax": comment_syntax,
            "cspChecked": True
        }
    return None


def scan_design_tokens(project_root):
    """Scan for CSS custom properties and extract design tokens."""
    tokens = {"colors": {}, "fonts": {}, "radius": {}}
    
    # Find CSS files
    css_files = list(project_root.rglob("*.css"))
    css_files = [f for f in css_files if "node_modules" not in str(f)][:5]
    
    for css_file in css_files:
        try:
            content = css_file.read_text()
            # Find :root block
            root_match = re.search(r':root\s*\{([^}]+)\}', content, re.DOTALL)
            if root_match:
                root_content = root_match.group(1)
                # Extract custom properties
                for match in re.finditer(r'--([\w-]+)\s*:\s*([^;]+);', root_content):
                    name, value = match.groups()
                    value = value.strip()
                    if any(kw in name for kw in ["color", "background", "foreground", "primary", "accent", "mint", "gold"]):
                        tokens["colors"][name] = value
                    elif "font" in name:
                        tokens["fonts"][name] = value
                    elif "radius" in name:
                        tokens["radius"][name] = value
        except:
            continue
    
    return tokens


def create_product_template(project_root, project_name):
    """Create a PRODUCT.md template."""
    template = f"""# PRODUCT.md — {project_name}

## Purpose
[What does this product do? One sentence.]

## Users
- [Who is the primary user?]
- [What situation are they in?]

## Core loop
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Differentiator
[What makes this different from alternatives?]

## Platform
- Web: [URL if live]

## Constraints
- [Any hard constraints]

## Voice
[How does the product sound? e.g. "Energetic, playful"]
"""
    (project_root / "PRODUCT.md").write_text(template)
    return project_root / "PRODUCT.md"


def create_design_md(project_root, project_name, tokens):
    """Create DESIGN.md from scanned tokens."""
    colors_yaml = "\n".join(f'  {k}: "{v}"' for k, v in list(tokens["colors"].items())[:12])
    if not colors_yaml:
        colors_yaml = '  background: "#ffffff"\n  foreground: "#000000"'
    
    fonts_yaml = ""
    if tokens["fonts"]:
        for k, v in list(tokens["fonts"].items())[:4]:
            fonts_yaml += f'  {k}: "{v}"\n'
    else:
        fonts_yaml = '  body: "system-ui, sans-serif"\n'
    
    content = f"""---
name: {project_name}
description: [One-line tagline]
colors:
{colors_yaml}
typography:
{fonts_yaml}---

# Design System: {project_name}

## Overview
[2-3 sentences describing the visual personality. Update after reviewing the site.]

## Colors
[Describe the palette.]

## Typography
[Describe the font pairing.]

## Layout
[Describe the spatial model.]

## Elevation & Depth
[Shadows or tonal layering?]

## Shapes
[Corner radius strategy.]

## Components
### Buttons
[Describe button styles.]

## Do's and Don'ts
### Do:
- **Do** [prescription]

### Don't:
- **Don't** [prohibition]
"""
    (project_root / "DESIGN.md").write_text(content)
    return project_root / "DESIGN.md"


def main():
    if len(sys.argv) < 2:
        print("Usage: python setup.py /path/to/project-or-zip")
        print("       python setup.py /path/to/project.zip")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    script_dir = Path(__file__).parent
    
    # Handle zip file
    if input_path.suffix == ".zip":
        print(f"Extracting {input_path}...")
        extract_dir = input_path.parent / input_path.stem
        with zipfile.ZipFile(input_path, 'r') as z:
            z.extractall(extract_dir)
        # Find the actual project root (might be nested)
        project_root = extract_dir
        # If there's a single subdirectory, use it
        subdirs = [d for d in extract_dir.iterdir() if d.is_dir()]
        if len(subdirs) == 1 and not (extract_dir / "package.json").exists():
            project_root = subdirs[0]
        print(f"Project root: {project_root}")
    else:
        project_root = input_path
    
    if not project_root.exists():
        print(f"Error: {project_root} does not exist")
        sys.exit(1)
    
    project_name = project_root.name
    
    print(f"\nSetting up live mode for: {project_name}")
    print("=" * 50)
    
    # 1. Detect framework
    framework = detect_framework(project_root)
    print(f"Framework: {framework}")
    
    # 2. Create live config
    config = get_live_config(framework)
    if config:
        config_dir = project_root / ".impeccable" / "live"
        config_dir.mkdir(parents=True, exist_ok=True)
        (config_dir / "config.json").write_text(json.dumps(config, indent=2))
        print(f"Created: .impeccable/live/config.json")
    else:
        print("Warning: Could not detect framework. Manual config needed.")
        print("See: https://github.com/pbakaus/impeccable for config options")
    
    # 3. Scan design tokens
    print("Scanning for design tokens...")
    tokens = scan_design_tokens(project_root)
    print(f"  Found {len(tokens['colors'])} colors, {len(tokens['fonts'])} fonts")
    
    # 4. Create DESIGN.md if not exists
    design_path = project_root / "DESIGN.md"
    if not design_path.exists():
        create_design_md(project_root, project_name, tokens)
        print(f"Created: DESIGN.md (review and update the prose sections)")
    else:
        print(f"Exists: DESIGN.md (skipped)")
    
    # 5. Create PRODUCT.md template if not exists
    product_path = project_root / "PRODUCT.md"
    if not product_path.exists():
        create_product_template(project_root, project_name)
        print(f"Created: PRODUCT.md (fill in the product details)")
    else:
        print(f"Exists: PRODUCT.md (skipped)")
    
    # 6. Copy scripts
    scripts_src = script_dir / "scripts"
    if scripts_src.exists():
        scripts_dest = project_root / ".impeccable" / "scripts"
        if not scripts_dest.exists():
            shutil.copytree(scripts_src, scripts_dest)
            print(f"Copied: scripts to .impeccable/scripts")
        else:
            print(f"Exists: .impeccable/scripts (skipped)")
    
    print("\n" + "=" * 50)
    print("Setup complete!")
    print("\nNext steps:")
    print("1. Fill in PRODUCT.md with your product details")
    print("2. Review DESIGN.md and update the prose sections")
    print("3. Start your dev server (e.g. `npm run dev`)")
    print("4. Run: `.impeccable/scripts/impeccable live` (or `impeccable.cmd live` on Windows)")
    print("5. Open your dev server URL in the browser and pick elements to edit")


if __name__ == "__main__":
    main()
