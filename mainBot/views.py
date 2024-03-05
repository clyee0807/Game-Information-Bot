from django.shortcuts import render

# Create your views here.
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, StickerSendMessage, ImageSendMessage
from linebot.models import PostbackEvent, AudioSendMessage, FlexSendMessage

import os, re
import json
import requests
from pathlib import Path
# from openai import OpenAI

from mainBot.api.summoner import get_summoner_info, analyze_summoner
from mainBot.api.champion import get_champion_info, hero_name_to_id
from mainBot.api.matches import getFiveMatches
from mainBot.template.gameCarousel import createGameCarousel

image_folder = 'static'
domain = '285a-114-37-4-118.ngrok-free.app'
OPENAI_API_KEY = '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'

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # D:\CLY\CLYEE\projects\linebot_test\mainBot

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

# searching_summoner, searching_champion, analyzing_summoner, askAI
user_state = None

@csrf_exempt
def callback(request):
    global user_state
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):
                if(event.message.type == 'text'):
                    mtext = event.message.text  # user's input
                    uid = event.source.user_id
                    print(f'input: {mtext}')
                    
                    message = []
                    if user_state == 'searching_summoner':   # 查詢召喚師資料
                        print(f'searching for {mtext}')
                        user_state = None
                        summoner_name, level, proId, puuid = get_summoner_info(mtext)
                        print(f'summoner_name: {summoner_name}, level: {level}')
                        with open(os.path.join(BASE_DIR, 'template', 'summoner_flex.json'), 'r', encoding='utf-8') as file:
                            content = json.load(file)
                        content['body']['contents'][0]['text'] = summoner_name
                        content['body']['contents'][1]['contents'][1]['contents'][1]['text'] = str(level)
                        content['hero']['url'] = f'https://ddragon.leagueoflegends.com/cdn/14.4.1/img/profileicon/{proId}.png'
                        content['footer']['contents'][0]['action']['data'] = f'puuid={puuid}?name={summoner_name}'

                        message.append(FlexSendMessage(alt_text='flex_summoner', contents=content))
                    elif user_state == 'searching_champion':  # 查詢英雄資料
                        user_state = None
                        # champion, title, disc = get_champion_info(mtext)
                        with open(os.path.join(BASE_DIR, 'champion.json'), 'r', encoding='utf-8') as file:
                            data = json.load(file)
                        champion = hero_name_to_id[mtext]
                        title = data['data'][champion]['title']
                        type = data['data'][champion]['tags'][0]
                        desc = data['data'][champion]['blurb']
                        life = str(data['data'][champion]['stats']['hp'])
                        mana = str(data['data'][champion]['stats']['mp'])
                        moveSpeed = str(data['data'][champion]['stats']['movespeed'])
                        attack = str(data['data'][champion]['stats']['attackdamage'])

                        with open(os.path.join(BASE_DIR, 'template', 'champion_flex.json'), 'r', encoding='utf-8') as file:
                            content = json.load(file)
                        content['body']['contents'][0]['contents'][0]['contents'][0]['text'] = champion
                        content['body']['contents'][0]['contents'][0]['contents'][1]['text'] = title
                        content['body']['contents'][0]['contents'][1]['text'] = type
                        content['body']['contents'][1]['contents'][0]['contents'][0]['text'] = desc
                        content['body']['contents'][1]['contents'][1]['contents'][1]['text'] = life
                        content['body']['contents'][1]['contents'][2]['contents'][1]['text'] = mana
                        content['body']['contents'][1]['contents'][3]['contents'][1]['text'] = moveSpeed
                        content['body']['contents'][1]['contents'][4]['contents'][1]['text'] = attack
                        content['hero']['url'] = f'https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champion}_0.jpg'
                        message.append(FlexSendMessage(alt_text='flex_champion', contents=content))
                        # message.append(TextSendMessage(text=f'英雄名稱: {champion}\n英雄稱號: {title}\n英雄類型: {desc}'))
                    elif user_state == 'analyzing_summoner':  # 分析召喚師
                        user_state = None
                        importance, correlation_with_win = analyze_summoner(mtext)
                        message.append(TextSendMessage(text=f"在分析 {mtext} 過去100場的遊戲中，我們獲得以下資訊：\n \
                                                        擊殺數對勝率的影響程度: {importance[0]: .3f}\n \
                                                        死亡數對勝率的影響程度: {importance[1]: .3f}\n \
                                                        助攻數對勝率的影響程度: {importance[2]: .3f}\n \
                                                        賺取金錢對勝率的影響程度: {importance[3]: .3f}\n \
                                                        總傷害輸出對勝率的影響程度: {importance[4]: .3f}\n \
                                                        總承受傷害對勝率的影響程度: {importance[5]: .3f}\n \
                                                        遊戲時間對勝率的影響程度: {importance[6]: .3f}\n \
                                                        對建築物造成的傷害對勝率的影響程度: {importance[7]: .3f}\n\n \
                                                        除此之外，我們並分析了以下因素對於勝率的相關性：\n \
                                                        擊殺數與勝率的相關性: {correlation_with_win[0]: .3f}\n \
                                                        死亡數與勝率的相關性: {correlation_with_win[1]: .3f}\n \
                                                        助攻數與勝率的相關性: {correlation_with_win[2]: .3f}\n \
                                                        賺取金錢與勝率的相關性: {correlation_with_win[3]: .3f}\n \
                                                        總傷害輸出與勝率的相關性: {correlation_with_win[4]: .3f}\n \
                                                        總承受傷害與勝率的相關性: {correlation_with_win[5]: .3f}\n \
                                                        遊戲時間與勝率的相關性: {correlation_with_win[6]: .3f}\n \
                                                        對建築物造成的傷害與勝率的相關性: {correlation_with_win[7]: .3f}\n \
                                                    "))
                    else:
                        user_state = None
                        if(mtext == 'sticker'):
                            message.append(StickerSendMessage(sticker_id=11825377, package_id=6632)) 
                        elif(mtext == 'image'):
                            message.append(ImageSendMessage(original_content_url='https://i.imgur.com/btADJow.png', preview_image_url='https://i.imgur.com/btADJow.png'))
                        elif(mtext == '查詢使用者資料'):
                            user_state = 'searching_summoner'
                            message.append(TextSendMessage(text="請輸入召喚師名稱:"))
                        elif(mtext == '查看英雄資料'):
                            user_state = 'searching_champion'
                            message.append(TextSendMessage(text="請輸入英雄名稱:"))
                        elif(mtext == '分析召喚師'):
                            user_state = 'analyzing_summoner'
                            message.append(TextSendMessage(text="請輸入欲分析召喚師名稱:"))
                        else:
                            message.append(TextSendMessage(text=mtext))
                    
                    # reply message
                    line_bot_api.reply_message(event.reply_token, message)
            
            elif isinstance(event, PostbackEvent):  # 處理 PostbackEvent
                data = event.postback.data
                print(f'postback data: {data}')
                if(data[:5] == 'puuid'):  # 查看對戰紀錄
                    puuid = data[6:].split('?')[0]
                    summoner_name = data.split('?')[1][5:]
                    matchIds = getFiveMatches(puuid)     
                    line_bot_api.reply_message(event.reply_token, createGameCarousel(summoner_name, matchIds))           
                else:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Received postback : ' + data))
            
        return HttpResponse()
    else:
        return HttpResponseBadRequest()


