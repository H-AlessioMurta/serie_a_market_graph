import pandas as pd
import requests
import openpyxl
import json
import matplotlib.pyplot as plt
from datetime import datetime
from bs4 import BeautifulSoup
from openpyxl.drawing.image import Image
import time
import unicodedata

id_collection=pd.DataFrame(columns=['nome','id_fantacalcio','id_transfermarket','id_fantalgoritmo'])
tabella=pd.DataFrame(columns = [
    'Nome Giocatore',           # giocatore['name']
    'Squadra',                  # giocatore['team']
    'Ruolo',                    # giocatore['role']
    'Slot',                     # giocatore['features']['slot']
    'PMA',                      # giocatore['features']['pma']
    'PFC',                      # giocatore['features']['pfc']
    'FVM Classic 350',          # (int(giocatore['FVM']['Classic'])/1000)*350
    'Fantamedia Attesa',        # giocatore['features']['expectedFantamedia']
    'Titolarità Attesa',        # giocatore['features']['expectedTitolarita']
    'Probabilità Rigore',       # giocatore['features']['penaltyProbability']
    'Probabilità Punizione',    # giocatore['features']['freeKickProbability']
    'Range PMA',                # giocatore['features']['pmaRange']
    'Range PFC',                # giocatore['features']['pfcRange']
    'Voto Base Ultimi 3 Anni',  # giocatore['features']['lastThreeYearVotoBase']
    'Fantamedia Ultimi 3 Anni', # giocatore['features']['lastThreeYearFantamedia']
    'Titolarità Ultimi 3 Anni', # giocatore['features']['lastThreeYearTitolarity']
    'Voto Base Ultimi 5 Anni',  # giocatore['features']['lastFiveYearVotoBase']
    'Fantamedia Ultimi 5 Anni', # giocatore['features']['lastFiveYearFantamedia']
    'Titolarità Ultimi 5 Anni', # giocatore['features']['lastFiveYearTitolarity']
    'Voto Base Anno Scorso',    # giocatore['features']['lastYearVotoBase']
    'Fantamedia Anno Scorso',   # giocatore['features']['lastYearFantamedia']
    'Titolarità Anno Scorso',   # giocatore['features']['lastYearTitolarity']
    'Voto Base Stagione Corrente', # giocatore['features']['currentSeasonVotoBase']
    'Fantamedia Stagione Corrente', # giocatore['features']['currentSeasonFantamedia']
    'Titolarità Stagione Corrente', # giocatore['features']['currentSeasonTitolarity']
    'Piede',
    'Altezza',                  # giocatore['Altezza']
    'City',
    'Data di Nascita',          # giocatore['Nato il']
    'Nazionalità',              # giocatore['Nazionalità']
    'Valore Corrente',          # giocatore['current']
    'Valore Massimo',           # giocatore['highest']
    'Età',                      # giocatore['age']
    'Descrizione',               # giocatore['descrizione'],
])
grafici=pd.DataFrame(columns=['Giocatore','Grafico'])
storico_infortuni=pd.DataFrame(columns=['Giocatore','Anno','totalDays','totalInjuryRate','totalGamesMissed'])
storico_performance=pd.DataFrame(columns=['Giocatore','Anno','Competition',	'Club',	'Appearances',	'Goals','Assists',	'SubstitutionsOn',	'SubstitutionsOff',	'YellowCards','RedCards',	'MinutesPlayed','minutesPerGoal'])

#body_listone={"credits": 350,"flagNoGoal": False,"flagModDefense": True,"competitionParticipants": 12,"player_name": None,"flagSvincolati": False,"flagMantra": False,"auctionType": "pma","flag_clean_sheet": False, }   

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

def transfermarket_infortuni():
    headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
    html = requests.get("https://www.transfermarkt.it/serie-a/verletztespieler/wettbewerb/IT1", headers=headers)
    soup = BeautifulSoup(html.content, "html.parser")
    rows = soup.find_all('tr', class_=['odd', 'even'])
    lista_infortunati=[]
    for row in rows:
        player_name = row.find('a', title=True).text
        injury_type = row.find_all('td')[5].text.strip()
        data_rientro = row.find_all('td')[6].text.strip()
        market_value = row.find_all('td')[-1].text.strip()
        lista_infortunati.append({
            "Giocatore": player_name,
            "Infortunio": injury_type,
            "Data rientro": data_rientro,
            "Valore di Mercato": market_value
        })
    return lista_infortunati


