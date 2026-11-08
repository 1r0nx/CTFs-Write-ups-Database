# Haybales — Pwny-CTF (script de solve)
from menu import Screen, screen_controller
from badgeio import badge
from sao import upgrade_sao, sao_commit
from sao_util import read_sao
from pwnymon import Pwnymon
from battle_state import BattleState
from utils import draw_text_center

class WelcomeScreen(Screen):
    def __init__(self):
        self.pwnyname = ""
        self.welcome_state = 0
        self.cursor_state = False
        self.frame_count = 0
        self.welcome_key_cursor = (0,0)
        self.welcome_text = [
            "Welcome to Fall CTF!",
            "If you have a Pwnymon",
            "insert and press A.",
            "If not, press B to go",
            "to the main menu.",
            "Credits:",
            "Hardware: Sam",
            "Art: Anusha, Pomona",
            "... Tess, Seltzy",
            "Software: Pete, Sam",
            "... Richard, George",
            "... Jake, Emma",
            "... Pomona",
            "Logistics: Anusha",
            "... Sam",
            "Assembly: Sam, Jake",
            "... Minh, Anusha",
            "... Pete, Emma",
            "... Hassam, Julius",
            "... Richard, George",
            "... Kyler, Carlos"
        ]
        self.alphabet = [["Q","W","E","R","T","Y","U","I","O","P"],
                         ["A","S","D","F","G","H","J","K","L","M"],
                         ["Z","X","C","V","B","N"," ","OK!","OK!","OK!"]]

    def on_enter(self):
        self.welcome_state = 0
        self.welcome_scroll = 0
        try:
            f = open('start.txt', 'r')
            f.close()
            screen_controller.pop_screen()
        except OSError:
            pass

    def draw(self):
        if self.welcome_state == 0:
            for i in range(self.welcome_scroll, min(len(self.welcome_text), self.welcome_scroll + 8)):
                badge.display.text(self.welcome_text[i], 0, 9 * (i - self.welcome_scroll))
        else:
            self.frame_count = (self.frame_count + 1) % 30
            if (self.frame_count == 0):
                self.cursor_state = not self.cursor_state
            badge.display.text("Name " + BattleState.my_pwnymon.name, 0, 0)
            badge.display.blit(BattleState.my_pwnymon.sprite,  128-48, 64-48)

            draw_text_center("> " + self.pwnyname + " <", x=40, y=20)
            draw_text_center("QWERTYUIOP",x=40, y=30)
            draw_text_center("ASDFGHJKLM", x=40, y=40)
            draw_text_center("ZXCVBN OK!", x=40, y=50)
            if self.welcome_key_cursor[0] <= 9 and self.welcome_key_cursor[0] >= 7 and self.welcome_key_cursor[1] == 2:
                if self.cursor_state:
                    badge.display.hline(52, 58, 15, 1)
                else:
                    badge.display.rect(52, 50, 15, 9, 1, True)
            else:
                if self.cursor_state:
                    badge.display.hline(10+self.welcome_key_cursor[0]*6,38+self.welcome_key_cursor[1]*10, 5, 1)
                else:
                    badge.display.rect(10+self.welcome_key_cursor[0]*6,30+self.welcome_key_cursor[1]*10, 5, 9, 1, True)
        

    def up(self):
        if self.welcome_state == 0:
            self.welcome_scroll -= 1
            if self.welcome_scroll < 0:
                self.welcome_scroll = 0
        else:
            self.welcome_key_cursor = (self.welcome_key_cursor[0], self.welcome_key_cursor[1] - 1)
            if self.welcome_key_cursor[1] < 0:
                self.welcome_key_cursor = (self.welcome_key_cursor[0], 2)

    def down(self):
        if self.welcome_state == 0:
            self.welcome_scroll += 1
            if self.welcome_scroll > len(self.welcome_text) - 7:
                self.welcome_scroll = len(self.welcome_text) - 7
                if self.welcome_scroll < 0:
                    self.welcome_scroll = 0
        else:
            self.welcome_key_cursor = (self.welcome_key_cursor[0], self.welcome_key_cursor[1] + 1)
            if self.welcome_key_cursor[1] > 2:
                self.welcome_key_cursor = (self.welcome_key_cursor[0], 0)
    def left(self):
        if self.welcome_state == 0:
            pass
        else:
            if (self.welcome_key_cursor[0] == 0 and self.welcome_key_cursor[1] == 2):
                self.welcome_key_cursor = (9, self.welcome_key_cursor[1])
            else:
                self.welcome_key_cursor = (self.welcome_key_cursor[0] - 1, self.welcome_key_cursor[1])
                if self.welcome_key_cursor[0] < 0:
                    self.welcome_key_cursor = (9, self.welcome_key_cursor[1])
                if self.welcome_key_cursor[0] <= 9 and self.welcome_key_cursor[0] >= 7 and self.welcome_key_cursor[1] == 2:
                    self.welcome_key_cursor = (6, self.welcome_key_cursor[1])
    def right(self):
        if self.welcome_state == 0:
            pass
        else:
            if (self.welcome_key_cursor[0] == 6 and self.welcome_key_cursor[1] == 2):
                self.welcome_key_cursor = (7, self.welcome_key_cursor[1])
            else:
                self.welcome_key_cursor = (self.welcome_key_cursor[0] + 1, self.welcome_key_cursor[1])
                if self.welcome_key_cursor[0] > 9:
                    self.welcome_key_cursor = (0, self.welcome_key_cursor[1])
                if self.welcome_key_cursor[0] <= 9 and self.welcome_key_cursor[0] >= 7  and self.welcome_key_cursor[1] == 2:
                    self.welcome_key_cursor = (0, self.welcome_key_cursor[1])        
    
    def a(self):
        if self.welcome_state == 0:
            try:
                upgrade_sao()
                data = read_sao(0, 6)
                BattleState.my_pwnymon = Pwnymon.from_bytes(data)
                print("SAO Pwnymon: ", BattleState.my_pwnymon)
                self.welcome_state = 1
                # screen_controller.pop_screen()
            except:
                pass
        else:
            addchr = self.alphabet[self.welcome_key_cursor[1]][self.welcome_key_cursor[0]]
            if addchr == "OK!":
                BattleState.my_pwnymon.defname = self.pwnyname
                sao_commit()
                screen_controller.pop_screen()
            else:
                if len(self.pwnyname) < 10:
                    self.pwnyname += addchr


    def b(self):
        if self.welcome_state == 0:
            screen_controller.pop_screen()
        else:
            if len(self.pwnyname) > 0:
                self.pwnyname = self.pwnyname[:-1]
        
    def on_leave(self):
        open('start.txt', 'w').write('1')

