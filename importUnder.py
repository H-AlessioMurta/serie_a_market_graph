import json
import pandas as pd
from datetime import datetime

# Carica la lista di record JSON
with open("json_understat_2025-09-08.json", "r", encoding="utf-8") as f:
    data = json.load(f)   # deve essere una lista di record, non un singolo dict

# Conversione diretta in DataFrame
df = pd.DataFrame(data)

# Salvataggio in Excel
filename = "player_stats_" + datetime.today().strftime("%Y-%m-%d") + ".xlsx"
df.to_excel(filename, sheet_name="statistiche", index=False)
