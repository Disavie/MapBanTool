import requests
import json
import time
import threading
import unicodedata
import os
import pprint
from os import listdir
from os.path import isfile, join
import sys
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib as mpl

CLIENT_API_KEY = '5fde12b7-1660-4565-8f41-85492c4b7479'
AMOUNT = 100
teamname = ''
glob_match_ids = []
glob_results = {
                'picks':[],
                'drops':[]
                }
lock = threading.Lock()

def delete_file(file_path):
    """
    Deletes a specific file if the given path is valid and the file exists.
    
    Parameters:
        file_path (str): The path to the file to be deleted.
        
    Returns:
        str: Success or error message.
    """
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
            return f"File '{file_path}' has been deleted successfully."
        else:
            return f"No such file found: '{file_path}'"
    except Exception as e:
        return f"An error occurred while trying to delete the file: {e}"
def has_non_unicode_characters(s):
    try:
        # Attempt to encode the string to ASCII
        s.encode('ascii')
    except UnicodeEncodeError:
        # If encoding fails, it contains non-ASCII characters
        return True
    return False
def convert_to_english(input_string):
    """
    Converts non-English characters in a string to their similar English counterparts.
    
    Args:
        input_string (str): The input string with non-English characters.

    Returns:
        str: A string with characters converted to their English counterparts.
    """
    # Normalize the string to decompose characters with accents
    normalized_string = unicodedata.normalize('NFD', input_string)
    # Filter out diacritical marks (combining marks)
    english_string = ''.join(
        char for char in normalized_string if unicodedata.category(char) != 'Mn'
    )
    # Return the string in NFC format for proper composition
    return unicodedata.normalize('NFC', english_string)
def check_data_cache(url):
    onlyfiles = [f for f in listdir('cache/') if isfile(join('cache', f))]
    return f'{url}.cache' in onlyfiles
def cache_as_dictionary(filename,data):
    path = f'cache/{filename}.cache'
    f = open(path,'w')
    json.dump(data,f,indent = 3)
    f.close()
def retrieve_from_file(file_title,elem1,comparison):
    global lock

    with lock:
        f = open(f'cache/{file_title}.cache','r')
        file_data = json.load(f)
        f.close()
    faction_to_get = 'faction1'
    if comparison == 'TIME':
        return file_data['date']
    if file_data['faction2']['team_id'] == comparison:
        faction_to_get = 'faction2'
    try:
        data = file_data[faction_to_get][elem1]
    except KeyError:
        #print('{MapBanTool}\tKey Error blocked')
        return []
    return data
def get_data(match_id,team_id,time_requirement):

    return_dict = {
                    'picks':[],
                    'drops':[]
                    }

    if check_data_cache(match_id):
        #print('{MapBanTool}\tFound data from',match_id,'in cache')
        time = retrieve_from_file(match_id,'date','TIME')
        if time < time_requirement:
            return return_dict
        picks = retrieve_from_file(match_id,'picks',team_id)
        drops = retrieve_from_file(match_id,'drops',team_id)
        return_dict['picks'] = picks
        return_dict['drops'] = drops
        return return_dict

    global CLIENT_API_KEY
    headers = {'Authorization': f'Bearer {CLIENT_API_KEY}'}
    v4base = 'https://open.faceit.com/data/v4'
    v1base = 'https://api.faceit.com/democracy/v1'
    url = f"{v4base}/matches/{match_id}"

    response = requests.get(url+'/stats',headers=headers)
    match_stats = response.json()
    try:
        rounds = match_stats['rounds']
    except KeyError:
        return return_dict

    map_winners = {}
    for round in rounds:
        winner = round['round_stats']['Winner']
        map = round['round_stats']['Map']
        map_winners[map] = winner

    response = requests.get(url,headers=headers)
    match_data = response.json()

    temp_map_guids = {}
    try:
        entities = match_data['voting']['map']['entities']
    except KeyError:
        return return_dict
    for veto in entities:
        name = veto['name']
        if name == 'Esperan\u00e7a':
            name = convert_to_english(name)

        temp_map_guids[veto['guid']] = name
    
    for guid in temp_map_guids:
        if guid in map_winners:
            map_winners[temp_map_guids[guid]] = map_winners[guid]
            map_winners.pop(guid)

    the_juice = {}
    faction1_id = match_data.get('teams').get('faction1').get('faction_id')
    faction2_id = match_data.get('teams').get('faction2').get('faction_id')

    faction_to_collect = 'faction1'
    if team_id == faction2_id:
        faction_to_collect = 'faction2'
    try:
        start_time_unix = match_data['started_at']
    except KeyError:
        start_time_unix = 0
    if start_time_unix < time_requirement:
        print(f'stopped {match_id} from being collected, it started at the wrong time')
        return return_dict
    

    the_juice['match_id'] = match_id
    the_juice['date'] = start_time_unix
    the_juice['maps_played'] = {}
    for map in map_winners:
        the_juice['maps_played'][map] = map_winners[map]
    the_juice['faction1'] = {'team_id':faction1_id,'picks':[],'drops':[]}
    the_juice['faction2'] = {'team_id':faction2_id,'picks':[],'drops':[]}


    url = f"{v1base}/match/{match_id}/history"
    response = requests.get(url)
    veto_data = response.json()


    tickets = veto_data['payload']['tickets']
    team1_picks = []
    team1_bans = []
    team2_picks = []
    team2_bans = []
    for ticket in tickets:
        entities = ticket['entities']
        for entity in entities:

            pick_or_drop = entity['status']
            try:
                map_for_guid = temp_map_guids[entity['guid']]
            except KeyError:
                continue
            if entity['selected_by'] == 'faction1':
                match pick_or_drop:
                    case 'pick':
                        team1_picks.append(temp_map_guids[entity['guid']])
                    case 'drop':
                        team1_bans.append(temp_map_guids[entity['guid']])
            else:
                match pick_or_drop:
                    case 'pick':
                        team2_picks.append(temp_map_guids[entity['guid']])
                    case 'drop':
                        team2_bans.append(temp_map_guids[entity['guid']])

    the_juice['faction1']['picks'] = (team1_picks)
    the_juice['faction1']['drops'] = (team1_bans)
    the_juice['faction2']['picks'] = (team2_picks)
    the_juice['faction2']['drops'] = (team2_bans)
    #print('{MapBanTool}\tCollected data from ',match_id)
    cache_as_dictionary(match_id,the_juice)

    return_dict['picks'] = the_juice[faction_to_collect]['picks']
    return_dict['drops'] = the_juice[faction_to_collect]['drops']
    return return_dict
