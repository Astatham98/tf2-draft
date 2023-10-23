import requests
from get_log_ids import get_log_ids
from steamid_converter import Converter

def log_parser(pickleList):
    ids, id64_score = get_log_ids(pickleList)
    for match in ids:
        for log in match:
            log_json = requests.get('http://logs.tf/json/{}'.format(log)).json()
            if not log_json['success']:
                return
            else:
                players = log_json['players']
                for player_id, player_values in players.items():
                    player_id64 = Converter.to_steamID64(player_id)
                    mainClass = getMainClass(player_values)
                    match mainClass:
                        case 'scout':
                            get_scout_stats(player_values, id64_score.get(player_id64))
                        case 'soldier':
                            get_soldier_stats(player_values, id64_score.get(player_id64))
                        case 'demoman':
                            get_demoman_stats(player_values, id64_score.get(player_id64))
                        case 'medic':
                            get_medic_stats(player_values, id64_score.get(player_id64))
                    
                 
def getMainClass(player):
    class_stats = player['class_stats']
    best_time = 0
    mainClass = ''
    for stats in class_stats:
        if stats['total_time'] > best_time:
            mainClass = stats['type']
            best_time = stats['total_time']
    return mainClass

def get_medic_stats(player, score):
    pass
def get_demoman_stats(player, score):
    pass
def get_soldier_stats(player, score):
    pass
def get_scout_stats(player, score):
    pass

log_parser('prem_match_ids')