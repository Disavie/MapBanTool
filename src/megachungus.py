import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import InvalidArgumentException
import threading
import multiprocessing

tempc = "src/cache/temp.cache"
bans_list = []
lock = threading.Lock()
gloabal_completion_counter = 0
rooms = []
amount_of_matches_to_count = 0

def has_non_unicode_characters(s):
    try:
        # Attempt to encode the string to ASCII
        s.encode('ascii')
    except UnicodeEncodeError:
        # If encoding fails, it contains non-ASCII characters
        return True
    return False
def replace_non_ascii_with_x(input_string):
    """
    Replaces any non-ASCII characters in the given string with 'x'.

    Args:
        input_string (str): The string to process.

    Returns:
        str: A new string with non-ASCII characters replaced by 'x'.
    """
    return ''.join(char if ord(char) < 128 else 'x' for char in input_string)

def check_data_cache(url):
    f = open('src/cache/storage.cache','r')
    data = json.load(f)
    f.close()
    value = data.get(url,-1)
    return value

def cache_as_dictionary(new_entries):
    f = open('src/cache/storage.cache','r')
    dict = json.load(f)
    f.close()
    dict.update(new_entries)
    with open('src/cache/storage.cache','w') as f:
        json.dump(dict,f,indent=3)

def get_data(url):

    global bans_list
    global rooms
    global gloabal_completion_counter
    list = check_data_cache(url)
    if list != -1:
        for elem in list:
            print('added',elem)
            bans_list.append(elem)
        gloabal_completion_counter+=1
        print('{MapBanTool}\t',gloabal_completion_counter,'/',len(rooms),'Found',url,'data in storage.cache')
        return list

    print("{MapBanTool}\t\tCollecting new data")
    options = Options()
    options.add_argument("--window-position=-2400,-2400")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)

    delay = 2
    mapbans_class_name = 'HistoryItem__Li-sc-dcb0c0ec-0.dfJFLi'
    veto_history_link_xpath ="//span[@data-testid='mapsVetoHistory']"
    driver.get(url)
    list = [] #List of WebElement
    try:
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, veto_history_link_xpath)))
        vetobutton = driver.find_element(By.XPATH,veto_history_link_xpath)
        vetobutton.click()
        list = driver.find_elements(By.CLASS_NAME,mapbans_class_name)
    except NoSuchElementException:
        print("{MapBanTool}\tget_data :NoSuchElementException blocked")
    except TimeoutException:
        print("{MapBanTool}\tget_data : TimeoutException blocked")

    with lock:
        for ban in list:
            text = ban.text
            fixed = replace_non_ascii_with_x(text)
            bans_list.append(fixed)
    gloabal_completion_counter+=1
    print('{MapBanTool}\t',gloabal_completion_counter,'/',len(rooms),"Collected data from '",url,"'")
    return_list = []
    for elem in list:
        text = elem.text
        fixed = replace_non_ascii_with_x(text)
        return_list.append(fixed)

    driver.quit()
    return return_list

def get_rooms(team_id):

    global tempc

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
        PLAYER_HISTORY_URL = "https://open.faceit.com/data/v4/players/"+player_id+"/history"
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
            name_team1 = i.get('teams').get('faction1').get('nickname')
            name_team2 = i.get('teams').get('faction2').get('nickname')

            id_team1 = i.get('teams').get('faction1').get('team_id')
            id_team2 = i.get('teams').get('faction2').get('team_id')    
            #if i.get('match_id') == '1-13e3fe45-3eec-4555-aeaa-63686685ca67':
            #    print('{MapBanTool}\tname_team1 :',name_team1,'\tname_team2 :',name_team2)
            #    print('{MapBanTool}\tid_team1 :',id_team1,'\tid_team2 :',id_team2)
            #    print(input)
            if(id_team1 == input or id_team2 == input):
                current_id = i.get('match_id')
                if current_id not in match_ids:
                    print('{MapBanTool}\tAdded '+current_id+' to match_ids')
                    match_ids.append(current_id)

    #checking all unique room ids
    unique = []
    count = 0
    for id in match_ids:
        if id not in unique:
            unique.append(id)
        else:
            count+=1
    print("{MapBanTool}\tFound and removed ", count, " duplicates")

    with open('src/cache/ids.cache','w') as f:
        for id in match_ids:
            f.write(id)
            f.write('\n')
    return unique

def get_teamname(team_id):
    
    global tempc
    key = '6cd564bf-065b-4715-a59e-4fc060e2737a'
    headers = {'Authorization': 'Bearer '+key}

    req_teamURL = 'https://open.faceit.com/data/v4/teams/'+team_id
    response = requests.get(req_teamURL,headers=headers)
    data = response.json()
    with open(tempc,'w') as f:
        json.dump(data,f,indent=3)

    f = open(tempc)
    data = json.load(f) #loads file 'f' as a dictionary
    f.close()
    name = data.get('name')
    print('{MapBanTool}\tTeam name :',name)
    return name

def update_config(setting,change):
    with open("src/config.txt",'r') as f:
        config = f.readlines()
    i = 0
    for s in config:
        i = s.find(setting)
        if(i != -1):
            break
    config[i] = setting+'='+change +'\n'
    with open("src/config.txt",'w') as f:
        for line in config:
            f.write(line)
    return

def main():
    global rooms
    global amount_of_matches_to_count
    global tempc

    id = input('{MapBanTool}\tEnter id of team to scrape data : \n{MapBanTool}\t>>> ')
    amount_of_matches_to_count = input('{MapBanTool}\tEnter # of matches to sample (type * to get all): \n{MapBanTool}\t>>> ')
    print("{MapBanTool}\tCollecting room codes & extracting key")
    if amount_of_matches_to_count == '*':
        amount_of_matches_to_count = 9999
    else:
        amount_of_matches_to_count = int(amount_of_matches_to_count)
    rooms = get_rooms(id)

    print("{MapBanTool}\tCollected",len(rooms),"room codes")

    newkey = get_teamname(id)
    dict = {}
    for room_url in rooms:
        room = 'https://www.faceit.com/en/ow2/room/'+room_url
        recent_bans = get_data(room)
        dict[room] = recent_bans
        
    
    global bans_list
    with open(tempc,'w') as f:
        for ban in bans_list:
            f.write(ban)
            f.write('\n')
    cache_as_dictionary(dict)

    update_config("key",newkey)
    print("{MapBanTool}\tCleaning up...")

main()
quit()