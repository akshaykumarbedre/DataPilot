# Gemini Project: Dental App

This document provides an overview of the Dental App project structure and instructions for Gemini.

## Project Overview

This is a desktop application for dental practice management, built with Python and likely a UI framework like PyQt or PySide (based on the `.ui` files and widget structure).

## File Structure

-   **`app.py`**: The main entry point for running the application.
-   **`requirements.txt`**: A list of python dependencies required for the project.
-   **`app/`**: The core application package.
    -   **`main.py`**: Contains the primary application logic.
    -   **`config.py`**: Handles application configuration settings.
    -   **`database/`**: Manages all database interactions.
        -   `database.py`: Sets up the database connection.
        -   `models.py`: Defines the structure of database tables (ORM models).
    -   **`services/`**: Contains the business logic, with each service handling a specific domain (e.g., patients, authentication, dental examinations).
    -   **`ui/`**: Holds all user interface components.
        -   `main_window.py`: The main application window.
        -   `dashboard.py`: The main dashboard view.
        -   `dental_chart.py`: The interactive dental chart.
        -   `components/`: Reusable UI widgets and panels.
        -   `dialogs/`: Various dialog boxes used throughout the app.
    -   **`utils/`**: Common utility functions and constants.
-   **`data/`**: Contains the application's data, including the `dental_practice.db` SQLite database.
-   **`deployment/`**: Scripts and files related to building and deploying the application.
-   **`docs/`**: Project documentation.
-   **`tests/`**: Automated tests for the application.

## Development Workflow

After every code update, you must run the application for testing. I will then test the changes and provide feedback.

Use the following command to run the application:

```bash
conda activate dental && python app.py
```

## Git Commit Guidelines

When starting new major content or fine changes, commit your work using dont check git stats (git add .):

```bash
git add . && git commit -m "short descriptive comment"
```