def get_rooms_helper(player_id,team_id):
        global glob_match_ids
        global lock
        global CLIENT_API_KEY

        PLAYER_HISTORY_URL = f"https://open.faceit.com/data/v4/players/{player_id}/history?game=ow2,limit=50"
        headers = {'Authorization': 'Bearer '+CLIENT_API_KEY}
        response = requests.get(PLAYER_HISTORY_URL,headers=headers)
        data = response.json()

        match_ids = []
        for i in data['items']:
            id_team1 = i.get('teams').get('faction1').get('team_id')
            id_team2 = i.get('teams').get('faction2').get('team_id') 

            if(id_team1 == team_id or id_team2 == team_id):
                current_id = i.get('match_id')
                if current_id not in match_ids:
                        match_ids.append(current_id)

        with lock:
            glob_match_ids+=match_ids

def get_rooms(team_id):

    global teamname
    global glob_match_ids
    global CLIENT_API_KEY
    global AMOUNT
    input = team_id

    headers = {f'Authorization': f'Bearer {CLIENT_API_KEY}'}

    req_teamURL = 'https://open.faceit.com/data/v4/teams/'+input
    response = requests.get(req_teamURL,headers=headers)
    if(response.status_code == 429):
        quit()
    data = response.json()

    teamname = data['name']
    players = []
    for i in data['members']:
        players.append([i.get('nickname'),i.get('user_id')])

    threads = []
    for player in players:
        player_id = player[1]
        thread = threading.Thread(target=get_rooms_helper,args=(player_id,team_id))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

def count_map_wins(match_ids,map_pool,team_id,time_requirement):

    winrates_dict = {}
    for map in map_pool:
        #winrates_dict[map][0] win% [1] counts times played [2] counts times won
        winrates_dict[map] = [0,0,0]

    for match_id in match_ids:
        try:
            f = open(f'cache/{match_id}.cache')
        except FileNotFoundError:
            #print('{MapBanTool}\tNo data from '+match_id)
            continue
        data = json.load(f)
        f.close()
        if data['date'] < time_requirement:
            return winrates_dict

        maps_played = data['maps_played']
        for map in maps_played:
  
            if map in map_pool:
                winrates_dict[map][1]+=1
                if maps_played[map] == team_id:
                    winrates_dict[map][2]+=1
                    perc = winrates_dict[map][2] / winrates_dict[map][1]
                    winrates_dict[map][0] = int(perc*100)

    return winrates_dict
def write_to_output(filename,dict1,dict2):
    f = open(f'output_files/{filename}.txt', "w")

    # Define fixed column widths
    col_widths = [25, 10, 10, 10, 10]
    heading = f"{'Map'.ljust(col_widths[0])}{'#Picked'.ljust(col_widths[1])}{'#Drops'.ljust(col_widths[2])}{'Win%'.ljust(col_widths[3])}{'#Played'.ljust(col_widths[4])}\n"
    f.write(heading)

    for element in dict1:
        p =dict1[element]['picks']
        d =dict1[element]['drops']
        try:
            wr = dict2[element][0]
            tp = dict2[element][1]
        except KeyError:
            wr = 'unknown'
            tp = 'unknown'
        f.write(
            f"{element.ljust(col_widths[0])}"
            f"{str(p).ljust(col_widths[1])}"
            f"{str(d).ljust(col_widths[2])}"
            f"{str(wr).ljust(col_widths[3])}"
            f"{str(tp).ljust(col_widths[4])}\n"
        )

    f.close()