def get_hometown(link):
    hometown_url=f"https://www.transfermarkt.it{link}"
    headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
    home_player = requests.get(hometown_url, headers=headers)
    soup = BeautifulSoup(home_player.content, "html.parser")
    li_tag = soup.find_all('li', class_='data-header__label')
# Estrarre il testo all'interno di <span> con itemprop="birthPlace"
    birth_place = "Ignoto figlio di mignotta"
    for x in li_tag:
        if x.find('span', itemprop='birthPlace'):
            birth_place = birth_place = x.find('span', itemprop='birthPlace').get_text(strip=True)
    return birth_place



def transfermarket_infos(mapping_id,team,nome):
    ecezzioni_note={
            "sangare b.": 962125,
            "nava": 815563,
            "liberali": 988964,
            "adzic": 944570,
            "mbangula": 654991,
            "ekhator": 934878,
            "marin re.": 1041614,
            "bellanova": 357992,
            "kalolu": 585949,
            "nicolussi": 430280,
            "zambo":354361,
            "lovik":661212,
            "soulè":668951,
            "montipò":241923,
            "laurientè":579930,
            "konè":624690,
            "yildiz":845654,
            "bernabè":466802,
            "dodò":401529,
            "lucumì":413565,
            "marì":210178,
            "hojholt":543822,
            "toure":335516,
            "kone":921655,
            "kilicsoy":875334,
            "liteta":1134304,
            "gronbaek": 503866,
            "dembelè":1004344,
            "tourè":335516,
            "ostigard":367284,
            "candè":520530,
            "sorensen":514888,
            "hojlund":610442,
            "balogh": 0,
            "zè pedro":406151
        }
    id=-1
    link=''
    if len(nome.split(" ")[0]) >2:
        nome_da_cercare=nome.split(" ")[0]
    else:
        nome_da_cercare=nome.split(" ")[0]+' '+nome.split(" ")[1]
    print(team)
    for a_player in mapping_id[team]:
         if nome_da_cercare.lower().replace("'","") in a_player['name'].lower():
            id=a_player['id']
         if nome_da_cercare.lower().replace("'","") == "dambrosio":
            id=55769
         if nome_da_cercare.lower().replace("'","") == "yildiz":
            id=845654
    if nome == "MARTINEZ L.":
        id=406625
    if nome == "CAMARDA":
        id=1058368
    if nome_da_cercare.lower().replace("'","") in ecezzioni_note:
        id=ecezzioni_note[nome_da_cercare.lower().replace("'","")]
    if id == -1:
       print(f"non trovato { nome } nel {team} che id transfermarket uso? ")
       id=input("Inserisci un valore: ")
    for a_player in mapping_id [team]:
        if a_player['id']==id:
            link=a_player['link']
    if id != -1:
       tm_datas = {}
       #print(f"Trovato id di {nome} con valore {id}")
       performance_url=f"https://www.transfermarkt.it/ceapi/player/{id}/performance"
       performance_result=transfermarket_json(performance_url)
       print(f"ho queste performance {performance_result}")
       for x in performance_result:
           if x['nameSeason']  != None :
                tm_datas['possibleGames_' + x['nameSeason']] = x['possibleGames']
                tm_datas['gamesPlayed_' + x['nameSeason']] = x['gamesPlayed']
                tm_datas['goalsScored_' + x['nameSeason']] = x['goalsScored']
                tm_datas['assists_' + x['nameSeason']] = x['assists']
                tm_datas['yellowCards_' + x['nameSeason']] = x['yellowCards']
                tm_datas['secondYellowCards_' + x['nameSeason']] = x['secondYellowCards']
                tm_datas['redCards_' + x['nameSeason']] = x['redCards']
                tm_datas['startElevenPercent_' + x['nameSeason']] = x['startElevenPercent']
                tm_datas['minutesPlayedPercent_' + x['nameSeason']] = x['minutesPlayedPercent']
                tm_datas['goalsContributedPercent_' + x['nameSeason']] = x['goalsContributedPercent']
                tm_datas['concededGoals_' + x['nameSeason']] = x['concededGoals']
                tm_datas['cleanSheets_' + x['nameSeason']] = x['cleanSheets']
                tm_datas['blockedPenaltyPercent_' + x['nameSeason']] = x['blockedPenaltyPercent']
                tm_datas['minutesPlayed_' + x['nameSeason']] = x['minutesPlayed']
       market_values_url=f'https://www.transfermarkt.it/ceapi/marketValueDevelopment/graph/{id}'
       market_values_result=transfermarket_json(market_values_url)
       #print(market_values_result['list'])
       popped_marked=[]
       actual_age=0
       for x in market_values_result['list']:
           x.pop('wappen')
           popped_marked.append(x)
           if actual_age<int(x['age']):
               actual_age=int(x['age'])
       tm_datas['market_values']=popped_marked
       tm_datas['current'] = market_values_result['current']
       tm_datas['highest'] = market_values_result['highest']
       tm_datas['age']=actual_age
       tm_datas['city']=get_hometown(link)
       tm_datas['id_transfermarket']=id
       return tm_datas

