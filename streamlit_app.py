
import streamlit as st
from ILP import concave_ILP
from utils import read_data
import pandas as pd

st.set_page_config(layout="wide")

def evaluate_squad_from_names(squad_names, data):
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

def optimal_squad_page():
    st.title("Optimal Squad Finder")

    st.sidebar.header("Parameters")
    budget = st.sidebar.number_input("Budget", min_value=1, max_value=1000, value=450, help="Total budget for the starting 11 players.")
    beta = st.sidebar.slider("Beta Value", min_value=0.0, max_value=1.0, value=0.5, step=0.1, help="Penalty for low expected appearances. 0 = no penalty, 1 = linear penalty.")

    if st.sidebar.button("Find Optimal Squad"):
        players = read_data()
        try:
            with st.spinner("Calculating..."):
                result = concave_ILP(players, beta=beta, budget=budget)
            
            st.subheader("Optimal Squad")
            
            squad_df = pd.DataFrame(result['squadra'])
            st.dataframe(squad_df[['name', 'role', 'fmv_exp', 'price', 'pr_exp']])

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Score", f"{result['totale_score']:.2f}")
            col2.metric("Total Cost", result['costo'])
            col3.metric("Total FMV", f"{result['fantamedia_tot']:.2f}")

        except ValueError as e:
            st.error(f"Error: {e}")

def squad_evaluator_page():
    st.title("Squad Evaluator")
    
    players = read_data()
    player_names = [p['name'] for p in players]

    selected_players = st.multiselect("Select 11 players for your squad:", player_names)

    if st.button("Evaluate Squad"):
        if len(selected_players) != 11:
            st.warning("Please select exactly 11 players.")
        else:
            evaluation = evaluate_squad_from_names(selected_players, players)
            
            st.subheader("Squad Evaluation")
            squad_df = pd.DataFrame(evaluation['squad'])
            st.dataframe(squad_df[['name', 'role', 'fmv_exp', 'price', 'pr_exp']])

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Fantamedia (FMV)", f"{evaluation['total_fantamedia']:.2f}")
            col2.metric("Total Price", evaluation['total_price'])
            col3.metric("Average Expected Presence (%)", f"{evaluation['avg_pr_exp']:.2f}")


PAGES = {
    "Optimal Squad Finder": optimal_squad_page,
    "Squad Evaluator": squad_evaluator_page,
}

st.sidebar.title('Navigation')
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
page = PAGES[selection]
page()
