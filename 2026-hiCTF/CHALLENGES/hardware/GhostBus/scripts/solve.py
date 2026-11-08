#!/usr/bin/env python3
# GhostBus — déchiffrement du record scellé en émulant le firmware MCU (Unicorn).
# Nonce lu sur le bus UART (cmd 0x10), clé = SHA256(CONST24 ‖ nonce), AES-256 du firmware.
# Usage : python3 solve.py   (depuis ce dossier work/, avec extract/ à côté)
import os
from unicorn import *
from unicorn.arm_const import *

HERE = os.path.dirname(os.path.abspath(__file__))
FLASH_IMG = os.path.join(HERE, "extract", "flash_dump.bin")
flash = open(FLASH_IMG, "rb").read()

FLASH = 0x08000000                       # firmware lié ici (image flash = telle quelle)
mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
mu.mem_map(FLASH, 0x80000); mu.mem_write(FLASH, flash[:0x80000])
RAM = 0x20000000; mu.mem_map(RAM, 0x40000)
mu.mem_map(0, 0x1000)                     # page d'atterrissage pour le retour (LR=1)
STACK = RAM + 0x30000

def call(addr, r0=0, r1=0, r2=0, r3=0):
    mu.reg_write(UC_ARM_REG_SP, STACK)
    for r, v in [(UC_ARM_REG_R0, r0), (UC_ARM_REG_R1, r1),
                 (UC_ARM_REG_R2, r2), (UC_ARM_REG_R3, r3)]:
        mu.reg_write(r, v)
    mu.reg_write(UC_ARM_REG_LR, 1)        # retourne à 0 (adresse paire -> stop)
    mu.emu_start(addr | 1, 0, 0, 0)       # |1 = mode Thumb

# --- entrées ---
const24 = bytes.fromhex("04325a9c117f3da0c0ffee5aa55a00ff1234567890abcdef")  # .rodata @0x8000ca0
nonce   = bytes.fromhex("9e3b7a44c1d05f82a6e1b4907cd3f5a2")                  # nonce UART (cmd 0x10)
ct      = flash[0x6A000:0x6A030]                                            # sealed v2, 48 o

# --- tampons bien séparés et zéro-initialisés ---
SHA, CONST, NONCE, KEY, AESCTX, BUF = (RAM+0x1000, RAM+0x2000, RAM+0x3000,
                                       RAM+0x4000, RAM+0x5000, RAM+0x8000)
for base, sz in [(SHA,0x400),(CONST,0x100),(NONCE,0x100),(KEY,0x100),(AESCTX,0x1000),(BUF,0x400)]:
    mu.mem_write(base, b"\x00"*sz)
mu.mem_write(CONST, const24); mu.mem_write(NONCE, nonce)

# --- clé = SHA256(const24 ‖ nonce) via les fonctions du firmware ---
call(0x80006e4, r0=SHA)                        # sha256_init(ctx)
call(0x800073c, r0=SHA, r1=CONST, r2=24)       # sha256_update(ctx, const24, 24)
call(0x800073c, r0=SHA, r1=NONCE, r2=16)       # sha256_update(ctx, nonce, 16)
call(0x8000774, r0=SHA, r1=KEY)                # sha256_final(ctx, key)
key = bytes(mu.mem_read(KEY, 32))
print("key =", key.hex())

# --- AES-256 du firmware (le main byte-swap le ciphertext par mot de 32 bits) ---
ct_bs = b"".join(ct[i:i+4][::-1] for i in range(0, 48, 4))
mu.mem_write(BUF, ct_bs)
call(0x8000b5e, r0=AESCTX, r1=KEY, r2=NONCE)   # aes_setup(ctx, key, iv=nonce)
call(0x8000bdc, r0=AESCTX, r1=BUF, r2=48)      # aes_decrypt(ctx, buf, 48)
pt = bytes(mu.mem_read(BUF, 48))
print("plaintext =", repr(pt))                 # hiCTF{...} + padding PKCS#7