def transfermarket_json(tmurl):
    print(tmurl)
    headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
    x = requests.get(tmurl, headers=headers)
    return x.json()

def aggiorna_dati_fantaculo():
    print('Chiamata listone aggiornato - Fantaculo')
    x = requests.get('https://fantaculo.it/leghe-srv/api/v1/aste/listone?credits=350&flagNoGoal=false&flagModDefense=true&competitionParticipants=10&name=null&flagSvincolati=false&flagMantra=false&auctionType=pma')
    return x.json()

def get_by_name(name,id,mapping_id):
        player_url=f'https://fantaculo.it/leghe-srv/api/v1/aste/player?credits=350&flagNoGoal=false&flagModDefense=true&competitionParticipants=10&name={name}&flagSvincolati=false&flagMantra=false&auctionType=pma'
        x = requests.get(player_url)
        giocatore=x.json()
        print("inizo chiamate")
        giocatore.update(transfermarket_infos(mapping_id,giocatore['team'],giocatore['name']))
        print("----fine chiamata transfermarket")
        giocatore.update(fantacalcio_calciatore(giocatore['team'].lower(),giocatore['name'].lower(),id))
        print("----fine chiamata fantacalcio.it")
        return giocatore

def scraper(mapping_id,lista_infortuni):
    df_lista_infortuni= pd.DataFrame(lista_infortuni)
    listone=aggiorna_dati_fantaculo()
    conta = 0
    for i in listone:
        conta+=1
        print(f'N {conta} chiamata per {i["name"]}')
        name=i["name"]
        id=i['idFantacalcio']
        try:
            giocatore=get_by_name(name,id,mapping_id)
            nuovo_rigo = [
                giocatore['name'],
                giocatore['team'],
                giocatore['role'],
                giocatore['features']['slot'],
                giocatore['features']['pma'],
                giocatore['features']['pfc'],
                (int(giocatore['FVM']['Classic'])/1000)*350,
                giocatore['features']['expectedFantamedia'],
                giocatore['features']['expectedTitolarita'],
                giocatore['features']['penaltyProbability'],
                giocatore['features']['freeKickProbability'],
                giocatore['features']['pmaRange'],
                giocatore['features']['pfcRange'],
                giocatore['features']['lastThreeYearVotoBase'],
                giocatore['features']['lastThreeYearFantamedia'],
                giocatore['features']['lastThreeYearTitolarity'],
                giocatore['features']['lastFiveYearVotoBase'],
                giocatore['features']['lastFiveYearFantamedia'],
                giocatore['features']['lastFiveYearTitolarity'],
                giocatore['features']['lastYearVotoBase'],
                giocatore['features']['lastYearFantamedia'],
                giocatore['features']['lastYearTitolarity'],
                giocatore['features']['currentSeasonVotoBase'],
                giocatore['features']['currentSeasonFantamedia'],
                giocatore['features']['currentSeasonTitolarity'],
                giocatore['Piede'],
                giocatore['Altezza'],
                giocatore['city'],
                giocatore['Nato il'],
                giocatore['Nazionalità'],
                giocatore['current'],
                giocatore['highest'],
                giocatore['age'],
                giocatore['descrizione'],
            ]
            print("🦕🦕🦕🦕🦕🦕🦕🦕🦕🦕🦕🦕🦕🦕🦕 rigo fatto  🦕🦕🦕🦕🦕🦕🦕🦕🦕🦕🦕🦕🦕🦕🦕🦕🦕🦕🦕🦕🦕🦕")             

            print(giocatore['performances'])
            performance=giocatore['performances']
            for anno, valori in performance.items():
                # Creazione di un dizionario con i valori per il DataFrame
                riga_perf = { 'Giocatore': giocatore['name'], 'Anno': anno, 'totalDays': valori['totalDays']['value'], 'totalInjuryRate': valori['totalInjuryRate']['value'], 'totalGamesMissed': valori['totalGamesMissed']['value']                    }
                # Aggiunta della riga alla lista
                storico_performance.loc[len(storico_performance)]=riga_perf
                #print(f"valore infortuni {riga}")


            id_array=[giocatore['name'],i['idFantacalcio'],giocatore['id_transfermarket']]
            #print(f"id_array: {id_array}")
            tabella.loc[len(tabella)]=nuovo_rigo
            #print(f"\n===============================\nvalore nuovo_rigo {nuovo_rigo}")
            id_collection.loc[len(id_collection)]=id_array
            #print(f"\n===============================\nvalore id_array {id_array}")
            try:
                grafici_valore_mercato(giocatore['name'],giocatore['market_values'],giocatore['name']+'.png')
                print("----Grafico creato")
            except:
                print(f"fallita creazione grafico di {name} ")
                continue
        except:
            print(f"[GRAVE]fallita chiamata di {name}")
            continue
    print('fine-scraping')
    
    with pd.ExcelWriter('graphs_v1_scraper_fantaculo_'+datetime.today().strftime('%Y-%m-%d')+'.xlsx') as writer:
        tabella.to_excel(writer, sheet_name='dati')
        df_lista_infortuni.to_excel(writer,sheet_name='infortuni')
        id_collection.to_excel(writer,sheet_name='ids')
        storico_infortuni.to_excel(writer,sheet_name='storico_infortuni')
        storico_performance.to_excel(writer,sheet_name='storico_performance')
    print('file scritto')

