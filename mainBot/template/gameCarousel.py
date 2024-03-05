from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageAction, TemplateSendMessage, CarouselTemplate,  CarouselColumn
import requests, datetime

API_URL = 'https://sea.api.riotgames.com/lol/match/v5/matches/'
RIOTAPI = 'RGAPI-17e9e539-6fbf-4e46-a715-25ec17bb6710'
headers = {
    'X-Riot-Token': RIOTAPI
}

def createGameCarousel(summoner_name, matchIds):
    print(f'Creating carousel for {summoner_name}')
    print(f'matchIds: {matchIds}')
    
    player = []
    info = []

    for matchId in matchIds:
        url = API_URL + matchId
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            match_details = response.json() 
            participants = match_details['info']['participants']   
            
            # 只需要指定玩家的資料
            for participant in participants:
                if participant['summonerName'] == summoner_name:
                    player.append(participant)
                    info.append(match_details['info'])
                    break  
        else:
            print(f"Failed to retrieve data for match {matchId}, HTTP {response.status_code}")
    
    print(f'len(info) = {len(info)}')

    template_message = TemplateSendMessage(
        alt_text='Game Carousel template', 
        template= CarouselTemplate(columns=[
            CarouselColumn(
                thumbnail_image_url=f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{player[0]['championName']}_0.jpg",
                title=player[0]['championName'],
                text=f"{'WIN' if player[0]['win'] else 'LOSE'}, kda：{player[0]['kills']}/{player[0]['deaths']}/{player[0]['assists']}\n{datetime.datetime.fromtimestamp(info[0]['gameCreation']//1000).strftime('%Y-%m-%d  %H：%M：%S')}",
                actions=[
                    MessageAction(
                        label=' ',
                        text='message1'
                    ),
                ]
            ),
            CarouselColumn(
                thumbnail_image_url=f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{player[1]['championName']}_0.jpg",
                title=player[1]['championName'],
                text=f"{'WIN' if player[1]['win'] else 'LOSE'}, kda：{player[1]['kills']}/{player[1]['deaths']}/{player[1]['assists']}\n{datetime.datetime.fromtimestamp(info[1]['gameCreation']//1000).strftime('%Y-%m-%d  %H：%M：%S')}",
                actions=[
                    MessageAction(
                        label=' ',
                        text='message1'
                    ),
                ]
            ),
            CarouselColumn(
                thumbnail_image_url=f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{player[2]['championName']}_0.jpg",
                title=player[2]['championName'],
                text=f"{'WIN' if player[2]['win'] else 'LOSE'}, kda：{player[2]['kills']}/{player[2]['deaths']}/{player[2]['assists']}\n{datetime.datetime.fromtimestamp(info[2]['gameCreation']//1000).strftime('%Y-%m-%d  %H：%M：%S')}",
                actions=[
                    MessageAction(
                        label=' ',
                        text='message1'
                    ),
                ]
            ),
            CarouselColumn(
                thumbnail_image_url=f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{player[3]['championName']}_0.jpg",
                title=player[3]['championName'],
                text=f"{'WIN' if player[3]['win'] else 'LOSE'}, kda：{player[3]['kills']}/{player[3]['deaths']}/{player[3]['assists']}\n{datetime.datetime.fromtimestamp(info[3]['gameCreation']//1000).strftime('%Y-%m-%d  %H：%M：%S')}",
                actions=[
                    MessageAction(
                        label=' ',
                        text='message1'
                    ),
                ]
            ),
            CarouselColumn(
                thumbnail_image_url=f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{player[4]['championName']}_0.jpg",
                title=player[4]['championName'],
                text=f"{'WIN' if player[4]['win'] else 'LOSE'}, kda：{player[4]['kills']}/{player[4]['deaths']}/{player[4]['assists']}\n{datetime.datetime.fromtimestamp(info[4]['gameCreation']//1000).strftime('%Y-%m-%d  %H：%M：%S')}",
                actions=[
                    MessageAction(
                        label=' ',
                        text='message1'
                    ),
                ]
            ),
            
        ])
    )
    return template_message