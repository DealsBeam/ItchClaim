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

import os
from fire import Fire
from ItchUser import ItchUser
import DiskManager

class ItchClaim:
    def __init__(self,
                login: str = None,
                password: str = None,
                totp: str = None):
        if login is not None:
            self.user = ItchClaim._login(login, password, totp)
        else:
            self.user = None

    def refresh_sale_cache(object, clean: bool = False):
        DiskManager.remove_expired_sales()
        print('Downloading game sales pages.')
        i = 1
        more_games_exist = True
        while more_games_exist:
            page = DiskManager.get_online_sale_page(i)
            if page == False:
                break
            for game in page:
                if os.path.exists(game.get_default_game_filename()) and not clean:
                    more_games_exist = False
                    print(f'Game {game.name} has already been saved. Stopping execution')
                    break
                game.save_to_disk()
            print(f'Sale page #{i+1}: added {len(page)} games')
            i += 1

    def refresh_library(self):
        if self.user is None:
            print('You must be logged in')
            return
        self.user.reload_owned_games()
        self.user.save_session()

    def claim(self):
        if self.user is None:
            print('You must be logged in')
            return
        for game in DiskManager.load_all_games():
            if not self.user.owns_game(game) and game.claimable:
                self.user.claim_game(game)
                self.user.save_session()

    def _login(login: str = None,
               password: str = None,
               totp: str = None) -> ItchUser:
        user = ItchUser(login)
        try:
            user.load_session()
            print(f'Session {login} loaded successfully')
        except:
            user.login(password, totp)
            print(f'Logged in as {login}')
        return user

if __name__=="__main__":
    Fire(ItchClaim)