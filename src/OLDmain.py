import requests
import json

tempc = "temp.cache"

input = input(("{MapBanTool}\t Enter team id to aggregate data\n{MapBanTool}\t> "))

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

for i in players:
    print(i)

match_ids = []
for player in players:

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
        team1_playing = i.get('teams').get('faction1').get('team_id')
        team2_playing = i.get('teams').get('faction2').get('team_id')
        if(team1_playing == input or team2_playing == input):
            match_ids.append(i.get('match_id'))

#checking all unique room ids
unique = []
count = 0
for id in match_ids:
    if id not in unique:
        count+=1
        unique.append(id)
print("there were ", count, " duplicates")

with open('ids.cache','w') as f:
    for id in match_ids:
        f.write(id)
        f.write('\n')