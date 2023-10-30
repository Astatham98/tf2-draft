import requests
import pickle
from typing import Any
import logging
logging.basicConfig(filename='missingMatches.log', encoding='utf-8', level=logging.DEBUG)

#Input - Match id in str form
#Output - merged_score_ids - id and overall score for each player in a match
#       - match_stats['time'] - the date of the match
#       - match_stats['submitted'] - The date the match scores were submitted
#       - match_stats['maps'] - The maps played
#       - match_stats['round'] - The week the match was played in
#Alt    - None
# Gets the match stats needed for the database
def get_etf2l_stats(match: str):
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
            merged_score_ids = player_score_ids_c1 | player_score_ids_c2
            return merged_score_ids, match_stats['time'], match_stats['submitted'], match_stats['maps'], match_stats['round']
    else:
        while web.status_code == 429:
            web = requests.get(url)
        print(url, ' ', web.status_code)
    return

#Input  - id64 - list of player ids in string form
#       - before - The time the game was meant to be played
#       - after - The time the game scores were submitted
#       - etf2l_maps - The list of maps
#Output       - Output a list of the logs believed to have been played
#Gets the ids, and join them. Parses them through a map filter, a time filter and a title filter to get the suspected logs
def get_logs_stats(id64: list[str], before: int, after: int, etf2l_maps: list[str]) -> list[Any]:
    join_ids = 'player=' + ','.join(id64)
    
    logs_request_url = f"http://logs.tf/api/v1/log?" + join_ids
    potential_logs = requests.get(logs_request_url).json().get('logs')
    log_with_map = {log['id']: log['map'] for log in potential_logs}
    good_map_log_ids: list[Any] = [log for log in potential_logs if log['id'] in filter_logs_by_map(log_with_map, etf2l_maps)]
    final_logs: list[Any] = [log for log in good_map_log_ids if filter_logs_by_time(log, before, after) and filter_titles(log['title'])]
    return final_logs

#Input  - log - The log id 
#       - before - The time the game was meant to be played before
#       - after - the time the game scores were submitted
#       - Output - bool of if the times are between the log date
def filter_logs_by_time(log, before, after):
    if before < log.get('date') < after:
        return True
    return False

#Input  - log_with_map - a dictionary with the log id and the map playyed
#       - etf2l_maps - The maps played in that etf2l match
#Output - Filtered ids that match the etf2l played maps
def filter_logs_by_map(log_with_map, etf2l_maps):
    ids = []
    #Filter the etf2l maps into their componant parts
    filtered_etf2l_maps = [filter_maps(emap) for emap in etf2l_maps]
    for k, v in log_with_map.items():
        if fmap := filter_maps(v):
            if fmap in filtered_etf2l_maps:
                ids.append(k)
    return ids

#Input  - map - the full map name
#Output - a lowered, reduced complexity map name
def filter_maps(map):
    map_split = map.split('_')
    if len(map_split) < 2:
        return False
    map = map_split[0] + "_" + map_split[1]
    return map.lower()

#Input - title - The logs.tf log title
#Output - If serveme is in the title (not combined log)
def filter_titles(title):
    if 'serveme.tf' in title:
        return True
    return False

#Inputs  - pickeList - A string of the pickled list of etf2l match ids
#Outputs - ids - a list of all the log ids in all matches
#        - id64_scores - a dictionary of ids and the map scores
#        - weeks - A list of the weeks that games were played
def get_log_ids(pickeList):     
    with open(pickeList, "rb") as fp:
            match_ids = pickle.load(fp)
    ids = []
    id64_scores = {}
    weeks = []
    for match in match_ids:
        if get_etf2l_stats(match) is not None:
            id64_score, game_time, submitted_time, maps, week = get_etf2l_stats(match)
            logs = get_logs_stats(id64_score.keys(), game_time, submitted_time, maps)
            if logs == []:
                logging.info('Missing match: {}'.format(match))
            ids.append([log['id'] for log in logs])
            id64_scores = id64_scores | id64_score
            weeks.append(week)
        else: continue
    return ids, id64_scores, weeks