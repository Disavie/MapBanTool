import requests
import json
import time
import threading
import multiprocessing
import unicodedata
import os
import pprint
from os import listdir
from os.path import isfile, join

tempc = "src/cache/temp.cache"
gloabal_completion_counter = 0
amount_of_matches_to_count = 999
teamname = ''
TEAMIDMEM = ''

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
    onlyfiles = [f for f in listdir('src/cache/') if isfile(join('src/cache', f))]

    return f'{url}.cache' in onlyfiles
def cache_as_dictionary(data):
    match_id = data.get('match_id')
    path = f'src/cache/{match_id}.cache'
    f = open(path,'w')
    json.dump(data,f,indent = 3)
    f.close()
def get_map_pool():
    f = open('mappool.txt','r')
    data = f.read()
    data_into_list = data.split("\n")
    return data_into_list

def retrieve_from_file(file_title,elem1,comparison):
    f = open(f'src/cache/{file_title}.cache','r')
    file_data = json.load(f)

    faction_to_get = 'faction1'
    if file_data['faction2']['team_id'] == comparison:
        faction_to_get = 'faction2'
    try:
        data = file_data[faction_to_get][elem1]
    except KeyError:
        print('{MapBanTool}\tKey Error blocked')
        return []
    return data

def get_data(match_id,team_id):

    global rooms
    global gloabal_completion_counter
    return_dict = {
                    'picks':[],
                    'drops':[]
                    }

    if check_data_cache(match_id):
        print('{MapBanTool}\tFound data from',match_id,'in cache')
        picks = retrieve_from_file(match_id,'picks',team_id)
        drops = retrieve_from_file(match_id,'drops',team_id)
        return_dict['picks'] = picks
        return_dict['drops'] = drops
        return return_dict

    key = '6cd564bf-065b-4715-a59e-4fc060e2737a'
    headers = {'Authorization': f'Bearer {key}'}
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

            f = open(tempc,'w')
            json.dump(temp_map_guids,f,indent = 3)
            f.close()
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
    print('{MapBanTool}\tCollected data from ',match_id)
    cache_as_dictionary(the_juice)

    picks = retrieve_from_file(match_id,'picks',team_id)
    drops = retrieve_from_file(match_id,'drops',team_id)
    return_dict['picks'] = picks
    return_dict['drops'] = drops
    return return_dict

def get_rooms(team_id):

    global tempc
    global teamname
    input = team_id

    key = '6cd564bf-065b-4715-a59e-4fc060e2737a'
    headers = {'Authorization': 'Bearer '+key}

    req_teamURL = 'https://open.faceit.com/data/v4/teams/'+input
    response = requests.get(req_teamURL,headers=headers)
    data = response.json()
    with open(tempc,'w') as f:
        json.dump(data,f,indent=3)

    f = open(tempc)
    data = json.load(f) #loads file 'f' as a dictionary
    f.close()
    teamname = data['name']
    players = []
    for i in data['members']:
        players.append([i.get('nickname'),i.get('user_id')])

    match_ids = []
    flag = False
    for player in players:
        print('{MapBanTool}\tFetching data of ',player[0], '(',player[1],')')
        if(flag):
            break

        f = open(tempc,'w')

        player_id = player[1]
        PLAYER_HISTORY_URL = "https://open.faceit.com/data/v4/players/"+player_id+"/history?game=ow2,limit=100"
        response = requests.get(PLAYER_HISTORY_URL,headers=headers)
        data = response.json()
        json.dump(data,f,indent=3)
        f.close()

        f = open(tempc,'r')
        data = json.load(f)
        f.close()

        for i in data['items']:
 
            if len(match_ids) >= amount_of_matches_to_count:
                flag = True
                break

            id_team1 = i.get('teams').get('faction1').get('team_id')
            id_team2 = i.get('teams').get('faction2').get('team_id') 

            if(id_team1 == input or id_team2 == input):
                current_id = i.get('match_id')
                if current_id not in match_ids:
                    print('{MapBanTool}\tAdded '+current_id+' to match_ids')
                    match_ids.append(current_id)

    return match_ids

def count_map_wins(match_ids,map_pool,team_id):

    winrates_dict = {}
    for map in map_pool:
        #winrates_dict[map][0] win% [1] counts times played [2] counts times won
        winrates_dict[map] = [0,0,0]

    for match_id in match_ids:
        try:
            f = open(f'src/cache/{match_id}.cache')
        except FileNotFoundError:
            print('{MapBanTool}\tNo data from '+match_id)
            continue
        data = json.load(f)
        f.close()

        maps_played = data['maps_played']
        for map in maps_played:
  
            if map in map_pool:
                winrates_dict[map][1]+=1
                if maps_played[map] == team_id:
                    winrates_dict[map][2]+=1
                    perc = winrates_dict[map][2] / winrates_dict[map][1]
                    winrates_dict[map][0] = format(perc, '.2%')

    return winrates_dict

