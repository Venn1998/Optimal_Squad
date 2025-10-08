# Rosa Ottimale: Optimal Fantasy Football Squad Generator

This project is a web-based tool to help you build the optimal squad for your fantasy football auction.

## The Problem

Many tools are available to provide valuable pre-auction information, such as:

*   **Expected Fantasy Score (FMV):** The predicted average fantasy points for each player.
*   **Expected Appearances:** The percentage of matches a player is expected to play.
*   **Expected Cost:** The likely (or average) auction price for each player.

However, knowing this information is only half the battle. The real challenge is to assemble a complete squad that maximizes your team's potential while staying within a predefined budget. This tool addresses this exact problem.

## How It Works

This tool uses Integer Linear Programming (ILP) to find the optimal squad based on your preferences. Here's a breakdown of the methodology:

1.  **Player Data:** The tool uses a dataset of players with their roles, expected fantasy scores, expected appearances, and estimated prices.
2.  **Concave Scoring:** To account for the fact that a player's value doesn't increase linearly with their expected appearances (a player who plays 90% of the games is more valuable than two players who play 45% each), the tool uses a concave scoring function. Each player is assigned a "score" calculated as:

    `score = fmv_exp * (pr_exp / 100) ^ beta`

    *   `fmv_exp`: Expected fantasy score.
    *   `pr_exp`: Expected presence rate (in %).
    *   `beta`: A parameter that you can tune to adjust the importance of the presence rate. A lower `beta` gives less importance to the presence rate, while a higher `beta` gives more importance to it.

3.  **Optimization:** The ILP model maximizes the total score of the squad, subject to the following constraints:
    *   **Budget:** The total cost of the squad must not exceed your budget.
    *   **Team Formation:** The squad must consist of a specific formation (currently hardcoded to 1 goalkeeper, 4 defenders, 3 midfielders, and 3 attackers).

## How to Use (with Docker)

Containerizing the application with Docker is the recommended way to run it, as it guarantees a consistent environment across different machines (e.g., Linux, macOS, Windows). This is especially useful for avoiding issues with binary dependencies like the CBC solver, particularly on Apple Silicon.

1.  **Prerequisite:** Ensure you have [Docker](https://www.docker.com/get-started) installed and running on your system.

2.  **Build the Docker Image:**
    Open your terminal in the project's root directory and run the following command. This will build the image and tag it as `optimal-squad`.
    ```bash
    docker build -t optimal-squad .
    ```

3.  **Run the Docker Container:**
    Once the image is built, run the container with this command:
    ```bash
    docker run -p 5000:5000 optimal-squad
    ```
    This command starts the container and maps port 5000 from the container to port 5000 on your local machine.

4.  **Access the Application:**
    Open your web browser and navigate to `http://localhost:5000`.

## How to Use (Locally)

A demo is available at https://rosa-ottimale.onrender.com/, loading could take up to 30 seconds. 

If you want to run it locally: 

1. **Just run the application with uv:**
    ```bash
    uv run app.py
    ```

    or **using pip:**

    1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

    2.  **Run the Application:**
    ```bash
    python app.py
    ```

3.  **Open the Web Interface:**
    Open your web browser and go to `http://127.0.0.1:5000/`.

4.  **Set Parameters and Run the Optimization:**
    *   Adjust the `beta` and `budget` parameters to your liking.
    *   You can also edit the player data directly in the table (e.g., to update a player's expected price based on your league's dynamics, or edit a player's expected fmv given new info).
    *   Click the "FIND OPTIMAL SQUAD" button to find the optimal squad.

5.  **Evaluate Your Squad:**
    *   Go to the "Eval" page.
    *   Select 11 players to form a squad.
    *   Click the "EVALUATE SQUAD" button to see the total fantasy score, price, and average expected appearances for your team.

## Project Structure

```
/home/lorenzovenieri/Desktop/rosa_ottimale/
├───app.py              # Flask web application
├───ILP.py              # Core ILP optimization logic
├───utils.py            # Utility functions for data reading
├───requirements.txt    # Python dependencies
├───data/                 # Player data files
├───templates/            # HTML templates for the web app
└───static/               # CSS stylesheets
```
