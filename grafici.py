import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Leggi i dati dal file Excel
file_path = 'RED5_2025.xlsx'  # Sostituisci con il percorso del tuo file Excel
df = pd.read_excel(file_path, sheet_name='grafici')

# Creiamo una lista dei ruoli distinti
ruoli = df['Ruolo'].unique()
anni = df['Anno'].unique()

# Creazione di grafici separati per ogni ruolo
for ruolo in ruoli:
    # Filtra i dati per il ruolo corrente
    df_ruolo = df[df['Ruolo'] == ruolo]
    
    # Creazione del grafico per il ruolo
    plt.figure(figsize=(15, 6))
    
    for anno in anni:
        # Filtra i dati per l'anno corrente
        df_anno = df_ruolo[df_ruolo['Anno'] == anno]
        
        # Estrai le informazioni di interesse
        ordini = df_anno['Ordine']
        costi = df_anno['Costo']

        # Plotta la linea per l'anno corrente
        plt.plot(ordini, costi, marker='o', label=f'Anno {anno}', linestyle='-', linewidth=2)
    
    # Aggiunta delle etichette e del titolo
    plt.xlabel('Ordine di chiamata')
    plt.ylabel('FANTA MILIONI €)')
    plt.title(f'Andamento dei costi per il ruolo: {ruolo.capitalize()}')

    # Aggiunta della legenda
    plt.legend()

    # Mostra il grafico
    nome=ruolo+".png"
    plt.grid(True)
    plt.gca().set_xticks(np.arange(1, 96, 1))  
    #plt.show()
    plt.savefig(nome, format='png')
