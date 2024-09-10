# Synthetic Data Generation and Model Training API

This FastAPI-based project provides an API to generate synthetic data, augment and train machine learning models, and evaluate the synthetic data. It also includes user authentication, task status tracking, and result retrieval features.

## Features

- **Synthetic Data Generation**: Generate synthetic data based on different synthesizer types.
- **Asynchronous Data Augmentation and Model Training**: Perform data augmentation and model training in the background.
- **Result Tracking**: Track the accuracy of model training using task IDs.
- **Task Status Monitoring**: Check the current status of long-running tasks such as model training.
- **User Authentication**: Register and authenticate users with JWT tokens.
- **Dependency Injection**: Uses `Dependency Injector` for service and repository management.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Task and Result Tracking](#task-and-result-tracking)
- [Contributing](#contributing)

## Installation

### Prerequisites

- Python 3.8+
- FastAPI
- PostgreSQL
- SQLAlchemy
- Dependency Injector

### Setup

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/synthetic-data-api.git
   cd synthetic-data-api
2. Create a virtual environment and install dependencies:
    ```
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
3. Set up your environment variables in a .env file at the project root:
    ```bash
    DATABASE_URL=postgresql://username:password@localhost:5432/mydatabase
    SECRET_KEY=your_secret_key
4. Run database migrations:
    ```
   alembic upgrade head
5. Start the FastAPI server:
    ```
    uvicorn app.main:app --reload

### Usage
Running Background Tasks
The /augment-and-train/ endpoint allows you to initiate long-running model training tasks in the background. You can track the status of these tasks using the /task-status/{task_id} endpoint and retrieve results using the /result/{task_id} endpoint.

* Authentication
  * POST /auth/register/: Register a new user.
  * POST /auth/login/: Log in to obtain a JWT access token.
* Synthetic Data
  * POST /generate/: Generate synthetic data.
  * POST /augment-and-train/: Start an asynchronous task for data augmentation and model training.
  * POST /evaluate/: Evaluate synthetic data.
* Task and Result Tracking
  * GET /task-status/{task_id}: Retrieve the current status of a task.
  * GET /result/{task_id}: Retrieve the result of a completed task by task ID.


## Running the Application with Docker Compose
This project includes a docker-compose.yml file that allows you to run the FastAPI app and PostgreSQL database in containers.
1. Ensure your .env file is set up with the correct values (e.g., DATABASE_URL, SECRET_KEY).
```
DATABASE_URL=postgresql://postgres:postgres@db:5432/postgres
SECRET_KEY=your_secret_key
```
2. Build and start the services using Docker Compose:
```
docker-compose up --build
```
This will start the following services:

FastAPI app: Accessible on http://localhost:8003
PostgreSQL database: Running in a separate container on port 5432.