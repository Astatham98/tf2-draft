import requests
import pickle
import typing

compid: int = 896
compid2: int = 844
url = requests.get("http://api-v2.etf2l.org/competition/844/matches?page=1&limit=1000")
matches = url.json()['matches']
prem_match_ids = []
for match in matches['data']:
    
    if 'prem' in match['division']['name'].lower():
        print(match['round'])
        prem_match_ids.append(match['id'])
        
with open("prem_match_ids_prev", "wb") as fp:
    pickle.dump(prem_match_ids, fp)