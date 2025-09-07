import json
import pandas as pd
from datetime import datetime

# Supponiamo che la tua lista di record si chiami data (lista di dict)
with open("json_fantaculo_2025-09-07.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Flatten dei dati principali
df_main = pd.json_normalize(
    data,
    sep="_",  # separatore per campi annidati
    max_level=1
)

# Flatten dei dati di mercato (market_values) in un foglio separato
market_dfs = []
for record in data:
    player_name = record.get("name")
    team = record.get("team")
    if "market_values" in record:
        df_mv = pd.DataFrame(record["market_values"])
        df_mv["name"] = player_name
        df_mv["team"] = team
        market_dfs.append(df_mv)

df_market = pd.concat(market_dfs, ignore_index=True) if market_dfs else pd.DataFrame()

# Salvataggio in Excel
filename = "scraper_fantaculo_datas_" + datetime.today().strftime("%Y-%m-%d") + ".xlsx"
with pd.ExcelWriter(filename) as writer:
    df_main.to_excel(writer, sheet_name="giocatori", index=False)
    if not df_market.empty:
        df_market.to_excel(writer, sheet_name="market_values", index=False)
