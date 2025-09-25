import pandas as pd

# Supponiamo che i CSV abbiano almeno queste colonne:
# Nome, Prezzo, Fantamedia
# e che ogni file contenga solo giocatori di un ruolo

files = {
    "P": "data/Asta 2025 - POR.csv",
    "D": "data/Asta 2025 - DIF.csv",
    "C": "data/Asta 2025 - CEN.csv",
    "A": "data/Asta 2025 - ATT.csv"
}


def read_data(files=files):

    dfs = []
    for role, path in files.items():
        df = pd.read_csv(path, sep='\t' if '\t' in open(
            path).read(1000) else ',', engine='python')

        df = df.rename(columns={
            "Nome": "name",
            "Pr. Exp": "pr_exp",
            "FMVexp": "fmv_exp",
            "Prz mio": "price"
        })

        df = df.drop(columns=[col for col in df.columns if col not in [
                     "name", "pr_exp", "fmv_exp", "price"]], errors='ignore')

        # Aggiungi ruolo
        df["role"] = role

        if role == "P":
            # if in column "pr_exp" we have NaN, we input 100
            df["pr_exp"] = df["pr_exp"].fillna(100.0)

        # Droppa eventuali righe senza dati utili
        df = df.dropna(subset=["name", "fmv_exp", "price"])

        # price is an integer
        df["price"] = df["price"].astype(int)

        dfs.append(df)

    # Unisci tutto
    players_df = pd.concat(dfs, ignore_index=True)

    # Lista di dizionari (utile per ILP)
    players = players_df.to_dict(orient="records")

    # save to a csv file
    players_df.to_csv("data/players_processed.csv", index=False)

    return players


if __name__ == '__main__':
    read_data()
