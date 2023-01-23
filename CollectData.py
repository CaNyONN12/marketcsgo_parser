import requests
import websockets
import asyncio
import json
from ProcessData import ProcessData
import telebot


class CollectData:
    def __init__(self):
        self.url = self.get_key()

        self.__dm_url = 'https://api.dmarket.com/exchange/v1/market/items?side=market&orderBy=updated&orderDir=desc&title=&priceFrom=2&priceTo=1540&treeFilters=exterior%5B%5D=factory%20new,exterior%5B%5D=minimal%20wear,exterior%5B%5D=field-tested,exterior%5B%5D=well-worn,exterior%5B%5D=battle-scarred,category_1%5B%5D=not_souvenir&gameId=a8db&types=dmarket&cursor=&limit=100&currency=USD'
        self.__raw_guns_info = []

    @staticmethod
    def get_key():
        key = requests.get('https://market.csgo.com/api/v2/get-ws-auth?key=6HJIhgR3sE4i122IPZ62pD95cbk36jq').json().get(
            'wsAuth')
        url = f'wss://wsn.dota2.net/wsn/{key}'
        return url

    @staticmethod
    def open_json(name_file: str) -> dict:
        with open(name_file) as file:
            file_content = file.read()
            content = json.loads(file_content)
        return content

    @staticmethod
    def write_json(name_file, data):

        with open(name_file, 'w') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    @staticmethod
    def __form_new_item_info(item):
        return {
            'i_market_hash_name': item.get('i_market_hash_name'),
            'ui_price': item.get('ui_price'),
            'stickers': item.get('stickers'),
            'ui_id': item.get('ui_id')
        }

    async def collect(self):
        async with websockets.connect(self.url, ping_interval=None) as websocket:
            processor = ProcessData()
            while True:
                await websocket.send("newitems_go")
                item = json.loads(await websocket.recv())['data']
                item = item.encode('ascii').decode('unicode-escape')
                item = json.loads(item)
                items = self.open_json(r'guns_id.json')
                if item.get('stickers') and 'Souvenir' not in item.get('i_market_hash_name') and item.get(
                        'ui_id') not in items:
                    new_item = self.__form_new_item_info(item)
                    items.append(new_item.get('ui_id'))
                    processor.send_to_telegram(new_item)
                    self.write_json(r'guns_id.json', items)
