import pulp
from utils import read_data

RESULTS_FOLDER = "results2/"


def simple_ILP(budget=450):
    players = read_data()

    # Definisci il problema
    prob = pulp.LpProblem("FantaOptimization", pulp.LpMaximize)

    # Variabili binarie: x[g] = 1 se il giocatore viene scelto
    x = {p["name"]: pulp.LpVariable(p["name"], cat="Binary") for p in players}

    # Obiettivo: massimizzare la somma delle fantamedie
    prob += pulp.lpSum(p["fmv_exp"] * x[p["name"]] for p in players)

    # Vincolo budget (massimo 420 crediti)
    prob += pulp.lpSum(p["price"] * x[p["name"]] for p in players) <= budget

    # Vincoli per ruolo
    prob += pulp.lpSum(x[p["name"]] for p in players if p["role"] == "P") == 1
    prob += pulp.lpSum(x[p["name"]] for p in players if p["role"] == "D") == 4
    prob += pulp.lpSum(x[p["name"]] for p in players if p["role"] == "C") == 3
    prob += pulp.lpSum(x[p["name"]] for p in players if p["role"] == "A") == 3

    # Risolvi
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    # Estrai la squadra ottimale
    squadra = [p for p in players if pulp.value(x[p["name"]]) == 1]
    fantamedia_tot = sum(p["fmv_exp"] for p in squadra)
    costo_tot = sum(p["price"] for p in squadra)

    # Stampa risultato
    print("Squadra ottimale:")
    for p in squadra:
        print(
            f"{p['name']} ({p['role']}) - Prezzo: {p['price']} - FMV: {p['fmv_exp']} - Pr. Exp: {p['pr_exp']}")

    print("\nFantamedia totale:", fantamedia_tot)
    print("Costo totale:", costo_tot)


def ILP_presenze():
    players = read_data()

    # Filtra giocatori con almeno 50% di presenze attese
    players = [p for p in players if p["pr_exp"] >= 50]

    # Aggiungi campo "expected_points"
    for p in players:
        p["expected_points"] = p["fmv_exp"] * (p["pr_exp"] / 100) * 38

    # Definisci il problema
    prob = pulp.LpProblem("FantaOptimization", pulp.LpMaximize)

    # Variabili binarie: x[g] = 1 se il giocatore viene scelto
    x = {p["name"]: pulp.LpVariable(p["name"], cat="Binary") for p in players}

    # Obiettivo: massimizzare i punti attesi totali
    prob += pulp.lpSum(p["expected_points"] * x[p["name"]] for p in players)

    # Vincolo budget (massimo 420 crediti)
    prob += pulp.lpSum(p["price"] * x[p["name"]] for p in players) <= 420

    # Vincoli per ruolo
    prob += pulp.lpSum(x[p["name"]] for p in players if p["role"] == "P") == 1
    prob += pulp.lpSum(x[p["name"]] for p in players if p["role"] == "D") == 4
    prob += pulp.lpSum(x[p["name"]] for p in players if p["role"] == "C") == 3
    prob += pulp.lpSum(x[p["name"]] for p in players if p["role"] == "A") == 3

    # Risolvi
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    # Estrai la squadra ottimale
    squadra = [p for p in players if pulp.value(x[p["name"]]) == 1]
    punti_tot = sum(p["expected_points"] for p in squadra)
    costo_tot = sum(p["price"] for p in squadra)

    # Stampa risultato
    print("Squadra ottimale (con punti attesi):")
    for p in squadra:
        print(
            f"{p['name']} ({p['role']}) - Prezzo: {p['price']} "
            f"- FMVexp: {p['fmv_exp']} - Pr. Exp: {p['pr_exp']} "
            f"- Punti Attesi: {p['expected_points']:.1f}"
        )

    fantamedia_tot = sum(p["fmv_exp"] for p in squadra)

    print("\nTotale punti attesi:", round(punti_tot, 1))
    print("Fantamedia totale (se giocassero tutti):", fantamedia_tot)
    print("Costo totale:", costo_tot)


