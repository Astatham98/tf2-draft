import requests
from get_log_ids import get_log_ids
from steamid_converter import Converter
import sqlite3

def log_parser(pickleList):
    ids, id64_score, id64_week = get_log_ids(pickleList)
    for match in ids:
        for log in match:
            log_json = requests.get('http://logs.tf/json/{}'.format(log)).json()
            if not log_json['success']:
                return
            else:
                players = log_json['players']
                time = log_json['length']
                for player_id, player_values in players.items():
                    player_id64 = Converter.to_steamID64(player_id)
                    mainClass = getMainClass(player_values)
                    score = id64_score.get(player_id64)
                    week = id64_week.get(player_id64)
                    print(week)
                    match mainClass:
                        case 'scout':
                            scout_stats = get_scout_stats(player_values, time)

                            put_scout_db(scout_stats, score, player_id64, week)
                        case 'soldier':
                            soldier_stats = get_soldier_stats(player_values, time)

                            put_soldier_db(soldier_stats, score, player_id64, week)
                        case 'demoman':
                            demoman_stats = get_demoman_stats(player_values, time)

                            put_demoman_db(demoman_stats, score, player_id64, week)
                        case 'medic':
                            med_stats = get_medic_stats(player_values,  time)
                            
                            put_medic_db(med_stats, score, player_id64, week)

    con = sqlite3.connect("s45")
    cur = con.cursor()
    cur.execute("SELECT * FROM MEDIC")
    res = cur.fetchall()
    for res in res:
        print(res)
    con.close()
                            
                    
                 
def getMainClass(player):
    class_stats = player['class_stats']
    best_time = 0
    mainClass = ''
    for stats in class_stats:
        if stats['total_time'] > best_time:
            mainClass = stats['type']
            best_time = stats['total_time']
    return mainClass

def get_medic_stats(player, time):
    kills = player['kills']
    deaths = player['deaths']
    assists = player['assists']
    kapd = player['kapd']
    ubers = player['ubers']
    drops = player['drops']
    heals = player['heal']  
    
    heals_per_min = int(heals / (time/60))
    airshots = player['as']
    return [kills, deaths, assists, kapd, ubers, drops, heals_per_min, airshots]
def get_demoman_stats(player, time):
    kills = player['kills']
    deaths = player['deaths']
    assists = player['assists']
    kapd = player['kapd']
    airshots = player['as']
    dmg = player['dmg_real']
    dpm = int(dmg / (time/60))
    
    return [kills, deaths, assists, kapd, airshots, dpm]
def get_soldier_stats(player, time):
    kills = player['kills']
    deaths = player['deaths']
    assists = player['assists']
    kapd = player['kapd']
    airshots = player['as']
    dmg = player['dmg_real']
    dpm = int(dmg / (time/60))
    
    return [kills, deaths, assists, kapd, airshots, dpm]
def get_scout_stats(player, time):
    kills = player['kills']
    deaths = player['deaths']
    assists = player['assists']
    kapd = player['kapd']
    dmg = player['dmg_real']
    dpm = int(dmg / (time/60))
    
    return [kills, deaths, assists, kapd, dpm]

def put_medic_db(stats, score, id, week):
    idweek = id + "_" + week
    to_insert = [idweek] + [id] + stats + [score]
    
    con = sqlite3.connect("s45")
    cur = con.cursor()
    
    cur.execute(
    """CREATE TABLE if not exists MEDIC (IDWEEK VARCHAR(255), ID INT, KILLS int, DEATHS INT, ASSISTS INT, KAPD VARCHAR(255), UBERS INT, DROPS INT, HPM INT, AIRSHOTS INT, SCORE INT);""")
    cur.execute("INSERT INTO MEDIC VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", to_insert)
    con.commit()
    con.close()
    
def put_demoman_db(stats, score, id, week):
    idweek = id + "_" + week
    to_insert = [idweek] + [id] + stats + [score]
    
    con = sqlite3.connect("s45")
    cur = con.cursor()
    
    cur.execute(
        """CREATE TABLE if not exists DEMOMAN (IDWEEK VARCHAR(255), ID INT, KILLS int, DEATHS INT, ASSISTS INT, KAPD VARCHAR(255), AIRSHOTS INT, DPM INT, SCORE INT);""")
    cur.execute("INSERT INTO DEMOMAN VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", to_insert)
    con.commit()
    con.close()
    
def put_soldier_db(stats, score, id, week):
    idweek = id + "_" + week
    to_insert = [idweek] + [id] + stats + [score]
    
    con = sqlite3.connect("s45")
    cur = con.cursor()
    
    cur.execute(
        """CREATE TABLE if not exists SOLDIER (IDWEEK VARCHAR(255), ID INT, KILLS int, DEATHS INT, ASSISTS INT, KAPD VARCHAR(255), AIRSHOTS INT, DPM INT, SCORE INT);""")
    cur.execute("INSERT INTO SOLDIER VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", to_insert)
    con.commit()
    con.close()
    
def put_scout_db(stats, score, id, week):
    idweek = str(id) + "_" + week
    to_insert = [idweek] + [id] + stats + [score]
    
    con = sqlite3.connect("s45")
    cur = con.cursor()
    
    cur.execute(
        """CREATE TABLE if not exists SCOUT (IDWEEK VARCHAR(255), ID INT, KILLS int, DEATHS INT, ASSISTS INT, KAPD VARCHAR(255), DPM INT, SCORE INT);""")
    cur.execute("INSERT INTO SCOUT VALUES(?, ?, ?, ?, ?, ?, ?, ?)", to_insert)
    con.commit()
    con.close()
    
log_parser('prem_match_ids_prev')