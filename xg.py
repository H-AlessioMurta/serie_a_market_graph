import requests
import re
import json
from datetime import datetime
from bs4 import BeautifulSoup

transfermarket_teams = {
    'Inter': 46,
    'Milan': 5,
    'Juventus': 506,
    'Atalanta': 800,
    'Bologna': 1025,
    'Roma': 12,
    'Lazio': 398,
    'Fiorentina': 430,
    'Torino': 416,
    'Napoli': 6195,
    'Genoa': 252,
    'Monza': 2919,
    'Verona': 276,
    'Lecce': 1005,
    'Udinese': 410,
    'Cagliari': 1390,
    'Empoli': 749,
    'Parma': 130,
    'Como': 1047,
    'Cremonese': 2239,
    'Sassuolo' : 6574,
    'Pisa': 4172
}


def understat_get_team_players(team: str, season: int):
    url = f"https://understat.com/team/{team}/{season}"
    print(url)
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    scripts = soup.find_all("script")
    players_json = None
    for script in scripts:
            if "playersData" in script.text:
                # regex per estrarre la parte JSON
                match = re.search(r"JSON\.parse\('([^']+)'\)", script.text)
                if match:
                    raw_data = match.group(1)
                    # decodifica delle sequenze \x
                    decoded = raw_data.encode("utf-8").decode("unicode_escape")
                    players_json = json.loads(decoded)
                    break    
                if not players_json:
                    raise ValueError("Players data non trovati")

    return players_json


if __name__ == "__main__":
    understat_records = []

    for team_name, _ in transfermarket_teams.items():
        for season in [2025, 2024, 2023, 2022, 2021]:
            if team_name == 'Milan':
                players = understat_get_team_players("Ac_Milan", season)
            elif team_name == 'Parma':
                players = understat_get_team_players("Parma_Calcio_1913", season)
            else:
                players = understat_get_team_players(team_name, season)

            # aggiungiamo la stagione a ogni giocatore
            for p in players:
                p["season"] = season
                p["team"] = team_name  # utile anche sapere la squadra
                understat_records.append(p)

            print(f"✔ {team_name} {season} -> {len(players)} giocatori")

    print("Fine raccolta da Understat")

    filename = "json_understat_" + datetime.today().strftime("%Y-%m-%d") + ".json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(understat_records, f, ensure_ascii=False, indent=4)

    print(f"File salvato: {filename}")