def delete_all_files(directory):
    try:
        # Iterate over all files in the directory
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            # Check if it's a file and delete it
            if os.path.isfile(file_path):
                os.remove(file_path)
                #print(f"Deleted file: {file_path}")
    except Exception as e:
        pass
        #print(f"Error: {e}")
def check_valid(team_id):
    global CLIENT_API_KEY
    key = '6cd564bf-065b-4715-a59e-4fc060e2737a'
    headers = {'Authorization': 'Bearer '+CLIENT_API_KEY}
    base = f'https://open.faceit.com/data/v4/teams/{team_id}'
    response = requests.get(base,headers=headers)
    return response.status_code
def plot_data(data):
    # Extract data for plotting
    maps = list(data.keys())
    picks = [data[map_]["picks"] for map_ in maps]
    drops = [data[map_]["drops"] for map_ in maps]
    winrates = [data[map_]["winrate"] for map_ in maps]
    #plt.style.use('seaborn-v0_8-pastel')
    plt.style.use('dark_background')

    # Create the plot
    fig, ax1 = plt.subplots(figsize=(6.2, 4),dpi=100)

    # Check if Calibri is available
    if 'Calibri' in [f.name for f in mpl.font_manager.fontManager.ttflist]:
        # Set the default font family
        plt.rcParams['font.family'] = 'Calibri'
    else:
        print("Calibri font not found. Using default font.")
    plt.xticks(fontsize=8)


    # X-axis positions
    x = np.arange(len(maps))
    width = 0.25  # Width of each bar

    # Bar chart for picks, drops, and winrate
    bar1 = ax1.bar(x - width, picks, width, label="Picks", color="skyblue")
    bar2 = ax1.bar(x, drops, width, label="Drops", color="navajowhite")
    ax2 = ax1.twinx()
    bar3 = ax2.bar(x + width, winrates, width, label="Winrate (%)", color="mediumseagreen")


    ax1.set_ylabel("Picks/Drops")
    ax1.set_xticks(x)
    ax1.set_xticklabels(maps, rotation=45, ha="right")
    ax1.grid(axis="y", linestyle="-", alpha=0.5)

    # Formatting the second axis
    ax2.set_ylabel("Winrate (%)")

    ax1.legend([bar1,bar2,bar3],["Picks","Drops","Win%"],loc='lower left', bbox_to_anchor=(0,1.02,1,0.2),mode='expand',ncol=3)

    # Title and layout
    plt.tight_layout()

    return fig
def get_data_helper(match_id,team_id,time_requirement):
    global lock
    global glob_results
    temp =get_data(match_id,team_id,time_requirement)
    with lock:
        glob_results['picks']+=temp['picks']
        glob_results['drops']+=temp['drops']   

    
def main(team_id,map_pool,time_requirement):
    global teamname
    global glob_results
    global glob_match_ids
    glob_match_ids = []
    glob_results = {
                'picks':[],
                'drops':[]
                }
    ALLMAPS = [
            'Antarctic Peninsula','Busan','Ilios','Lijiang Tower','Nepal','Oasis','Samoa',
            'Blizzard World','Eichenwalde','Hollywood','King\'s Row','Midtown','Numbani','Paraiso',
            'Colosseo','Esperanca','New Queen Street','Runasapi',
            'New Junk City','Suravasa',
            'Hanaoka','Throne of Anubis',
            'Circuit Royal','Dorado','Havana','Junkertown','Rialto','Route 66','Shambali Monastery','Watchpoint Gibraltar'
            ]

    if check_data_cache(team_id):
        f = open(f'cache/{team_id}.cache')
        data = json.load(f)
        f.close()
        output_dict = {}
        for map in data:
            if map in map_pool:
                output_dict[map]=data[map]
        return output_dict


    get_rooms(team_id)

    
    threads = []

    for match_id in glob_match_ids:
        thread = threading.Thread(target=get_data_helper,args=(match_id,team_id,time_requirement))
        threads.append(thread)
        thread.start()        

    for thread in threads:
        thread.join()

    ALL_MAPWINRATES = count_map_wins(glob_match_ids,ALLMAPS,team_id,time_requirement)
    output_dict_allmaps = {}

    for map in ALLMAPS:
        output_dict_allmaps[map] = {}
        output_dict_allmaps[map]['picks'] = glob_results['picks'].count(map)
        output_dict_allmaps[map]['drops'] = glob_results['drops'].count(map)


    for map in ALL_MAPWINRATES:
        output_dict_allmaps[map]['winrate'] = ALL_MAPWINRATES[map][0]


    cache_as_dictionary(team_id,output_dict_allmaps)


    f = open(f'cache/{team_id}.cache')
    data = json.load(f)
    f.close()
    output_dict = {}
    for map in data:
        if map in map_pool:
            output_dict[map]=data[map]

    return output_dict
