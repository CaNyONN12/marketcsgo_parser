import json
from collections import Counter
from list_conditions import list_conditions


class ProcessData:
    @staticmethod
    def read_json(name_file: str):
        with open(name_file) as file:
            file_content = file.read()
            content = json.loads(file_content)
        return content

    @staticmethod
    def write_json(name_file, data):
        with open(name_file, 'w') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    def __init__(self):
        self.steam_price_stickers = self.read_json('steam_price_stickers.json')
        self.steam_price_guns = self.read_json('steam_price_guns.json')
        self.stickers_id = self.read_json('stickers_id.json')
        self.list_conditions = list_conditions
        self.dollar_to_ruble = 70

    # Convert string of stickers id to list of named stickers.
    # Example: "4504557993|45032722"4504557993|4503272214|2244557015|2244557015"14|2244557015|2244557015"
    def get_stickers_name(self, string: str) -> list:
        if string is None:
            return []

        item_stickers_id = string.split('|')
        stickers_name = []
        for sticker_id in item_stickers_id:
            sticker_name = self.stickers_id.get(sticker_id)
            if sticker_name is not None:
                sticker_name = sticker_name.replace('Наклейка: ', '')
                stickers_name.append(sticker_name)
        return stickers_name

    def get_total_price_stickers(self, gun_info: dict) -> int:
        stickers = self.get_stickers_name(gun_info.get('stickers'))
        total_price = 0
        for sticker in stickers:
            if self.steam_price_stickers.get(f'Наклейка | {sticker}') is not None:
                total_price += self.steam_price_stickers.get(f'Наклейка | {sticker}')
            elif self.steam_price_stickers.get(f'Sticker | {sticker}') is not None:
                total_price += self.steam_price_stickers.get(f'Sticker | {sticker}')
            elif self.steam_price_stickers.get(f'{sticker}') is not None:
                total_price += self.steam_price_stickers.get(f'{sticker}')
        return total_price

    # Create a dictionary to send a message to telegram
    def build_item_body(self, item):
        name = item.get('i_market_hash_name')
        stickers = self.get_stickers_name(item.get('stickers'))
        price_stickers = self.get_total_price_stickers(item)
        count_same_stickers = max(Counter(stickers).values()) if stickers != [] else 0
        self_price = round((item.get('ui_price')) / self.dollar_to_ruble, 2)
        steam_price = round(self.steam_price_guns.get(name), 2) if self.steam_price_guns.get(
            name) is not None else self_price
        ui_id = item.get('ui_id')

        return {'name': name, 'stickers': stickers, 'price_stickers': price_stickers,
                'count_same_stickers': count_same_stickers, 'self_price': self_price,
                'steam_price': steam_price, 'ui_id': ui_id
                }

    # Check conditions
    @staticmethod
    def verify_conditions(list_conditions_: list, checked_obj: dict) -> bool:
        for dict_condition in list_conditions_:
            if all([checked_obj['count_same_stickers'] == dict_condition['count_same_stickers'],
                    checked_obj['price_stickers'] >= dict_condition['price_stickers'],
                    checked_obj['self_price'] < checked_obj['steam_price'] * 1.3,
                    checked_obj['self_price'] < dict_condition['self_price']
                    ]):
                return True
        return False

    @staticmethod
    def form_telegram_message(item: dict) -> str:
        name = item.get('name')
        stickers = item.get('stickers')
        price_stickers = item.get('price_stickers')
        count_same_stickers = item.get('count_same_stickers')
        self_price = item.get('self_price')
        steam_price = item.get('steam_price')
        ui_id = item.get('ui_id')
        return f'#{count_same_stickers} \n {name} \n Цена оружия: {self_price}$ \n цена оружия в стиме: {steam_price} \n \n Стикеры: {stickers} \n \n Общая цена стикеров: {price_stickers}$ \n\n id - {ui_id}'

    def send_to_telegram(self, gun_info):
        gun_info = self.build_item_body(gun_info)
        if self.verify_conditions(self.list_conditions, gun_info):
            print(self.form_telegram_message(gun_info))
