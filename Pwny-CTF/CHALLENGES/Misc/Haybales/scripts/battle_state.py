# Haybales — Pwny-CTF (script de solve)
from pwnymon import Pwnymon

class BattleState:
    opponent_pwnymon = Pwnymon()
    opponent_move = None
    my_move = None
    my_pwnymon = None
    started_battle = False
    did_win = False
