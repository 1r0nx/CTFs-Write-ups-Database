# from menu import TableMenu
from menu import Screen
from badgeio import badge
from sao import sao_fetch_pwnymon
from battle_state import BattleState

class StatsMenu(Screen):
    def __init__(self):
        super().__init__()
    def on_enter(self):
        super().__init__()
        sao_fetch_pwnymon()
    def draw(self):
        # Draw the pwnymon sprite on the right side. Don't used flipped sprites.
        badge.display.blit(BattleState.my_pwnymon.sprite, 128-48, 8)
        # Uppercase the pwnymon's name and draw
        if len(BattleState.my_pwnymon.defname) > 0:
            badge.display.text(BattleState.my_pwnymon.defname[0].upper() + BattleState.my_pwnymon.defname[1:].lower(), 0, 0)
        else:
            badge.display.text(BattleState.my_pwnymon.name[0].upper() + BattleState.my_pwnymon.name[1:], 0, 0)
        # Draw the stats
        badge.display.text(f"HP: {BattleState.my_pwnymon.stat_hp}", 0, 10)
        badge.display.text(f"ATK: {BattleState.my_pwnymon.stat_attack}", 0, 20)
        badge.display.text(f"SPD: {BattleState.my_pwnymon.stat_speed}", 0, 30)
        badge.display.text(f"LV: {BattleState.my_pwnymon.exp//100}", 0, 40)
        badge.display.text(f"XP:", 0, 50)
        # Draw the XP bar as a middling bar
        badge.display.hline(20, 53, (BattleState.my_pwnymon.exp % 100)//2, 1)
        # Draw the XP outline to give distinguishing features
        badge.display.hline(18, 56, 51, 1)
        badge.display.hline(18, 57, 50, 1)
        badge.display.line(67, 56, 71, 52, 1)
        badge.display.line(68, 56, 72, 52, 1)
