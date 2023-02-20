# The MIT License (MIT)
# 
# Copyright (c) 2022-2023 Péter Tombor.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from datetime import datetime
import json, requests, re
from bs4.element import Tag
from bs4 import BeautifulSoup
from functools import cached_property

class ItchGame:
    def __init__(self, div: Tag):
        self.id = div.attrs['data-game_id']
        a = div.find('a', class_='title game_link')
        self.name = a.text
        self.url = a.attrs['href']

        self.cover_image = div.find('div', class_='game_thumb').find('img').attrs['data-lazy_src']

        price_element = div.find('div', attrs={'class': 'price_value'})
        # Some elements don't have a price defined
        if price_element != None:
            price_str = re.findall("[-+]?(?:\d*\.\d+|\d+)", price_element.text)[0]
            self.price = float(price_str)
        else:
            self.price = -1
            return

        #self.sale_percent (sometimes it's 50%, sometimes it's "In bundle")

    @cached_property
    def claimable(self) -> bool:
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, 'html.parser')
        buy_row = soup.find('div', class_='buy_row')
        if buy_row is None:
            # Game is probably WebGL or HTML5 only
            return False
        buy_box = buy_row.find('a', class_='button buy_btn')
        claimable = buy_box.text == 'Download or claim'
        return claimable

    @cached_property
    def sale_end(self) -> datetime:
        r = requests.get(self.url + '/data.json')
        resp = json.loads(r.text)
        date_str = resp['sale']['end_date']
        date_format = '%Y-%m-%d %H:%M:%S'
        return datetime.strptime(date_str, date_format)

    @staticmethod
    def get_sale_page(page: int):
        r = requests.get(f"https://itch.io/games/on-sale?page={page}&format=json")
        html = json.loads(r.text)['content']
        soup = BeautifulSoup(html, 'html.parser')
        games_raw = soup.find_all('div', class_="game_cell")
        games = []
        for div in games_raw:
            game_parsed = ItchGame(div)
            if game_parsed.price == 0:
                games.append(game_parsed)
        if len(games) == 0 and json.loads(r.text)["num_items"] == 0:
            return False
        return games

    @staticmethod
    def get_all_sales():
        pass
