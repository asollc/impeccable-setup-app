# Impeccable Live Mode Setup App

Quickly set up impeccable live mode for any website project.

## What it does
1. Takes a project directory or zip file
2. Detects the framework (Vite, Next.js, Nuxt, SvelteKit, TanStack, Astro)
3. Creates `.impeccable/live/config.json` for the framework
4. Scans CSS for design tokens and generates a starter `DESIGN.md`
5. Creates a `PRODUCT.md` template
6. Copies the impeccable scripts

## Sending changes to Gigi

When you're done editing, use the pack-and-send tool:

```bash
# Double-click send.bat (Windows) or run:
python send.py /path/to/project
```

This zips your project (excluding node_modules, .git, build files) and saves it to your Desktop. Then drag the zip into your chat with Gigi and she'll push it live.

## Setup new project

```bash
# From a project directory
python setup.py /path/to/my-website

# From a zip file
python setup.py /path/to/my-website.zip
```

## After setup
1. Fill in `PRODUCT.md` with your product details
2. Review `DESIGN.md` and update the prose sections
3. Start your dev server (e.g. `npm run dev` or `vite dev`)
4. Run live mode:
   - Windows: `.impeccable\scripts\impeccable.cmd live`
   - Mac/Linux: `.impeccable/scripts/impeccable live`
5. Open your dev server URL in the browser
6. Click elements to pick them, then edit

## Requirements
- Python 3.6+
- Node.js project with a dev server (for live mode to work)
- Chromium browser

## Supported frameworks
- Vite SPA (including TanStack Router)
- TanStack Start (SSR)
- Next.js (App Router and Pages)
- Nuxt
- SvelteKit
- Astro