def concave_ILP(players, budget=450, beta=1.5, pr_cutoff=50):
    """
    players: lista di dict con keys: name, role (P/D/C/A), price, fmv_exp, pr_exp
    beta: parametro concavità (0<beta<=1). Più basso = meno importanza alle presenze.
    pr_cutoff: considera solo giocatori con pr_exp >= cutoff
    """
    # filtro cutoff
    players = [p for p in players if p.get("pr_exp", 0) >= pr_cutoff]
    if not players:
        raise ValueError(f"Nessun giocatore dopo cutoff pr_exp >= {pr_cutoff}")

    # calcola punteggio concavo
    for p in players:
        weight = (p["pr_exp"] / 100.0) ** beta
        p["score"] = p["fmv_exp"] * weight

    # ILP
    prob = pulp.LpProblem("FantaConcave", pulp.LpMaximize)
    x = {p["name"]: pulp.LpVariable(p["name"], cat="Binary") for p in players}

    # obiettivo: somma degli score
    prob += pulp.lpSum(p["score"] * x[p["name"]] for p in players)

    # vincolo budget
    prob += pulp.lpSum(p["price"] * x[p["name"]] for p in players) <= budget

    # vincoli ruolo (1P,4D,3C,3A)
    prob += pulp.lpSum(x[p["name"]] for p in players if p["role"] == "P") == 1
    prob += pulp.lpSum(x[p["name"]] for p in players if p["role"] == "D") == 4
    prob += pulp.lpSum(x[p["name"]] for p in players if p["role"] == "C") == 3
    prob += pulp.lpSum(x[p["name"]] for p in players if p["role"] == "A") == 3

    # risolvi
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    # estrai squadra
    squadra = [p for p in players if pulp.value(x[p["name"]]) == 1]
    totale_score = sum(p["score"] for p in squadra)
    costo = sum(p["price"] for p in squadra)
    fantamedia_tot = sum(p["fmv_exp"] for p in squadra)

    print("Squadra ottimale (concave ILP):")
    print(f"{'Giocatore':<20} {'FMV':<8} {'Costo':<8} {'Pr. Exp':<10}")
    print("-" * 50)
    for p in squadra:
        print(
            f"{p['name']:<20} {p['fmv_exp']:<8.2f} {p['price']:<8} {p['pr_exp']:<9.1f}%")
    print("\nTotale score:", round(totale_score, 2))
    print("Fantamedia totale (se giocassero tutti):", fantamedia_tot)
    print("Costo totale:", costo)
    print(
        f"Percentuale spesa attaccanti: {sum(p['price'] for p in squadra if p['role'] == 'A')/500*100:.1f}%")
    print(
        f"Percentuale spesa centrocampisti: {sum(p['price'] for p in squadra if p['role'] == 'C')/500*100:.1f}%")
    print(
        f"Percentuale spesa difensori: {sum(p['price'] for p in squadra if p['role'] == 'D')/500*100:.1f}%")
    print(
        f"Percentuale spesa portiere: {sum(p['price'] for p in squadra if p['role'] == 'P')/500*100:.1f}%")

    # write everything to a file
    with open(f"{RESULTS_FOLDER}/results_concave_ILP_beta{beta}_pr{pr_cutoff}.txt", "w") as f:
        f.write("Squadra ottimale (concave ILP):\n")
        for p in squadra:
            f.write(
                f"{p['name']} ({p['role']}) - Prezzo: {p['price']} "
                f"- FMVexp: {p['fmv_exp']} - Pr. Exp: {p['pr_exp']} "
                f"- Score: {p['score']:.2f}\n"
            )
        f.write(f"\nTotale score: {round(totale_score, 2)}\n")
        f.write(f"Fantamedia totale (se giocassero tutti): {fantamedia_tot}\n")
        f.write(f"Costo totale: {costo}\n")
        f.write(
            f"Percentuale spesa attaccanti: {sum(p['price'] for p in squadra if p['role'] == 'A')/500*100:.1f}%\n")
        f.write(
            f"Percentuale spesa centrocampisti: {sum(p['price'] for p in squadra if p['role'] == 'C')/500*100:.1f}%\n")
        f.write(
            f"Percentuale spesa difensori: {sum(p['price'] for p in squadra if p['role'] == 'D')/500*100:.1f}%\n")
        f.write(
            # format everything in nice formatted tables
            f"Percentuale spesa portiere: {sum(p['price'] for p in squadra if p['role'] == 'P')/500*100:.1f}%\n")
    with open(f"{RESULTS_FOLDER}/results_concave_ILP_beta{beta}_pr{pr_cutoff}.md", "w") as f:
        f.write("# Squadra Ottimale (Concave ILP)\n\n")
        f.write(
            f"**Parametri:** Beta = `{beta}`, PR Cutoff = `{pr_cutoff}`\n\n")
        f.write(
            "| Giocatore            | Ruolo | Prezzo | FMVexp | Pr. Exp | Score  |\n")
        f.write(
            "|:---------------------|:------|:-------|:-------|:--------|:-------|\n")
        for p in squadra:
            f.write(
                f"| {p['name']:<20} | {p['role']:<5} | {p['price']:<6} | {p['fmv_exp']:<6.2f} | {p['pr_exp']:<7.1f}% | {p['score']:<6.2f} |\n"
            )
        f.write("\n### Riepilogo\n")
        f.write(f"- **Totale Score:** `{round(totale_score, 2)}`\n")
        f.write(
            f"- **Fantamedia totale (se giocassero tutti):** `{fantamedia_tot}`\n")
        f.write(f"- **Costo totale:** `{costo}`\n")
        f.write("\n### Spesa per Ruolo\n")
        f.write("| Ruolo       | Spesa (%) |\n")
        f.write("|:------------|:----------|\n")
        f.write(
            f"| Attaccanti  | {sum(p['price'] for p in squadra if p['role'] == 'A')/budget*100:.1f}% |\n")
        f.write(
            f"| Centrocampisti | {sum(p['price'] for p in squadra if p['role'] == 'C')/budget*100:.1f}% |\n")
        f.write(
            f"| Difensori   | {sum(p['price'] for p in squadra if p['role'] == 'D')/budget*100:.1f}% |\n")
        f.write(
            f"| Portiere    | {sum(p['price'] for p in squadra if p['role'] == 'P')/budget*100:.1f}% |\n")

    return {
        "squadra": squadra,
        "totale_score": totale_score,
        "fantamedia_tot": fantamedia_tot,
        "costo": costo,
        "beta": beta
    }


