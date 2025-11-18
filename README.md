# Job Hunting AI Web Tool

Structure follows the spec in `job_ai_tech_design.md`.

See `frontend/` and `backend/` folders for implementation.

## Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Setting Up Python Virtual Environment](#venv)
- [Install Requirements](#reqs)
- [Update .env](#env)
- [Set PYTHONPATH and Start the Server](#start)
- [Formatting and Linting](#formatting)
- [Contributors](#contributors)
- [README Citation](#citation)

## Overview<a name="overview"></a>

The Job Hunting AI Web Tool is an intelligent, data-driven job search platform designed to improve how users discover and match with employment opportunities. Unlike traditional job boards that rely solely on keyword matching, this platform integrates AI-powered text analysis and semantic similarity to provide personalized job recommendations that correlate closely with users' skills, education, and preferences.

Our tool aims to reduce the time, effort, and uncertainty involved in job hunting by learning from both user-provided criteria and real-world job data. The system will be fully interactive and web-based, allowing users to input preferences (skills, location, keywords) and receive ranked, relevant job listings fetched via APIs from available sources.

Given the school term timeline with 10 hours per person per week, this project focuses on delivering a functional MVP (Minimum Viable Product) that demonstrates core AI matching capabilities with a clean, usable interface.

## Requirements<a name="requirements"></a>

- Python 3.9+
- VSCode Recommended

## Setting Up Python Virtual Environment<a name="venv"></a>

It is recommended that you use a Python virtual environment for this (and all) Python projects.

### 1. Creating a Python Virtual Environment

#### Windows, macOS, and Linux

1. Launch Command Prompt, PowerShell, or your terminal emulator

2. Enter the following command to ensure you have the correct version of Python installed:

   ```bash
   python --version
   ```

   > Depending on your Python configuration, you may need to enter the following command instead:

   ```bash
   python3 --version
   ```

   > Keep track of which command works, and use it for each after this. For brevity, only `python` will be shown in examples.

3. Enter the following command to create a virtual environment named `env`:

   ```bash
   python -m venv env
   ```

   > Optionally, you may specify the Python version for the virtual environment:

   ```bash
   py -3.9 -m venv env
   ```

### 2. Activate the Virtual Environment

#### VSCode

1. Open the Command Palette and select `Python: Select Interpreter`
2. Select the interpreter located in the virtual environment `('env':venv)`
3. Reload your terminal

#### Windows

- In the PowerShell or Command Prompt, enter the following command to activate the virtual environment:
  ```
  cd env\Scripts\
  .\activate
  cd ..\..
  ```

#### macOS and Linux

- In the terminal, enter the following command to activate the virtual environment:
  ```sh
  source env/bin/activate
  ```

## Install Requirements<a name="reqs"></a>

- Within the virtual environment, enter the following command into the terminal to install all requirements. For all future commands it is assumed that they will be executed from within the virtual environment.

  ```bash
  python -m pip install -U -r backend/requirements.txt
  ```

- **Download the ML model** (required for semantic job matching):
  ```bash
  python backend/download_model.py
  ```
  This downloads the sentence-transformers model (~82MB) to cache directory (`~/.cache/torch/sentence_transformers/`). Running this step before starting the app avoids download delays and connection timeouts during the first request.

## Update .env<a name="env"></a>

- The included `.env.example` file must be updated with appropriate values, and renamed to `.env`

## Set PYTHONPATH and Start the Server<a name="start"></a>
Run the server (development vs production)

- Development (local, no forking):

  - Ensure the repo root is on `PYTHONPATH`:

    ```bash
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    ```

  - Start the Flask app in the foreground (recommended for debugging):

    ```bash
    FLASK_DEBUG=0 python -m backend.app
    ```

- Production (Gunicorn):

  - Start with a WSGI entrypoint (`wsgi.py`) and Gunicorn:

    ```bash
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    gunicorn --bind 0.0.0.0:8000 wsgi:app --workers 3 --log-level info
    ```

  - Replace `8000` with your desired port. Avoid `--preload` unless you understand master-process model loading.

Notes and troubleshooting

- macOS users: PyTorch's MPS/Metal backend can be unstable when used inside forked worker processes (Gunicorn). For local development prefer the Flask foreground server above or run inside a Linux container. If you see worker crashes or `ERR_EMPTY_RESPONSE` in the browser, try `FLASK_DEBUG=0 python -m backend.app` or run the service in Docker/Linux.
- If you need cross-origin requests during development, enable CORS in `backend/app.py` (use `flask-cors`) and restrict origins for production.

## Formatting and Linting<a name="formatting"></a>

This project uses black for formatting, and flake8 for linting.

- To run black:

  ```bash
  black .
  ```

- To run flake8:
  ```bash
  flake8 .
  ```

## Contributors<a name="contributors"></a>

- Team Member 1 Eduardo Camacho-Lopez – `Team Leader & Integration Lead`
- Team Member 2 Wei-Yin Chen – `Machine Learning / Data Lead`
- Team Member 3 Khoi Le – `Web Development Lead`
- Team Member 4 Ian Bubier – `Backend & Testing Lead`

## README Citation<a name="citation"></a>

README portions ([Requirements](#requirements), [Setting Up Python Virtual Environment](#venv), [Install Requirements](#reqs)) were reused from a previous project.

- URL - https://github.com/coopeaus/cs340_project/blob/main/README.md
- Date retrieved - 10/13/2025
- Title - CS340 project
- Type - source code
- Author - Austin Cooper
- Code version - N/A
