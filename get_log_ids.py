import requests
import pickle

def get_etf2l_stats(match):
    
    url = f"https://api-v2.etf2l.org/matches/{match}"
    web = requests.get(url)
    if web.status_code == 200:
        web_json = web.json()
        match_stats = web_json['match']
        if match_stats['r1'] is not None:
            player_team_ids = {player['steam']['id64']: player['team_id'] for player in match_stats['players']}
            
            c1id = match_stats['clan1']['id']
            c2id = match_stats['clan2']['id']
            
            c1score = match_stats['r1']
            c2score = match_stats['r2']
            
            player_score_ids_c1 = {id: c1score for id, tid in player_team_ids.items() if tid == c1id}
            player_score_ids_c2 = {id: c2score for id, tid in player_team_ids.items() if tid == c2id}
            id64_week = {id: match_stats['round'] for id in player_team_ids.keys()}
            merged_score_ids = player_score_ids_c1 | player_score_ids_c2
            return merged_score_ids, match_stats['time'], match_stats['submitted'], match_stats['maps'], id64_week
    else:
        print(url, ' ', web.status_code)
    return
        
def get_logs_stats(id64, before, after, etf2l_maps):
    join_ids = 'player=' + ','.join(id64)
    
    logs_request_url = f"http://logs.tf/api/v1/log?" + join_ids
    potential_logs = requests.get(logs_request_url).json().get('logs')
    log_with_map = {log['id']: log['map'] for log in potential_logs}
    good_map_log_ids = [log for log in potential_logs if log['id'] in filter_logs_by_map(log_with_map, etf2l_maps)]
    final_logs = [log for log in good_map_log_ids if filter_logs_by_time(log, before, after) and filter_titles(log['title'])]
    print(final_logs)
    return final_logs
    
def filter_logs_by_time(log, before, after):
    if before < log.get('date') < after:
        return True
    return False
    
def filter_logs_by_map(log_with_map, etf2l_maps):
    ids = []
    filtered_etf2l_maps = [filter_maps(emap) for emap in etf2l_maps]
    for k, v in log_with_map.items():
        if fmap := filter_maps(v):
            if fmap in filtered_etf2l_maps:
                ids.append(k)
    return ids

def filter_maps(map):
    map_split = map.split('_')
    if len(map_split) < 2:
        return False
    map = map_split[0] + "_" + map_split[1]
    return map.lower()

def filter_titles(title):
    if 'serveme.tf' in title:
        return True
    return False


    
def get_log_ids(pickeList):     
    with open(pickeList, "rb") as fp:
            match_ids = pickle.load(fp)
    ids = []
    id64_scores = {}
    id64_week = {}
    for match in match_ids:
        if get_etf2l_stats(match) is not None:
            id64_score, game_time, submitted_time, maps, week = get_etf2l_stats(match)
            logs = get_logs_stats(id64_score.keys(), game_time, submitted_time, maps)
            ids.append([log['id'] for log in logs])
            id64_scores = id64_scores | id64_score
            id64_week = id64_week | week
        else: continue
    return ids, id64_scores, id64_week