def weighted_backup_ILP(players, budget=470, pr_cutoff=40):
    """
    players: lista di dict con keys:
        name, role (P/D/C/A), price, fmv_exp, pr_exp
    budget: crediti totali disponibili
    pr_cutoff: considera solo giocatori con pr_exp >= cutoff
    n_giornate: numero di giornate (38)

    Logica:
    - titolari: 1P, 4D, 3C, 3A
    - panchinari: 1 per ruolo D/C/A
    - obiettivo: somma FMV titolari + contributo proporzionale panchinaro
    - contributo_panchinaro = fmv_panchinaro * (soglia_presenze - presenze_tot_titolari)/90
    """

    # filtro giocatori con poche presenze
    players = [p for p in players if p["pr_exp"] >= pr_cutoff]

    # separazione per ruolo
    roles = {"P": [], "D": [], "C": [], "A": []}
    for p in players:
        roles[p["role"]].append(p)

    # ordina per FMV decrescente
    for r in ["D", "C", "A"]:
        roles[r] = sorted(roles[r], key=lambda x: x["fmv_exp"], reverse=True)

    # definisci ILP
    prob = pulp.LpProblem("FantaWeightedBackupClean", pulp.LpMaximize)

    # variabili binarie
    x = {p["name"]: pulp.LpVariable(p["name"], cat="Binary") for p in players}

    # vincolo budget
    prob += pulp.lpSum(x[p["name"]]*p["price"] for p in players) <= budget

    # titolari
    prob += pulp.lpSum(x[p["name"]] for p in roles["P"][:1]) == 1
    prob += pulp.lpSum(x[p["name"]] for p in roles["D"][:4]) == 4
    prob += pulp.lpSum(x[p["name"]] for p in roles["C"][:3]) == 3
    prob += pulp.lpSum(x[p["name"]] for p in roles["A"][:3]) == 3

    # panchinari
    prob += pulp.lpSum(x[p["name"]] for p in roles["D"][4:5]) == 1
    prob += pulp.lpSum(x[p["name"]] for p in roles["C"][3:4]) == 1
    prob += pulp.lpSum(x[p["name"]] for p in roles["A"][3:4]) == 1

    # funzione obiettivo: titolari + contributo proporzionale panchinari
    objective = []

    # portiere titolare
    objective.append(roles["P"][0]["fmv_exp"] * x[roles["P"][0]["name"]])

    # titolari + panchinaro per ruolo
    for r, n_titolari in zip(["D", "C", "A"], [4, 3, 3]):
        titolari = roles[r][:n_titolari]
        panchinaro = roles[r][n_titolari]  # ultimo in ordine FMV

        # somma FMV titolari
        for p in titolari:
            objective.append(p["fmv_exp"] * x[p["name"]])

        # calcolo contributo proporzionale panchinaro
        soglia_presenze = 30 * n_titolari
        presenze_tot_titolari = pulp.lpSum(
            p["pr_exp"] * x[p["name"]] for p in titolari)
        contributo_panchinaro = panchinaro["fmv_exp"] * \
            (soglia_presenze - presenze_tot_titolari) / 95
        objective.append(contributo_panchinaro * x[panchinaro["name"]])

    prob += pulp.lpSum(objective)

    # risolvi
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    # estrai squadra
    squadra = [p for p in players if pulp.value(x[p["name"]]) == 1]
    totale_FMV = sum(p["fmv_exp"] for p in squadra)
    totale_FMV_titolari = sum(p["fmv_exp"] for p in squadra if p not in [
        roles["D"][4], roles["C"][3], roles["A"][3]])
    totale_costo = sum(p["price"] for p in squadra)

    print("Squadra ottimale (weighted backup ILP):")
    for p in squadra:
        print(
            f"{p['name']} ({p['role']}) - Prezzo: {p['price']} "
            f"- FMVexp: {p['fmv_exp']} - Pr. Exp: {p['pr_exp']}"
        )
    print("\nTotale FMV:", totale_FMV)
    print("Totale FMV titolari:", totale_FMV_titolari)
    print("Costo totale:", totale_costo)

    return {
        "squadra": squadra,
        "totale_FMV": totale_FMV,
        "costo": totale_costo,
        "totale_FMV_titolari": totale_FMV_titolari,
    }


