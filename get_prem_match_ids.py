import requests
import pickle
compid = 896
compid2 = 844
url = requests.get("http://api-v2.etf2l.org/competition/844/matches?page=1&limit=1000")
matches = url.json()['matches']
prem_match_ids = []
for match in matches['data']:
    print(match['id'])
    if 'prem' in match['division']['name'].lower():
        prem_match_ids.append(match['id'])
        
with open("prem_match_ids_prev", "wb") as fp:
    pickle.dump(prem_match_ids, fp)