def rimuovi_accenti(input_str):
    nfkd_form = unicodedata.normalize('NFD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore').decode('utf-8')
    return only_ascii

# Funzione ricorsiva per applicare la rimozione accenti a tutte le stringhe in un dizionario o lista
def applica_rimozione_accenti(data):
    if isinstance(data, dict):
        return {k: applica_rimozione_accenti(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [applica_rimozione_accenti(i) for i in data]
    elif isinstance(data, str):
        return rimuovi_accenti(data)
    else:
        return data

def aggiorna_rigo(file_path,mapping_id):
    # Apri il file Excel
    df = pd.read_excel(file_path)
    #print(df)
    listone=aggiorna_dati_fantaculo()
    for i in listone:
        if i['name'] not in  df['Nome Giocatore'].values:
            name=i["name"]
            print(f"Non trovato {name}")
            id=i['idFantacalcio']
            if i['team'] == '*':
                print(f"senza squadra {i['team']} 🦕")
                continue
            try:
                giocatore=get_by_name(name,id,mapping_id)
            except Exception as err:
                print(f"fallisco a poolare il campo 🦕 {err}")
                continue
            nuovo_rigo = [
                    "xyz",
                    giocatore['name'],
                    giocatore['team'],
                    giocatore['role'],
                    giocatore['features']['slot'],
                    giocatore['features']['pma'],
                    giocatore['features']['pfc'],
                    (int(giocatore['FVM']['Classic'])/1000)*350,
                    giocatore['features']['expectedFantamedia'],
                    giocatore['features']['expectedTitolarita'],
                    giocatore['features']['penaltyProbability'],
                    giocatore['features']['freeKickProbability'],
                    giocatore['features']['pmaRange'],
                    giocatore['features']['pfcRange'],
                    giocatore['features']['lastThreeYearVotoBase'],
                    giocatore['features']['lastThreeYearFantamedia'],
                    giocatore['features']['lastThreeYearTitolarity'],
                    giocatore['features']['lastFiveYearVotoBase'],
                    giocatore['features']['lastFiveYearFantamedia'],
                    giocatore['features']['lastFiveYearTitolarity'],
                    giocatore['features']['lastYearVotoBase'],
                    giocatore['features']['lastYearFantamedia'],
                    giocatore['features']['lastYearTitolarity'],
                    giocatore['features']['currentSeasonVotoBase'],
                    giocatore['features']['currentSeasonFantamedia'],
                    giocatore['features']['currentSeasonTitolarity'],
                    giocatore['Piede'],
                    giocatore['Altezza'],
                    giocatore['city'],
                    giocatore['Nato il'],
                    giocatore['Nazionalità'],
                    giocatore['current'],
                    giocatore['highest'],
                    giocatore['age'],
                    giocatore['descrizione'] 
                ]
            print(f"provo ad aggiornare per {name}")
            df.loc[len(df)]=nuovo_rigo
            df.to_excel(file_path, index=False)

def transfermarket_teams_list():
    headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
    teams = {}
    for team_name, team_list in transfermarket_teams.items():
            url=f'https://www.transfermarkt.it/quickselect/players/{team_list}'
            id_list= requests.get(url, headers=headers)
            teams[team_name]=applica_rimozione_accenti(id_list.json())
    print(teams)
    return teams

def fantacalcio_calciatore(team,name,id):
    fc_datas={}
    fantacalcio_calciatore_profile_url=f'https://www.fantacalcio.it/serie-a/squadre/{team}/{name}/{id}'
    print(f"verifica che esista {fantacalcio_calciatore_profile_url}")
    headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
    html = requests.get(fantacalcio_calciatore_profile_url, headers=headers)
    soup = BeautifulSoup(html.content, "html.parser")
    section = (
        soup.find('section', {'id': 'player-description'})
        or soup.find('section', {'id': 'description'})
        or soup.find('section', {'id': 'player-main-info'})
    )
    fc_datas['descrizione'] = ''
    for class_name in ['p1', 'li1', 'ul1','bullist','p2']:
        p1_tags = section.find_all(class_=class_name)
        for p1 in p1_tags:
            fc_datas['descrizione']= str(fc_datas['descrizione'])+p1.get_text(strip=True)
    dt_tag = soup.find('dt', string='Piede')
    # Trovare il successivo elemento <dd> rispetto a <dt>
    dd_tag = dt_tag.find_next('dd')

    # Trovare il tag <span> all'interno del <dd> e prendere il valore dell'attributo title
    span_title = dd_tag.find('span')['title']
    fc_datas['Piede']=span_title    
    altezza = soup.find('dd', itemprop='height').text
    fc_datas['Altezza'] = altezza
    # Nato il
    nato_il = soup.find('dd', class_='birthdate').text
    fc_datas['Nato il'] = nato_il
    # Nazionalità
    nazionalita = soup.find('dd', class_='nationalities').text
    fc_datas['Nazionalità'] = nazionalita
    print("fin la")
    # Medie
    medie = {}
    medie_elements = soup.select('.player-stats .group:nth-of-type(1) .badge')
    medie['MV'] = medie_elements[0].text
    medie['FM'] = medie_elements[1].text
    fc_datas['Medie'] = medie
    # Quotazione
    quotazione = {}
    quotazione_elements = soup.select('.player-stats .group:nth-of-type(2) .badge')
    quotazione['Classic'] = quotazione_elements[0].text
    quotazione['Mantra'] = quotazione_elements[1].text
    fc_datas['Quotazione'] = quotazione
    # FVM
    fvm = {}
    fvm_elements = soup.select('.player-stats .group:nth-of-type(3) .badge')
    fvm['Classic'] = fvm_elements[0].text
    fvm['Mantra'] = fvm_elements[1].text
    fc_datas['FVM'] = fvm
    return fc_datas

def grafici_valore_mercato(name, market_values, file_path):
    dates = [pd.to_datetime(mv['x'], unit='ms') for mv in market_values]
    # Converti i valori in milioni di euro
    values = [mv['y'] / 1_000_000 for mv in market_values]
    # Crea il grafico
    plt.figure(figsize=(6, 4))
    plt.plot(dates, values, marker='o', linestyle='-', color='b')
    plt.title(f'Valore di Mercato di {name}')
    plt.xlabel('Data')
    plt.ylabel('Valore in Milioni €')
    plt.grid(True)    
    plt.savefig(file_path, format='png')
    plt.close()

def fantaalgoritmo(name,fantaid):
    token =  "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICItTzNCNEJ0dGdUclFNNldRQnF6S1NBNUJicjdPV281SnhnbUYzclMzVzdvIn0.eyJleHAiOjE3MjQ0MjA2MzAsImlhdCI6MTcyNDQxNzAzMCwiYXV0aF90aW1lIjoxNzI0NDE3MDI5LCJqdGkiOiIwZjg2NDAyNS1mZGQwLTQ2ZTItYjE5Zi0xZmExODRjMTYyYmQiLCJpc3MiOiJodHRwczovL2FkbWluLmZhbnRhbGdvcml0bW8uaXQvcmVhbG1zL2ZhbnRhbGdvcml0bW8iLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiNDg1NzBiYzgtMjVjZi00Yzg5LWJlYjEtOWMzOTkxMjgwNWUxIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiZmFudGFsZ29yaXRtby1hcHAtcmVnaXN0ZXIiLCJub25jZSI6ImNhY2VmZGU4LWY3YmUtNDc3My1hN2YxLWMyYTRjY2U3ZDY5ZiIsInNlc3Npb25fc3RhdGUiOiI3OTUxMzM1Yi1lOGIyLTQzM2ItOTlkNi01OTM5ODhkY2IxZGYiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHBzOi8vYXBwLmZhbnRhbGdvcml0bW8uaXQvKiIsImh0dHBzOi8vYXBwLmZhbnRhbGdvcml0bW8uaXQiXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbImRlZmF1bHQtcm9sZXMtZmFudGFsZ29yaXRtbyIsIm9mZmxpbmVfYWNjZXNzIiwiZnJlZW1pdW0iLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoib3BlbmlkIGVtYWlsIHByb2ZpbGUiLCJzaWQiOiI3OTUxMzM1Yi1lOGIyLTQzM2ItOTlkNi01OTM5ODhkY2IxZGYiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwibmFtZSI6IkFsZXNzaW8gTXVydGEiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJhbGVzc2lvLm11cnRhQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJBbGVzc2lvIiwiZmFtaWx5X25hbWUiOiJNdXJ0YSIsImVtYWlsIjoiYWxlc3Npby5tdXJ0YUBnbWFpbC5jb20ifQ.SmqDOJHV9CZ8FowkONsvEZDHs1_iPUqo-84y4pgVf5HSJIvnm3SVnc9dZMCegkeQmKwZcsV5NA6ixdVyNQ5P0DmcxESX8fT0VSZN5tLQGdE4smiExr0UFdCDNUlbq8e1W71lMvDu0dDIwniFOViqoLtaT3pWePASWfFlG3HeZqViBNyK6SrH70bZjDoyGTrX07w7qULjqE0vPZROUX7S-bV3rQIwmGb0X6qzevTRo3OFFvadQwSWoWhRIHwvifycXElntTNZ60yovR4tLyVWqvIequJNLOETn8w1-Z_CWc9vTywBHKnMdxUTPgw0XKWW-UQFfMui7IHLhjKq_x6n3A"
    headers = { 
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Authorization": token  # Aggiungi il token come header Authorization
    }
    #print("entro")
    html = requests.get(f"https://api.fantalgoritmo.it/players?page=0&size=50&sort=role%2Casc&sort=surname%2Casc&search={name}", headers=headers)
    print(f"---------search ha risposto {html}")
    giocatore=html.json()
    data_fanta={}
    for x in giocatore['content']:
        #print(f'valore dentro content {x}')
        profile=f"https://api.fantalgoritmo.it/players/{x['id']}"
        get_fantaid= requests.get(profile,headers=headers).json()
        fantacalcioid=get_fantaid['fantacalcioId']
        #print(f"{fantacalcioid} == {fantaid}")
        if int(fantacalcioid) == int(fantaid):
            statistics=f"https://api.fantalgoritmo.it/players/{x['id']}/statistics"
            html2 = requests.get(statistics, headers=headers)
            print(f"---------chiamata alle statistiche {html2.status_code}")
            value_html2=html2.json()
            #print(f"json di statistiche:\n {value_html2}")
            data_fanta.update(value_html2)
            data_fanta['id_fantaalgoritmo']=x['id']
            if "dateContractExpiration" in get_fantaid:
                data_fanta['fine_contratto']= get_fantaid['dateContractExpiration']
    if "fine_contratto" not in data_fanta:
        data_fanta['fine_contratto']  = "Non rompere il cazzo" 
    return data_fanta            

def parse_tabella_giocatore(giocatore, squadra):
    BASE_URL = "https://www.transfermarkt.it"
    HEADERS = {"User-Agent": "Mozilla/5.0"} 
    url = BASE_URL + giocatore["link"].replace("profil", "leistungsdatendetails")+"/saison//verein/0/liga/0/wettbewerb//pos/0/trainer_id/0/plus/1"
    print(f"Scarico {giocatore['name']} → {url}")
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    # estraggo la stagione attuale

    table = soup.find("table", {"class": "items"})
    if not table or table is None:
        return "Riprova"
    dati_giocatore = []
    for row in table.select("tbody tr"):
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        if not cols:
            continue
        print(cols)
        dati = {
            "Giocatore": giocatore["name"],
            "Anno": cols[0],
            "Competition": cols[2] if len(cols) > 2 else "",
            "Club": squadra,
            "Appearances": cols[5] if len(cols) > 2 else "",
            "Punti A Partita": cols[6] if len(cols) > 2 else "",
            "Goals": cols[7] if len(cols) > 3 else "",
            "Assists": cols[8] if len(cols) > 4 else "",
            "Entrate": cols[9] if len(cols) > 7 else "",
            "Sostituzioni": cols[10] if len(cols) > 7 else "",
            "Gialli": cols[11] if len(cols) > 7 else "",
            "Doppi Gialli": cols[12] if len(cols) > 7 else "",
            "Rossi": cols[12] if len(cols) > 7 else "",
            "Rigori": cols[12] if len(cols) > 7 else "",
            "MinutesPlayed": cols[-2] if len(cols) > 2 else "",
            "minutesPerGoal": cols[-1] if len(cols) > 1 else "",
        }
        dati_giocatore.append(dati)
    return dati_giocatore


def transfer_market_performance(mapping_id):
    tutti_dati = []
    for squadra, giocatori in mapping_id.items():
        for g in giocatori:
            while True:
                dati = parse_tabella_giocatore(g, squadra)
                if dati != "Riprova":
                    tutti_dati.extend(dati)
                    break
                else:
                    print(f"riprovo per {g}")
                    time.sleep(30)               

    # Scrittura Excel
    df = pd.DataFrame(tutti_dati, columns=[
            "Giocatore",
            "Anno",
            "Competition",
            "Club",
            "Appearances",
            "Punti A Partita",
            "Goals",
            "Assists",
            "Entrate",
            "Sostituzioni",
            "Gialli",
            "Doppi Gialli",
            "Rossi",
            "Rigori",
            "MinutesPlayed",
            "minutesPerGoal"
    ])
    df.to_excel("AA_dati_giocatori.xlsx", index=False)
    print("File Excel 'dati_giocatori.xlsx' scritto con successo!")







#https://fantaculo.it/leghe-srv/api/v1/aste/listone?credits=350&flagNoGoal=false&flagModDefense=true&competitionParticipants=12&name=null&flagSvincolati=false&flagMantra=false&auctionType=pma
if __name__ == "__main__":
    

    raw=aggiorna_dati_fantaculo()
    df = pd.DataFrame(raw, columns=["name", "idFantacalcio"])
    # Salvataggio in Excel
    df.to_excel("id.xlsx", index=False)

    print("File Excel creato: giocatori.xlsx")
    #mapping_id=transfermarket_teams_list()
    #print(mapping_id)
    #transfer_market_performance(mapping_id)
    #aggiorna_rigo("graphs_scraper_fantaculo_2025-09-09.xlsx",mapping_id)
    #lista_infortuni=transfermarket_infortuni()
    #scraper(mapping_id,lista_infortuni)
 