def weighted_backup_ILP_full(players, budget=430, pr_cutoff=50):
    """
    players: lista di dict con keys: name, role (P/D/C/A), price, fmv_exp, pr_exp
    budget: crediti totali disponibili
    pr_cutoff: considera solo giocatori con pr_exp >= cutoff

    Logica:
    - titolari: 1P, 4D, 3C, 3A
    - panchinari: 1 per ruolo D/C/A
    - obiettivo: somma FMV titolari + contributo proporzionale panchinaro
    """

    # filtro giocatori con poche presenze
    players = [p for p in players if p["pr_exp"] >= pr_cutoff]

    # separazione per ruolo
    roles = {"P": [], "D": [], "C": [], "A": []}
    for p in players:
        roles[p["role"]].append(p)

    prob = pulp.LpProblem("FantaWeightedBackupFull", pulp.LpMaximize)

    # variabili binarie per ogni giocatore
    x = {p["name"]: pulp.LpVariable(
        f"x_{p['name']}", cat="Binary") for p in players}

    # vincoli titolari per ruolo
    prob += pulp.lpSum(x[p["name"]] for p in roles["P"]) == 1
    prob += pulp.lpSum(x[p["name"]] for p in roles["D"]) == 4
    prob += pulp.lpSum(x[p["name"]] for p in roles["C"]) == 3
    prob += pulp.lpSum(x[p["name"]] for p in roles["A"]) == 3

    # variabili binarie panchinari, 1 per ruolo
    panchinari = {}
    for r, n_titolari in zip(["D", "C", "A"], [4, 3, 3]):
        candidates = roles[r]
        for p in candidates:
            panchinari[p["name"]] = pulp.LpVariable(
                f"panch_{r}_{p['name']}", cat="Binary")  # 1 se p è panchinaro
        prob += pulp.lpSum(panchinari[p["name"]] for p in candidates) == 1
        # nessun giocatore può essere titolare e panchinaro insieme
        for p in candidates:
            prob += x[p["name"]] + panchinari[p["name"]] <= 1

    # vincolo budget: somma dei prezzi dei titolari e panchinari <= budget
    prob += pulp.lpSum(x[p["name"]] * p["price"] for p in players) + pulp.lpSum(panchinari[p["name"]] * p["price"]
                                                                                for p in players if p["name"] in panchinari) <= budget
    # prob += pulp.lpSum(x[p["name"]] * p["price"] for p in players) <= budget

    # funzione obiettivo
    objective = []

    # portiere titolare
    objective.append(pulp.lpSum(
        x[p["name"]] * p["fmv_exp"] for p in roles["P"]))

    # vincolo: in ogni ruolo (tra titolari e panchinari): sum(pr_exp) >= 90*n_titolari
    # prob += pulp.lpSum(x[p["name"]] * p["pr_exp"] for p in roles["P"]) >= 90 * 1
    prob += pulp.lpSum(x[p["name"]] * p["pr_exp"] for p in roles["D"]) + pulp.lpSum(panchinari[p["name"]] * p["pr_exp"]
                                                                                    for p in roles["D"]) >= 90 * 4
    prob += pulp.lpSum(x[p["name"]] * p["pr_exp"] for p in roles["C"]) + pulp.lpSum(panchinari[p["name"]] * p["pr_exp"]
                                                                                    for p in roles["C"]) >= 90 * 3
    prob += pulp.lpSum(x[p["name"]] * p["pr_exp"] for p in roles["A"]) + pulp.lpSum(
        panchinari[p["name"]] * p["pr_exp"] for p in roles["A"]) >= 90 * 3

    # titolari + panchinaro con contributo proporzionale
    for r, n_titolari in zip(["D", "C", "A"], [4, 3, 3]):
        titolari = roles[r]

        # FMV titolari
        objective += [x[p["name"]] * p["fmv_exp"] for p in titolari]

        # FMV panchinaro proporzionale al deficit presenze
        soglia = 90 * n_titolari
        presenze_titolari = pulp.lpSum(
            x[p["name"]] * p["pr_exp"] for p in titolari)

        # una sola variabile ausiliaria per ruolo
        y = pulp.LpVariable(f"contrib_{r}", lowBound=0)

        # vincoli lineari per y
        # contributo massimo = FMV del panchinaro scelto
        prob += y <= pulp.lpSum(p["fmv_exp"] *
                                panchinari[p["name"]] for p in titolari)
        # contributo proporzionale al deficit presenze
        prob += y <= soglia - presenze_titolari

        objective.append(y)

    prob += pulp.lpSum(objective)

    # risolvi
    prob.solve(pulp.PULP_CBC_CMD(msg=True))

    squadra = [p for p in players if pulp.value(x[p["name"]]) == 1]
    panch_selected = [p for p in players if p["name"]
                      in panchinari and pulp.value(panchinari[p["name"]]) == 1]
    totale_FMV = sum(p["fmv_exp"] for p in squadra) + \
        sum(p["fmv_exp"] for p in panch_selected)
    totale_costo = sum(p["price"] for p in squadra + panch_selected)

    print("Squadra ottimale (weighted backup ILP full):")
    for p in squadra:
        print(
            f"{p['name']} ({p['role']}) - Prezzo: {p['price']} "
            f"- FMVexp: {p['fmv_exp']} - Pr. Exp: {p['pr_exp']}"
        )
    print("Panchinari:")
    for p in panch_selected:
        print(
            f"{p['name']} ({p['role']}) - Prezzo: {p['price']} "
            f"- FMVexp: {p['fmv_exp']} - Pr. Exp: {p['pr_exp']}"
        )
    print("\nTotale FMV (titolari + panchinari):", totale_FMV)
    print("\nTotale FMV titolari:", sum(p["fmv_exp"] for p in squadra))
    print("Costo totale:", totale_costo)

    return {
        "titolari": squadra,
        "panchinari": panch_selected,
        "totale_FMV": totale_FMV,
        "costo": totale_costo
    }


if __name__ == "__main__":
    # simple_ILP()
    # ILP_presenze()
    for beta in [0, 0.5, 0.7, 0.9, 1.0, 1.5, 2.0]:
        print(f"\n=== Risultati per beta = {beta} ===")
        concave_ILP(read_data(), beta=beta, pr_cutoff=50)
    # weighted_backup_ILP_full(read_data(), budget=470, pr_cutoff=60)
