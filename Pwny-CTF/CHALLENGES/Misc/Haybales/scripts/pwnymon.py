# Haybales — Pwny-CTF (script de solve)
import random
from utils import pbm_to_fbuf, flip_framebuffer

class Type:
    Rizz = 0
    Magic = 1
    Physical = 2
    NoType = 3

class PwnymonID:
    rustabone = 0
    purrtegeist = 1
    snakepwny =  2
    missingno = 3

    metadata = {
        rustabone: {
            "name": "rustabone",
            "type": Type.Physical
        },
        purrtegeist: {
            "name": "purrtegeist",
            "type": Type.Rizz
        },
        snakepwny: {
            "name": "snakepwny",
            "type": Type.Magic
        }
    }

def type_advantage(type1, type2):
    if type1 == type2:
        return 0
    
    beats = [
        (Type.Rizz, Type.Magic),
        (Type.Magic, Type.Physical),
        (Type.Physical, Type.Magic)
    ]

    if (type1, type2) in beats:
        return 1
    else:
        return -1

class MoveKind:
    Attack = 0
    Defend = 1
    Heal = 2

class Move:
    
    def __init__(self, id, name, type, kind, damage=0, heal=0, defense=0, pp=2):
        self.id = id
        self.name = name
        self.type = type
        self.kind = kind
        self.damage = damage
        self.heal = heal
        self.defense = defense
        self.max_pp = pp
        self.pp = pp

    def __str__(self):
        return f"{self.name} ({self.type})"
    
    def __repr__(self):
        return f"{self.name} ({self.type})"
    
class Pwnymon:
    id = 0
    stat_hp = 0
    stat_attack = 0
    stat_speed = 0
    stat_crit_chance = 0
    defname = ""
    exp = 0

    hp = 0

    def __init__(self, id=PwnymonID.missingno, stat_hp=0, stat_attack=0, stat_speed=0, exp=0, defname=""):
        self.id = id
        self.stat_hp = stat_hp
        self.stat_attack = stat_attack
        self.stat_speed = stat_speed
        self.defname = defname
        self.exp = exp
        self.sprites = {
            PwnymonID.rustabone: pbm_to_fbuf('sprites/rust_crab.pbm'),
            PwnymonID.purrtegeist: pbm_to_fbuf('sprites/scratch_cat.pbm'),
            PwnymonID.snakepwny: pbm_to_fbuf('sprites/python_snake.pbm')
        }
        self.flipped_sprites = {
            PwnymonID.rustabone: pbm_to_fbuf('sprites/rust_crab.pbm'),
            PwnymonID.purrtegeist: pbm_to_fbuf('sprites/scratch_cat.pbm'),
            PwnymonID.snakepwny: pbm_to_fbuf('sprites/python_snake.pbm')
        }
        for _, fbuf in self.flipped_sprites.items():
            flip_framebuffer(fbuf)
    
    def init(self):
        self.hp = self.stat_hp

    def __str__(self):
        return f"{self.name} ({self.id})"

    def dump(self):
        return f"{self.name=} {self.hp=} {self.exp=} {self.stat_hp=} {self.stat_attack=} {self.stat_speed=}"
    
    def __repr__(self):
        return f"{self.name} ({self.id})"
    
    def reset(self):
        self.hp = self.stat_hp

    def max_heal(self):
        self.hp = self.stat_hp
    
    def to_bytes(self):
        bytname = self.defname.encode("utf-8")
        bytname = bytname + b"\x00" * (10 - len(bytname))
        return bytes([self.id, self.stat_hp, self.stat_attack, self.stat_speed]) + self.exp.to_bytes(2, "little") + bytname
    
    @property
    def sprite(self):
        return self.sprites[self.id]

    @property
    def flipped_sprite(self):
        return self.flipped_sprites[self.id]
    
    @staticmethod
    def from_bytes(b):
        assert len(b) >= 6
        if (len(b) == 16):
            user_name = ""
            try:
                user_name = b[6:].decode("utf-8").strip()
            except:
                pass
            return Pwnymon(b[0], b[1], b[2], b[3], int.from_bytes(b[4:6], "little"), user_name)
        else:
            return Pwnymon(b[0], b[1], b[2], b[3], int.from_bytes(b[4:6], "little"))
    def get_move_by_id(self, move_id):
        # This is a little gross, but I am lazy
        move = next(filter(lambda m: m.id == move_id, self.moveset))
        return move

    @property
    def moveset(self):

        # The move 'id' is the index of the move in the moveset
        moveset = {
            PwnymonID.rustabone: [
                Move(0, "Crab - Physical Attack", Type.Physical, MoveKind.Attack, damage=5),
                Move(1, "Crab - Rizz Attack", Type.Rizz, MoveKind.Attack, damage=5),
                Move(2, "Crab - Magic Attack", Type.Magic, MoveKind.Attack, damage=5),
                Move(3, "Crab - Heal", Type.NoType, MoveKind.Heal, heal=5),
                Move(4, "Crab - Defend", Type.NoType, MoveKind.Defend, defense=5),
            ],
            PwnymonID.purrtegeist: [
                Move(0, "Cat - Physical Attack", Type.Physical, MoveKind.Attack, damage=5),
                Move(1, "Cat - Rizz Attack", Type.Rizz, MoveKind.Attack, damage=5),
                Move(2, "Cat - Magic Attack", Type.Magic, MoveKind.Attack, damage=5),
                Move(3, "Cat - Heal", Type.NoType, MoveKind.Heal, heal=5),
                Move(4, "Cat - Defend", Type.NoType, MoveKind.Defend, defense=5),
            ],
            PwnymonID.snakepwny: [
                Move(0, "Snake - Physical Attack", Type.Physical, MoveKind.Attack, damage=5),
                Move(1, "Snake - Rizz Attack", Type.Rizz, MoveKind.Attack, damage=5),
                Move(2, "Snake - Magic Attack", Type.Magic, MoveKind.Attack, damage=5),
                Move(3, "Snake - Heal", Type.NoType, MoveKind.Heal, heal=5),
                Move(4, "Snake - Defend", Type.NoType, MoveKind.Defend, defense=5),
            ],
        }

        return moveset[self.id]

    @property
    def metadata(self):
        return PwnymonID.metadata[self.id]

    @property
    def name(self):
        return self.metadata["name"]
    
    @property
    def type(self):
        return self.metadata["type"]

    @property
    def is_alive(self):
        return self.hp > 0

class StatID:
    pwnymon_id = 0
    hp = 1
    attack = 2
    speed = 3

    attr_lookup = {
        0: "id",
        1: "stat_hp",
        2: "stat_attack",
        3: "stat_speed"
    }


def build_initial_pwnymon(pwnymon_id, pp_points=8):
    base_stats = {
        PwnymonID.rustabone: {
            StatID.hp: 10,
            StatID.attack: 5,
            StatID.speed: 5
        },
        PwnymonID.purrtegeist: {
            StatID.hp: 7,
            StatID.attack: 3,
            StatID.speed: 10
        },
        PwnymonID.snakepwny: {
            StatID.hp: 4,
            StatID.attack: 10,
            StatID.speed: 6
        }
    }

    stats = base_stats[pwnymon_id]

    for _ in range(pp_points):
        stat_to_improve = random.choice(list(stats.keys()))
        stats[stat_to_improve] += 1
    
    stats[StatID.pwnymon_id] = pwnymon_id

    return Pwnymon(**{
        StatID.attr_lookup[x]: y for x, y in stats.items()
    })

def test():
    # We would read from a stored file to create a Pwnymon object, but we'll just create one here.
    pass

if __name__ == "__main__":
    test()
