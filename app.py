from flask import Flask, render_template, request, jsonify, session, send_from_directory, redirect, url_for
from ILP import concave_ILP
from utils import read_data
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

UPLOAD_FOLDER = 'data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html', uploaded_file=session.get('uploaded_file_name'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and file.filename.endswith('.csv'):
        filename = 'temp_players.csv'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        session['uploaded_file_name'] = filename
        session['uploaded_file_path'] = filepath
    return redirect(url_for('index'))

@app.route('/clear')
def clear_upload():
    if 'uploaded_file_path' in session:
        if os.path.exists(session['uploaded_file_path']):
            os.remove(session['uploaded_file_path'])
        session.pop('uploaded_file_name', None)
        session.pop('uploaded_file_path', None)
    return redirect(url_for('index'))

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

    if 'uploaded_file_path' in session:
        players = pd.read_csv(session['uploaded_file_path']).to_dict('records')
    elif edited_players:
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
