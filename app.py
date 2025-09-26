from flask import Flask, render_template, request, jsonify
from ILP import concave_ILP
from utils import read_data
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_ilp', methods=['POST'])
def run_ilp_route():
    data = request.get_json()
    beta = float(data.get('beta', 1.5))
    
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
        result = concave_ILP(players, beta=beta)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
