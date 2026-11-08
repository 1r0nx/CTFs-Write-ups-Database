# Haybales — Pwny-CTF (script de solve)
import time
from badgeio import badge

VERSION_SENTINEL = 0x1337c0de

SENTINEL_ADDR = 0xf0
VERSION_ADDR = 0xf4

class Version:
    # 4 byte pwnymon (whats preflashed rn)
    # (technically not a version bc sentinel not included)
    BASALT = 0
    # 6 byte pwnymon (add experience)
    OBSIDIAN = 1

pending_op = None

def write_sao(data, addr=0x0):
    # default addressing 8-bit
    assert addr + len(data) <= 0x100
    badge.sao.writeto_mem(80, addr, data)
    # need to wait after writing before reading!
    time.sleep(0.2)

def read_sao(addr, n_bytes=4):
    # default addressing 8-bit
    assert addr + n_bytes <= 0x100
    return badge.sao.readfrom_mem(80, addr, n_bytes)

def is_sao_attached():
    try:
        badge.sao.writeto(80, b'')
        return True
    except OSError:
        return False