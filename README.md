# Rosa Ottimale - Fantasy Football Squad Optimizer

This project is a tool to help you build the best possible fantasy football team for the Italian Serie A.
It uses an Integer Linear Programming (ILP) model to select the optimal squad based on your budget and player statistics.

## How it works

The project reads player data from CSV files located in the `data/` directory. Each file contains players for a specific role (goalkeepers, defenders, midfielders, attackers).

The core of the project is the `concave_ILP` function in `ILP.py`. This function implements an optimization model that aims to maximize the total "score" of the team. The score is a combination of the player's expected fantasy points (`fmv_exp`) and their expected number of appearances (`pr_exp`). A `beta` parameter allows you to control how much to penalize players with a lower expected number of appearances.

The ILP model selects the best 11-player squad (1 Goalkeeper, 4 Defenders, 3 Midfielders, 3 Attackers) that maximizes the total score while respecting the given budget.

The project provides two interfaces:
1.  A **Streamlit web app** (`streamlit_app.py`) for an interactive experience.
2.  A **Flask-based web app** (`app.py`) which also provides an API.

## How to run it

1.  **Install dependencies:**
    Make sure you have Python installed. Then, install the required libraries using pip:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Streamlit App:**
    For an interactive web interface, run the Streamlit application:
    ```bash
    streamlit run streamlit_app.py
    ```
    This will open a new tab in your browser. You can use the sidebar to set the budget and the `beta` parameter, and then find the optimal squad or evaluate a custom squad.

3.  **Run the Flask App (Alternative):**
    To run the Flask application:
    ```bash
    python app.py
    ```
    This will start a local server, and you can access the application at `http://127.0.0.1:5000` in your browser.

## Project Structure

```
/home/lorenzovenieri/Desktop/rosa_ottimale/
├───.gitignore
├───.python-version
├───app.py                # Flask web application
├───eval_squad.py         # Script to evaluate a squad
├───ILP.py                # Core Integer Linear Programming optimization logic
├───pyproject.toml
├───README.md             # This file
├───requirements.txt      # Python dependencies
├───streamlit_app.py      # Streamlit web application
├───utils.py              # Data loading and processing utilities
├───uv.lock
├───data/
│   ├───Asta 2025 - ATT.csv   # Attackers data
│   ├───Asta 2025 - CEN.csv   # Midfielders data
│   ├───Asta 2025 - DIF.csv   # Defenders data
│   ├───Asta 2025 - POR.csv   # Goalkeepers data
│   └───players_processed.csv # Processed player data
├───results2/             # Directory to store optimization results
├───static/
│   └───style.css         # CSS for the Flask app
└───templates/
    ├───eval.html         # HTML template for squad evaluation
    └───index.html        # HTML template for the main page
```
