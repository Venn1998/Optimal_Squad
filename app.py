from flask import Flask, render_template, request, jsonify
from ILP import concave_ILP
from utils import read_data
import pandas as pd

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/eval')
def eval_page():
    players = read_data()
    return render_template('eval.html', players=players)


@app.route('/run_ilp', methods=['POST'])
def run_ilp_route():
    data = request.get_json()
    beta = float(data.get('beta', 0.5))
    budget = int(data.get('budget', 450))

    edited_players = data.get('players')

    if edited_players:
        # If player data is edited, we use it
        all_players_df = pd.DataFrame(read_data())

        edited_df = pd.DataFrame(edited_players)

        # Update the main players dataframe with the edited values
        all_players_df.set_index('name', inplace=True)
        edited_df.set_index('name', inplace=True)

        all_players_df.update(edited_df)

        players = all_players_df.reset_index().to_dict('records')
    else:
        # Otherwise, we read the data from the files
        players = read_data()

    try:
        result = concave_ILP(players, beta=beta, budget=budget)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

def evaluate_squad_from_names(squad_names):
    data = read_data()
    squad_players = []
    total_fantamedia = 0
    total_price = 0
    total_pr_exp = 0

    for player_name in squad_names:
        for p in data:
            if p['name'] == player_name:
                squad_players.append(p)
                total_fantamedia += p['fmv_exp']
                total_price += p['price']
                total_pr_exp += p['pr_exp']
                break
    
    return {
        "squad": squad_players,
        "total_fantamedia": total_fantamedia,
        "total_price": total_price,
        "avg_pr_exp": total_pr_exp / 11 if squad_names else 0
    }

@app.route('/run_eval', methods=['POST'])
def run_eval_route():
    data = request.get_json()
    squad_names = data.get('players', [])

    if len(squad_names) != 11:
        return jsonify({"error": "Please select exactly 11 players."}), 400

    evaluation = evaluate_squad_from_names(squad_names)
    return jsonify(evaluation)


if __name__ == '__main__':
    app.run(debug=True)
