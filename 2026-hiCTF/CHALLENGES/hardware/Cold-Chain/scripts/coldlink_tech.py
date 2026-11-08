#!/usr/bin/env python3
"""
ColdLink Technician Toolkit  (field service client for CM-900 case managers)
----------------------------------------------------------------------------
ColdLink Refrigeration Systems -- Authorized Service Partners only.

This utility speaks CLMP/1.1 to a ColdLink CaseManager CM-900 over TCP and
lets a field technician read case temperatures, inspect schedules and
maintenance macros, and apply corrections.

Quick start:
    python3 coldlink_tech.py --host <ip> --port 7601 cases
    python3 coldlink_tech.py --host <ip> --port 7601 sched-list
    python3 coldlink_tech.py --host <ip> --port 7601 status
    python3 coldlink_tech.py --host <ip> --port 7601 raw "SCHED GET S9"

See CLMP_reference.md for the full command/register reference, and
historian_sample.log for an example of the controller's event feed
(default historian port 7602).
"""

import argparse
import hashlib
import socket
import sys

# ---------------------------------------------------------------------------
# Field service authentication.
#
# CM-900 controllers authenticate technicians with a challenge/response: the
# controller presents its SERIAL and a per-connection NONCE in the greeting,
# and the toolkit answers with a token derived from the ColdLink field master
# key provisioned below. This master key is common to the CM-900 fleet; keep
# this toolkit on authorized service laptops only.
# ---------------------------------------------------------------------------
FIELD_MASTER_KEY = "CLNK-FIELD-MASTER-6E1D-DO-NOT-DISTRIBUTE"


def auth_token(serial: str, nonce_hex: str) -> str:
    material = "%s|%s|%s" % (FIELD_MASTER_KEY, serial, nonce_hex)
    return hashlib.sha256(material.encode()).hexdigest()[:16]


class Client:
    def __init__(self, host, port, timeout=10.0):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.f = self.sock.makefile("rwb", buffering=0)
        self.serial = None
        self.nonce = None
        self._read_greeting()

    def _readline(self):
        raw = self.f.readline()
        if not raw:
            raise ConnectionError("connection closed by controller")
        return raw.decode("utf-8", "replace").rstrip("\n")

    def _read_greeting(self):
        # Greeting ends with a line beginning "OK".
        while True:
            line = self._readline()
            if line.startswith("SERIAL "):
                self.serial = line.split(None, 1)[1].strip()
            elif line.startswith("NONCE "):
                self.nonce = line.split(None, 1)[1].strip()
            elif line.startswith("OK") or line.startswith("ERR"):
                break

    def send(self, cmd):
        self.f.write((cmd + "\n").encode())
        lines = []
        while True:
            line = self._readline()
            if line.startswith("OK") or line.startswith("ERR"):
                lines.append(line)
                break
            lines.append(line)
        return lines

    def authenticate(self):
        if not self.serial or not self.nonce:
            raise RuntimeError("controller did not present serial/nonce")
        token = auth_token(self.serial, self.nonce)
        resp = self.send("AUTH %s %s" % (self.serial, token))
        if not resp[-1].startswith("OK"):
            raise RuntimeError("auth failed: %s" % resp[-1])
        return resp[-1]

    def close(self):
        try:
            self.send("QUIT")
        except Exception:
            pass
        try:
            self.f.close()
            self.sock.close()
        except Exception:
            pass


def main():
    ap = argparse.ArgumentParser(description="ColdLink Technician Toolkit")
    ap.add_argument("--host", required=True)
    ap.add_argument("--port", type=int, default=7601)
    ap.add_argument("command", help="cases|sched-list|sched-get|macro-list|"
                                     "macro-get|status|raw")
    ap.add_argument("args", nargs="*")
    opts = ap.parse_args()

    c = Client(opts.host, opts.port)
    print("[*] connected: serial=%s nonce=%s" % (c.serial, c.nonce))
    try:
        c.authenticate()
        print("[*] authenticated as technician")

        cmd = opts.command.lower()
        if cmd == "cases":
            out = c.send("CASES")
        elif cmd == "sched-list":
            out = c.send("SCHED LIST")
        elif cmd == "sched-get":
            out = c.send("SCHED GET %s" % opts.args[0])
        elif cmd == "macro-list":
            out = c.send("MACRO LIST")
        elif cmd == "macro-get":
            out = c.send("MACRO GET %s" % opts.args[0])
        elif cmd == "status":
            out = c.send("STATUS")
        elif cmd == "raw":
            out = c.send(" ".join(opts.args))
        else:
            print("unknown command: %s" % cmd)
            sys.exit(2)

        for line in out:
            print(line)
    finally:
        c.close()


if __name__ == "__main__":
    main()
