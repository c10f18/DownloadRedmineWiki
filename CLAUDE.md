# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DownloadRedmineWiki is a Python GUI application built with tkinter that downloads wiki pages from Redmine projects via API and converts them to Markdown files. The application supports both single project downloads and bulk downloads of all accessible projects with two authentication methods (API Key or Username/Password).

## Development Environment

- **Python Version**: 3.12+ recommended
- **Virtual Environment**: Located in `.venv/` directory (optional)
- **Cross-platform**: Works on Windows, macOS, and Linux

## Development Commands

### Virtual Environment
- **Activate environment**: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Unix-like)
- **Deactivate environment**: `deactivate`

### Package Management
- **Install packages**: `python -m pip install <package_name>`
- **Install from requirements**: `python -m pip install -r requirements.txt` (when requirements.txt exists)

### Running Code
- **Run main application**: `python main.py`
- **Install dependencies**: `python -m pip install -r requirements.txt`
- **Run from virtual environment**: Ensure virtual environment is activated first

## Project Structure

- `main.py` - Main application file containing the GUI and core functionality
- `requirements.txt` - Python dependencies (requests library)
- `.venv/` - Python virtual environment
- `.idea/` - IntelliJ IDEA project configuration
- `DownloadRedmineWiki.iml` - IntelliJ module file
- `.claude/` - Claude Code configuration

## Application Features

- **GUI Interface**: Built with tkinter for user-friendly operation
- **Dual Authentication**: Supports both API Key and Username/Password authentication
- **Two Download Modes**:
  - Single project: Select and download one specific project's wiki
  - All projects: Download wiki pages from all accessible projects
- **Real-time Progress**: Progress bar and detailed logging during downloads
- **Cancellation Support**: Can cancel downloads in progress
- **Markdown Conversion**: Converts Redmine wiki pages to .md files
- **File Management**: Creates organized folder structures for downloaded content
- **Auto-dependency Install**: Automatically installs required packages if missing
- **Cross-platform**: Works on Windows, macOS, and Linux

## Building Executable

Use PyInstaller to create standalone executable:
```bash
# Run build script
python build.py
# Or use batch file (Windows)
build.bat
# Or manual command
pyinstaller --onefile --windowed --name "RedmineWikiDownloader" --icon=favicon.ico main.py
```

## API Endpoints Used

- `GET /projects.xml` - List all projects (with auth params)
- `GET /projects/{identifier}/wiki/index.xml` - Get wiki page list for a project
- `GET /projects/{identifier}/wiki/{title}.xml` - Get individual wiki page content