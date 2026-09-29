<p align="center">
  <img src="header.png" alt="Abraxas Labs — uptime-kuma-setup-toctou" width="100%">
</p>

<p align="center">
  <a href="https://abraxaslabs.tech"><strong>abraxaslabs.tech</strong></a>
  &nbsp;·&nbsp;
  <a href="https://github.com/abraxas">github.com/abraxas</a>
  &nbsp;·&nbsp;
  <a href="https://x.com/abraxas_null">@abraxas_null</a>
  &nbsp;·&nbsp;
  <a href="https://github.com/abraxas/uptime-kuma-setup-toctou">uptime-kuma-setup-toctou</a>
</p>

# uptime-kuma-setup-toctou

**Uptime Kuma** `2.5.5` — Louis Lam

Unpublished Uptime Kuma source finding: concurrent unauthenticated Socket.IO setup on first-run can insert a hidden second admin, then that account can set disableAuth so new sockets auto-login as user id 1. setup does COUNT(user) then bcryptjs.hash cost 10 then INSERT. Username is UNIQUE only; there is no one-row constraint.

| | |
|---|---|
| ID | Unpublished Uptime Kuma source finding #1 (no CVE yet) |
| CWE | [CWE-362, CWE-367](https://cwe.mitre.org/data/definitions/367.html) |
| CVSS | **High: 7.4** `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N` |
| Product | [Uptime Kuma](https://github.com/louislam/uptime-kuma) |
| Affected | all versions **through 2.5.5** (inclusive) |
| Patched | vendor patch — see references |
| Auth | unauthenticated (see source map) |
| License | [GNU Affero GPL v3.0](LICENSE) |
| Lab | `127.0.0.1` only · vendor/client disclosure pack, not a scanner |

---

## Advisory (from the source map)

server.js 705-720 COUNT then bcrypt then INSERT. password-hash.js 10-12 bcrypt.hash cost 10. knex_init_db.js 54-56 username UNIQUE only. setSettings 1505-1517 disableAuth after doubleCheckPassword on socket.userID. auto-login 1757-1760 R.findOne(user) lowest id.

---

## Entry

- **Method:** `SOCKET.IO`
- **Path:** `setup`
- **Router:** socket.on setup in server/server.js. COUNT user then passwordHash.generate then R.store. No transaction, no mutex, no one-row constraint.
- **Notes:** Unauthenticated unpublished Uptime Kuma #1 CWE-362 2.5.5. First-run only. Already-connected sockets emit setup in the same poll. Witness: sqlite 1|labadmin 2|UK-SETUP-TOCTOU-WITNESS. Late sequential setup rejected. Extra user can disableAuth. Not eval. Not a reverse shell. Disclose GitHub private advisory, not a public vendor issue.

### Call chain

- `Connect N Socket.IO clients while the user table is empty`
- `Barrier-emit setup(labadmin) and setup(UK-SETUP-TOCTOU-WITNESS)`
- `sqlite SELECT id, username FROM user ORDER BY id`
- `Sequential setup after the race is rejected (initialized)`
- `Extra user emits login then setSettings disableAuth=true`
- `Reconnect autoLogin; prepare2FA otpauth identity is user id 1`

### Lab preconditions

- Uptime Kuma 2.5.5 with an empty user table (first-run /setup)
- UPTIME_KUMA_DB_TYPE=sqlite so the v2 database wizard is skipped
- Default product listen is 0.0.0.0:3001; lab binds 127.0.0.1:18141
- Already-connected Socket.IO clients emit setup in the same poll

### Witness

sqlite user rows 1|labadmin and 2|UK-SETUP-TOCTOU-WITNESS; late setup rejected as initialized; extra user sets disableAuth; reconnect autoLogin prepare2FA otpauth is labadmin (id 1)

### Not success

- eval/base64/system payload
- reverse shell
- single user row after concurrent setup
- UK-SETUP-TOCTOU-WITNESS missing from the user table
- sequential late setup accepted after the race

---

## Patch / remediation

**Do this first:** Apply the vendor patch for **Uptime Kuma**. See references.

**Verify after upgrade**

- Re-run `uptime-kuma-setup-toctou-Abraxas-Labs.py` against the patched build: the mapped witness must **not** appear.
- Confirm the vendor advisory / changeset in the deployed tree (see references).
- A WAF signature is delay, not a patch.

**If you cannot update immediately**

- Disable or isolate the affected component.
- Hunt for the witness condition on production (new privileged users, unexpected files, injected rows — whatever this CVE's map names).

---

## Reproduction (authorized lab)

Target **only** `http://127.0.0.1:18141` (or the loopback you bound). Do not point this script at the internet.

```bash
python3 uptime-kuma-setup-toctou-Abraxas-Labs.py
```

Success is the **witness** above in the response body. Generic 200 HTML is not it.

---

## Lab images

Loopback stack used to reproduce. Official images unless a `Dockerfile` in this folder builds from source.

- [`lab/docker-compose.yml`](lab/docker-compose.yml)
- [`lab/Dockerfile`](lab/Dockerfile)
- [`lab/run.sh`](lab/run.sh)
- [`lab/poc.py`](lab/poc.py)
- [`lab/requirements.txt`](lab/requirements.txt)

`./run.sh` starts `louislam/uptime-kuma:2.5.5` on loopback `:18141` (`UPTIME_KUMA_DB_TYPE=sqlite`) and runs the Socket.IO race.

```bash
cd lab
./run.sh
```

Publish nothing except `127.0.0.1`.

---

## References

- [github.com/louislam/uptime-kuma](https://github.com/louislam/uptime-kuma) tag 2.5.5
- Vendor intake: [GitHub private advisory](https://github.com/louislam/uptime-kuma/security/advisories/new) plus an empty [security issue](https://github.com/louislam/uptime-kuma/issues/new?assignees=&labels=help&template=security.md) ([SECURITY.md](https://github.com/louislam/uptime-kuma/blob/2.5.5/SECURITY.md)). Do **not** open a public GitHub issue.

- Abraxas Labs: [abraxaslabs.tech](https://abraxaslabs.tech) · [github.com/abraxas](https://github.com/abraxas) · [@abraxas_null](https://x.com/abraxas_null)

---

## Records (structured)

```
# Uptime Kuma unpublished #1 — concurrent setup TOCTOU

CWE: CWE-362, CWE-367
Severity: High (HTTP/Socket.IO lab SUCCESS, 95%)

## Description

Unauthenticated Socket.IO `setup` on first-run does `COUNT(user)` then `bcryptjs.hash` cost 10 then `INSERT`. There is no transaction, mutex, or one-row constraint (username UNIQUE only). Concurrent already-connected clients can insert a hidden second admin. That account can set `disableAuth`; reconnect auto-login is `R.findOne("user")` = user id 1.

## Product

Uptime Kuma tag 2.5.5 (`c98982a`); lab image `louislam/uptime-kuma:2.5.5` on loopback `:18141`. Oracle: sqlite `1|labadmin` `2|UK-SETUP-TOCTOU-WITNESS`; late setup rejected; `disableAuth` auto-login identity is labadmin.
```

---

## License

This disclosure pack is licensed under the **GNU Affero General Public License v3.0**. See [LICENSE](LICENSE).

---

## Disclaimer

This pack is for **the vendor, the site owner, and licensed labs**. The script talks to `127.0.0.1`. Using it against systems you do not own is not authorized by Abraxas Labs. No warranty.

<p align="center">
  <a href="https://abraxaslabs.tech">abraxaslabs.tech</a> ·
  <a href="https://github.com/abraxas">github.com/abraxas</a> ·
  <a href="https://x.com/abraxas_null">@abraxas_null</a>
</p>
