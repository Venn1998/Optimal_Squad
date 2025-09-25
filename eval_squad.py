from utils import read_data


def evaluate_squad(squad_path):
    """Dato un file txt in cui sono scritti gli 11 titolari riga per riga, usa le tabelle ottenute con read players per valutare: 
    - Fanta media voto 
    - costo totale
    - percentuale di presenze attese"""

    # num players must be 11
    with open(squad_path, 'r') as f:
        squad = [line.strip() for line in f.readlines() if line.strip()]
        print(len(squad))
        assert len(squad) == 11, "La rosa deve contenere esattamente 11 giocatori"

    data = read_data()

    # for player in squad, find the player in data, print and sum the fanta media, price and pr_exp
    # probably we can drop the index in the data and use the name as key
    total_fantamedia = 0
    total_price = 0
    total_pr_exp = 0
    for player in squad:
        for p in data:
            if p['name'] == player:
                # print(f"{player}, FMV: {p['fmv_exp']}, Costo: {p['price']}, Pr_exp: {p['pr_exp']}%")
                total_fantamedia += p['fmv_exp']
                total_price += p['price']
                total_pr_exp += p['pr_exp']
                break
    print(f"{'Giocatore':<20} {'FMV':<8} {'Costo':<8} {'Pr. Exp':<10}")
    print("-" * 50)
    for player_name in squad:
        for p in data:
            if p['name'] == player_name:
                print(
                    f"{p['name']:<20} {p['fmv_exp']:<8.2f} {p['price']:<8} {p['pr_exp']:<9.1f}%")
                break

    return total_fantamedia, total_price, total_pr_exp / 11


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: python eval_squad.py <squad_file>")
        sys.exit(1)
    squad_file = sys.argv[1]
    fmv, price, pr_exp = evaluate_squad(squad_file)
    print(f"Fanta media totale: {fmv}")
    print(f"Costo totale: {price}")
    print(f"Percentuale di presenze attese: {pr_exp}%")
