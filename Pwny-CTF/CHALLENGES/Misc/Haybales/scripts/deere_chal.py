# Haybales — Pwny-CTF (script de solve)
from menu import Screen
from badgeio import badge
from utils import pbm_to_fbuf
from rp2 import asm_pio, StateMachine
import random
import hashlib

@asm_pio(autopull=True, autopush=True)
def simple_pio():
    wrap_target()
    out(x, 1)
    out(y, 3)
    jmp(not_x, "skip")
    jmp(y_dec, "skip")
    label("skip")
    mov(y, invert(y))
    in_(y, 3)
    in_(x, 1)
    wrap()


# states for start screen, game, and end screen
class DeereState:
    START = 0
    RULES = 1
    GAME = 2
    LEVEL_UP = 3
    LOSE = 4
    WIN = 9

class DeereChalScreen(Screen):
    def __init__(self):
        self.tractors = [
            pbm_to_fbuf('sprites/tractor0.pbm'),
            pbm_to_fbuf('sprites/tractor1.pbm'),
            pbm_to_fbuf('sprites/tractor2.pbm'),
            pbm_to_fbuf('sprites/tractor3.pbm'),
        ]
        self.haybale = pbm_to_fbuf('sprites/haybale.pbm')
        self.john_deere_logo = pbm_to_fbuf('sprites/john_deere_logo.pbm')
        self.exit_data = None

    def on_enter(self):
        self.state = DeereState.START

        self.haybales = []

        self.ticks = 0

        self.tractor_y = 30
        self.num_haybales = 0
        self.missed = 0
        self.level = 0

        # integer multiplier for haybale movement rate
        self.speed = 0
        # likelihood of haybale spawning per frame
        self.spawn_rate = 0.03
        # number of moved pixels since last haybale spawn
        self.last_haybale = 0

        self.key_history_size = 32
        self.keys = 0

        self.rules_scroll = 0
        self.rules_text = [
            'Rules:',
            '1. Move the tractor',
            '   with up and down',
            '   buttons.',
            '2. Collect haybales',
            '3. Miss three',
            '   haybales and you',
            '   lose!',
            '',
            'There are two flags',
            'to find! Connect the',
            'board to your com-',
            'puter to find them.',
            '',
            'Challenge and art',
            'made by Richard'
            '',
            'Press [A] to continue',
        ]

        self.sm = StateMachine(0, simple_pio)

    def draw(self):
        if self.state == DeereState.START:
            self.draw_start()
        elif self.state == DeereState.GAME:
            self.draw_game()
        elif self.state == DeereState.RULES:
            self.draw_rules()
        elif self.state == DeereState.LOSE:
            self.draw_lose()
        elif self.state == DeereState.WIN:
            self.draw_win()

    def draw_start(self):
        badge.display.blit(self.john_deere_logo, 0, 20)
        badge.display.text('This challenge is', 0, 0)
        badge.display.text('sponsored by', 0, 10)
        badge.display.text('Press [A] to continue', 0, 54)

    def draw_rules(self):
        for i in range(self.rules_scroll, min(len(self.rules_text), self.rules_scroll + 8)):
            badge.display.text(self.rules_text[i], 0, 9 * (i - self.rules_scroll))

    def draw_game(self):
        self.ticks += 1

        # level up every 2^level * 10 haybales
        if self.num_haybales >= (1 << self.level) * 10:
            self.level += 1
            self.speed += 1
            self.spawn_rate += 0.01

        # spawn haybales
        if self.last_haybale > 15 and random.random() < self.spawn_rate:
            self.haybales.append((140, random.randint(0, 34)))
            self.last_haybale = 0

        # move haybales
        movement = self.speed
        # for speed=0, only move when ticks lsb = 0
        if self.speed == 0:
            movement = self.ticks & 1
        for i in range(len(self.haybales)):
            self.haybales[i] = (self.haybales[i][0] - movement, self.haybales[i][1])
        self.last_haybale += movement

        remove_haybales = []
        # check for collisions and missed haybales, and draw haybales
        for i, (xpos, ypos) in enumerate(self.haybales):
            if xpos > -16 and xpos < 120:
                badge.display.blit(self.haybale, xpos, ypos, 0)
                # check for collision
                if abs(xpos) < 10 and abs(ypos - self.tractor_y) < 16:
                    self.num_haybales += 1
                    remove_haybales.append(i)
            elif xpos < -16:
                remove_haybales.append(i)
                self.missed += 1
        for i in remove_haybales[::-1]:
            self.haybales.pop(i)

        # don't try to check flag too often
        if self.ticks & 0x1f == 0:
            if self.decode_flag() is not None:
                self.state = DeereState.WIN

        # check for loss
        if self.missed >= 3:
            self.state = DeereState.LOSE

        # draw tractor
        current_tractor = self.tractors[(self.ticks >> 3) & 3]
        badge.display.blit(current_tractor, 0, self.tractor_y, 0)

        # draw status bar
        badge.display.rect(0, 50, 128, 14, 1, 1)

        got = self.num_haybales
        missed = self.missed
        level = self.level + 1
        badge.display.text(f'L{level} Hay:{got:<3d} Missed:{missed}', 4, 54, 0)

    def draw_lose(self):
        badge.display.text(f'You lost! Score: {self.num_haybales}', 0, 0)
        badge.display.text(f'          Level: {self.level}', 0, 10)
        high_score = self.get_high_score()
        if self.num_haybales > high_score:
            high_score = self.num_haybales
            self.set_high_score(high_score)
        badge.display.text(f'== High Score:{high_score:4d} ==', 0, 30)
        badge.display.text('[A]:Restart [B]:Exit', 0, 54)

    def get_high_score(self):
        try:
            return int(open('high_score.txt', 'r').read())
        except:
            return 0

    def set_high_score(self, score):
        open('high_score.txt', 'w').write(str(score))

    def draw_win(self):
        if self.state != DeereState.WIN and self.decode_flag() is None:
            self.state = DeereState.GAME
            return

        num, flag = self.decode_flag()
        badge.display.text(f'You win chal {num}! Flag:', 0, 0)
        badge.display.text(flag[:21], 0, 10)
        if len(flag) > 21:
            badge.display.text(flag[21:], 0, 20)

    def right(self):
        self.next_page()

    def left(self):
        pass

    def up(self):
        if self.state == DeereState.GAME:
            self.move_tractor(0)
        elif self.state == DeereState.RULES:
            self.rules_scroll -= 1
            if self.rules_scroll < 0:
                self.rules_scroll = 0

    def down(self):
        if self.state == DeereState.GAME:
            self.move_tractor(1)
        elif self.state == DeereState.RULES:
            self.rules_scroll += 1
            if self.rules_scroll > len(self.rules_text) - 7:
                self.rules_scroll = len(self.rules_text) - 7
                if self.rules_scroll < 0:
                    self.rules_scroll = 0

    # dir is 0 for up, 1 for down
    def move_tractor(self, dir):
        move = -1 if dir == 0 else 1
        self.tractor_y += 5 * move
        if self.tractor_y > 34:
            self.tractor_y = 34
        elif self.tractor_y < 0:
            self.tractor_y = 0
        self.keys = (self.keys << 1) | (~dir & 1)
        self.keys &= (1 << self.key_history_size) - 1

    def a(self):
        self.next_page()

    def next_page(self):
        if self.state == DeereState.START:
            self.state = DeereState.RULES
        elif self.state == DeereState.RULES:
            self.state = DeereState.GAME
        elif self.state == DeereState.LOSE or self.state == DeereState.WIN:
            self.state = DeereState.START
            self.on_enter()

    def pio_mix(self, num):
        self.sm.restart()
        self.sm.active(1)
        self.sm.put(num & 0xffffffff)
        res = self.sm.get() & 0xffffffff
        self.sm.active(0)
        return res

    def decode_flag(self):
        key = self.keys
        if key == 0xdcd8be1:
            # easy flag
            encoded = [2108351122, 1991566742, 2142157452, 984939473, 1386462089, 1855125712, 1889658065]
            flag = ''.join([int.to_bytes(encoded[i] ^ key, 4, 'little').decode() for i in range(len(encoded))])
            return (1, flag)
        elif self.pio_mix(key) == 0x122c5bf4:
            # hard flag
            key = int.to_bytes(key, 4, 'little')
            hashed = hashlib.sha256(key).digest()
            encoded = bytes.fromhex('9ca16ac0128e729ef5b55a9d6f9f7ffff5f97a48f508db908a86f7')
            decoded = bytes([a ^ b for a, b in zip(hashed, encoded)])
            return (2, decoded.decode())
        else:
            return None
