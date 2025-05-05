# Temporal PoC Demo Project

This project demonstrates a basic Temporal workflow using Python.

## Prerequisites

Before you begin, ensure you have the following installed:

1.  **Homebrew:** If you don't have Homebrew, install it by following the instructions at [https://brew.sh/](https://brew.sh/).

2.  **pyenv:** Install `pyenv` to manage Python versions.
    ```bash
    brew update
    brew install pyenv
    ```
    Configure your shell environment for `pyenv` according to the instructions provided by `brew postinstall pyenv` or the official `pyenv` documentation.

3.  **Python 3.13:** Install Python 3.13 using `pyenv`.
    ```bash
    pyenv install 3.13
    pyenv global 3.13
    ```

4.  **Poetry:** Install `poetry` for dependency management.
    ```bash
    brew install pipx 
    pipx install poetry
    ```

5.  **Temporal CLI:** Install the Temporal command-line tool.

    ```bash
    brew install temporal
    ```

    For more details, refer to the [Temporal documentation](https://learn.temporal.io/getting_started/python/dev_environment/).

## Project Setup

1.  **Clone the repository (if applicable):**

    ```bash
    # git clone <your-repo-url>
    cd temporal_poc # Or your project directory
    ```

2.  **Set the Python version for Poetry:**
    Ensure you are in the project directory. Tell Poetry to use the Python 3.13 version installed via `pyenv`.

    ```bash
    poetry env use 3.13
    ```

    Alternatively, if `pyenv` is correctly configured in your shell and `3.13` is available globally or locally:

    ```bash
    poetry env use 3.13
    ```

3.  **Install dependencies:**
    Install the project dependencies using Poetry. This will create a virtual environment if one doesn't exist.

    ```bash
    poetry install
    ```

## Running the Demo

1.  **Start the Temporal Development Server:**
    Open a terminal window and run the Temporal development server. This server uses an in-memory store by default, so data will be lost when it's stopped unless you configure persistence (see Temporal docs).
    ```bash
    temporal server start-dev
    ```
    Keep this terminal window open. The server will be available at `localhost:7233` and the Web UI at `http://localhost:8233`.

2.  **Run the Worker:**
    Open a *new* terminal window, navigate to the project directory, and activate the Poetry virtual environment:
    ```bash
    poetry shell
    ```
    Then, start the worker:
    ```bash
    python run_worker.py
    ```
    Keep this terminal window open.

3.  **Run Mock Server:**
    Open a *thidr* terminal window, navigate to the project directory, and activate the Poetry virtual environment:
    ```bash
    poetry shell
    ```
    Then, run the script that starts the mockserver:
    ```bash
    python run_mockserver.py
    ```

4.  **Run the Workflow Starter:**
    Open a *fourth* terminal window, navigate to the project directory, and activate the Poetry virtual environment:
    ```bash
    poetry shell
    ```
    Then, run the script that starts the workflow:
    ```bash
    python run_workflow.py
    ```
    You can run this multiple times to simulate new transactions.

You should now see the workflow executing, with logs appearing in the worker terminal and the workflow starter terminal confirming the start. You can monitor the workflow progress via the Temporal Web UI at `http://localhost:8233`.


## How it works
- mockserver has 3 endpoints with minimal chaos engineering
- each endpoint has 20% chance to respond with 400 error
- workflow activities assume that each error (4xx and 5xx) is retryable
- workflow tries to validate wallet, authorize card and then send crypto. If any of the steps fails it's automatically handled and retried according to the policy
- you can shut down worker process and restart. Workflow will resume at the same place
- whole business logic lays in activities

## Reference material
https://learn.temporal.io/getting_started/python/
