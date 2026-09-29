# Multi-Agent Research Assistant

Welcome to the **Multi-Agent Research Assistant**! This is my final project.

## Overview

This application is a self-hostable research assistant that uses specialized AI agents to:
- Search the web and analyze documents.
- Gather evidence and provide precise, verifiable citations for every claim.
- Draft comprehensive research reports.
- Include a human-in-the-loop approval system, pausing for human review before finalizing any document.

## Architecture

This project is divided into the following main components:
*   **`backend/`**: The core AI logic, pipeline execution, and API server built in Python.
*   **`frontend/`**: The web-based user interface.
*   **`desktop/`**: A native desktop application wrapper.

## Setup & Running Locally

1. Create an environment file (`.env`) based on `.env.example`.
2. To boot up the infrastructure (Postgres, Redis), run:
   ```bash
   docker compose up -d
   ```
3. Boot the API and frontend according to their individual directory setups.

---
*Created by Shikhar Singh for the Final Project.*
