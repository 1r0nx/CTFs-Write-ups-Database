# Haybales — Pwny-CTF (script de solve)
from menu import Screen, screen_controller
from utils import draw_text_center
from sao_util import is_sao_attached, read_sao, write_sao, \
    VERSION_ADDR, SENTINEL_ADDR, VERSION_SENTINEL, Version
from pwnymon import Pwnymon
from battle_state import BattleState

class SAOAttachPrompt(Screen):
    def __init__(self):
        super().__init__()
        self.items = []
        self.callback = None

    def draw(self):
        super().draw()
        draw_text_center("Attach SAO", y=14)
        draw_text_center("Contact Helper if", y=34)
        draw_text_center("problem persists", y=44)
        if is_sao_attached():
            screen_controller.pop_screen()
            if self.callback:
                self.callback()

    def open(self, callback = None):
        self.callback = callback
        screen_controller.push_screen(self)
    
    def b(self):
        """
        Back button should only reset you to the primary menu
        """
        screen_controller.pop_to_bottom()

SAO_ATTACH_PROMPT = SAOAttachPrompt()

def sao_fetch_pwnymon():
    try:
        upgrade_sao()
        data = read_sao(0, 16)
        print(data)
        BattleState.my_pwnymon = Pwnymon.from_bytes(data)
        BattleState.my_pwnymon.init()
        print("SAO Pwnymon: ", BattleState.my_pwnymon, BattleState.my_pwnymon.defname)
        return 1

    except OSError:
        SAO_ATTACH_PROMPT.open(sao_fetch_pwnymon)

def sao_commit():
    try:
        data = BattleState.my_pwnymon.to_bytes()
        write_sao(data)
    except OSError:
        SAO_ATTACH_PROMPT.open(sao_fetch_pwnymon)

def upgrade_sao():
    sentinel = int.from_bytes(read_sao(SENTINEL_ADDR, 4), "little")
    if sentinel != VERSION_SENTINEL:
        print("Sentinel not found, upgrading to Basalt")
        # Upgrade to Basalt
        write_sao(VERSION_SENTINEL.to_bytes(4, "little"), SENTINEL_ADDR)
        write_sao(Version.BASALT.to_bytes(4, "little"), VERSION_ADDR)
    
    version = int.from_bytes(read_sao(VERSION_ADDR, 4), "little")
    print("Version: ", version)
    if version not in [Version.BASALT, Version.OBSIDIAN]:
        print("Invalid version, setting to Basalt")
        version = Version.BASALT
    if version == Version.BASALT:
        print("Upgrading to Obsidian")
        # Upgrade to Obsidian
        version = Version.OBSIDIAN
        data = read_sao(0, 4)
        BattleState.my_pwnymon = Pwnymon.from_bytes(data + b'\x00\x00')
        sao_commit()
    
    write_sao(version.to_bytes(4, "little"), VERSION_ADDR)
