import requests

RIOTAPI = 'RGAPI-17e9e539-6fbf-4e46-a715-25ec17bb6710'

def getFiveMatches(puuid):
    API_URL = f'https://sea.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count='
    COUNT = 5

    url = API_URL + str(COUNT)
    headers = {
        'X-Riot-Token': RIOTAPI
    }
    response = requests.get(url, headers=headers)
    matches = response.json()
    
    # print(matches)
    return matches


def getMatchDetails(gameId, puuid):  # 只有puuid玩家的資料
    API_URL = 'https://sea.api.riotgames.com/lol/match/v5/matches/'

    url = API_URL + gameId
    headers = {
        'X-Riot-Token': RIOTAPI
    }
    response = requests.get(url, headers=headers)
    match = response.json()

    participants = match["info"]["participants"]
    
    for participant in participants:
        if participant["puuid"] == puuid:
            playerInfo = participant
            break  
    
    # print(match)
    return playerInfo