def get_winrates(team_id):
    
    global tempc
    key = '6cd564bf-065b-4715-a59e-4fc060e2737a'
    headers = {'Authorization': 'Bearer '+key}

    req_teamURL = 'https://open.faceit.com/data/v4/teams/'+team_id+'/stats/ow2'
    response = requests.get(req_teamURL,headers=headers)
    data = response.json()
    with open(tempc,'w') as f:
        json.dump(data,f,indent=3)
    f = open(tempc)
    data = json.load(f) #loads file 'f' as a dictionary
    f.close()

    segments = data.get('segments')
    allmaps_data = {}
    for map_info in segments:
        currentmap_winrate = map_info.get('stats').get('Win rate %')
        currentmap_timesplayed = map_info.get('stats').get('Matches')
        currentmap = map_info.get("label")
        if currentmap == 'Esperance':
            currentmap = 'Esperanca'
        allmaps_data[currentmap] = [currentmap_winrate,currentmap_timesplayed]

    with open('src/cache/winrates.cache','w') as f:
        json.dump(allmaps_data,f,indent=3)
    return allmaps_data

def update_config(setting,change):
    with open("src/config.txt",'r') as f:
        config = f.readlines()
    i = 0
    for s in config:
        i = s.find(setting)
        if(i != -1):
            break
    config[i] = setting+'='+str(change)
    config[i].replace(' ','')

    with open("src/config.txt",'w') as f:
        for line in config:
            f.write(line)
            f.write('\n')
    return

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
                print(f"Deleted file: {file_path}")
    except Exception as e:
        print(f"Error: {e}")

def check_valid(team_id):

    key = '6cd564bf-065b-4715-a59e-4fc060e2737a'
    headers = {'Authorization': 'Bearer '+key}
    base = f'https://open.faceit.com/data/v4/teams/{team_id}'
    response = requests.get(base,headers=headers)
    return response.status_code

def get_user_input():

    global TEAMIDMEM
    global amount_of_matches_to_count

    front = '{MapBanTool}\t'

    options = {
                'help' : f'show all commands',
                'run' : f'scrape data from team by id',
                'update' : f'recalculate data using more recent matches',
                'clear' : f'clears cache',
                'amount' : f'choose amount of matches to sample (leave blank or * to get all)',
                'id' : 'update id to get data of',
                'quit' : 'quits app'
                }

    inp = input(f'{front}>>> ')
    if inp == 'run' or inp == 'r':
        responsecode = check_valid(TEAMIDMEM)
        if responsecode == 200:
            main(TEAMIDMEM)
        else:
            print(f'{front}Enter a valid team id')

    elif inp == 'update':
        responsecode = check_valid(TEAMIDMEM)
        if responsecode == 200:
            main(TEAMIDMEM)
        else:
            print(f'{front}Enter a valid team id')
    elif inp == 'help':
        print()
        for option in options:
            print(f'\t{option}\t{options[option]}')
        print()
    elif inp == 'clear':
        delete_all_files('src/cache/')
    elif inp == 'amount':
        inp = input(f'{front}Enter amount of games to sample\n{front}>>> ')
        amount_of_matches_to_count = int(inp)
    elif inp == 'id':
        print(f'{front}Current id is {TEAMIDMEM}')
        inp = input(f'{front}Enter team id or leave blank to use current\n{front}>>> ')
        if inp.strip() != '':
            TEAMIDMEM = inp
            print(f'{front}Updated id to {TEAMIDMEM}')
        else:
            print(f'{front}Current id is {TEAMIDMEM}')

    elif inp == 'quit' or inp == 'q':
        exit()
    else:
        if inp.strip() == '':
            return
        responsecode = check_valid(inp)
        if responsecode == 200:
            TEAMIDMEM = inp
        else:
            print(f'{front}{inp} os not recognized as a command')





    
def main(team_id):
    global teamname
    global rooms
    global amount_of_matches_to_count
    global tempc


    print("{MapBanTool}\tCollecting room codes & extracting key")
    if amount_of_matches_to_count == '*':
        amount_of_matches_to_count = 999
    else:
        amount_of_matches_to_count = int(amount_of_matches_to_count)

    rooms = get_rooms(team_id)

    print("{MapBanTool}\tCollected",len(rooms),"room codes")

    dict = {
            'picks':[],
            'drops':[]
            }
    
    for match_id in rooms:
        temp = get_data(match_id,team_id)
        #list1 = temp['picks']
        #list2 = temp['drops']
        dict['picks'] += temp['picks']
        dict['drops'] += temp['drops']


    pool = get_map_pool()
    map_winrates = count_map_wins(rooms,pool,team_id)
    
    #counting picks
    count = 0
    output_dict = {}
    for item in pool:
        output_dict[item] = {}
        output_dict[item]['picks'] = dict['picks'].count(item)
        output_dict[item]['drops'] = dict['drops'].count(item)

    write_to_output(teamname,output_dict,map_winrates)


    print("{MapBanTool}\tCleaning up...")



print('{MapBanTool}\tEnter id of team or type help for options')
while(True):
    get_user_input()
quit()