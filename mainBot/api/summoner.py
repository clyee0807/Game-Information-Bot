import requests, os, time
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

BASE_DIR = Path(__file__).resolve().parent.parent

RIOTAPI = 'RGAPI-17e9e539-6fbf-4e46-a715-25ec17bb6710'
VERSION = '14.4.1'

def get_summoner_info(summoner_name):
    API_URL = 'https://tw2.api.riotgames.com/lol/summoner/v4/summoners/by-name/'
    # url = API_URL + summoner_name + '?api_key' + RIOTAPI
    url = API_URL + summoner_name
    headers = {
        'X-Riot-Token': RIOTAPI
    }
    response = requests.get(url, headers=headers)
    # response = requests.get(url)

    print(response.json())
    if response.status_code == 200:
        # id = response.json()['id']  # dX42yPW9Rp55Renay4bjE2I2HsBdtrG6oSQVJl0JeuN7Ju2KK5M0Jc9EzA
        # accountId = response.json()['accountId']  # i6vnDn1WjPdjRQP6yPbo1McS55_UQwKm8IC6ScfejPwiKu2TTZR65_dK
        puuid = response.json()['puuid']  # n9Ad3kMCf7v0qbQlClspFGU4XXhkdY8B1FEjSt6xuuN1F4OD7oHE0wg29wSBSQors0GC_5H6USH33Q
        name = response.json()['name']  # cLyee
        profileIconId = response.json()['profileIconId']  # 1392
        # revisionDate = response.json()['revisionDate']    # 1709222137974
        summonerLevel = response.json()['summonerLevel']  # 173
    else:
        print(f"Failed to fetch summoner info: HTTP {response.status_code}")
        return None
    
    icon_url = f'http://ddragon.leagueoflegends.com/cdn/{VERSION}/img/profileicon/{profileIconId}.png'
    response = requests.get(icon_url)
    path = os.path.join(BASE_DIR, 'img' , 'profileIcon' , f'{profileIconId}.png')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if response.status_code == 200:
        with open(path, 'wb') as file:
            file.write(response.content)
    else:
        print(f"Failed to fetch image: HTTP {response.status_code}")

    return name, summonerLevel, profileIconId, puuid

# get_summoner_info('cLyee')
# print(BASE_DIR)  # D:\CLY\CLYEE\projects\linebot_test\mainBot


# fetch summoner's recent 100 matches and analyze the relationship between the win rate
def analyze_summoner(summoner_name):
    puuid = get_summoner_info(summoner_name)[3]
    API_URL = f'https://sea.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count='
    COUNT = 100

    url = API_URL + str(COUNT)
    headers = {
        'X-Riot-Token': RIOTAPI
    }
    response = requests.get(url, headers=headers)
    matches = response.json()  # 100 matches gameId
    

    API_URL = 'https://sea.api.riotgames.com/lol/match/v5/matches/'
    request_interval = 1.0 / 20
    info = None
    participants_data = []
    for i in range(len(matches)):
        url = API_URL + matches[i]
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            match_details = response.json()  # 整個return的json
            info = match_details['info']['teams']
            teams = match_details['info']['teams']
            for participant in match_details['info']['participants']:
                participants_data.append(participant)
                
        else:
            print(f"Failed to retrieve data for match {matches[i]}, HTTP {response.status_code}")

        time.sleep(request_interval)

    df = pd.DataFrame(participants_data)
    features = ['kills', 'deaths', 'assists', 'goldEarned', 'totalDamageDealt', 'totalDamageTaken', 'timePlayed', 'damageDealtToBuildings']

    X = df[features]
    y = df['win']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=48)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"Model accuracy: {accuracy:.4f}")

    importances = model.feature_importances_
    for feature, importance in zip(features, importances):
        print(f"{feature}: {importance:.4f}")

    correlation_matrix = df[features + ['win']].corr()
    correlation_with_win = correlation_matrix['win'].drop('win') 
    print(correlation_with_win)

    return importances, correlation_with_win