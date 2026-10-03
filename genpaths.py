"""Gard Config: per-install secret paths (v7).
Paths look like normal CDN/API traffic for better survival on IR mobile operators.
Old installs keep existing paths; only missing slots are filled."""
import json, os, secrets, uuid

DATA = os.getenv("JINX_DATA", "/var/lib/pasarguard")
OUT_JSON = f"{DATA}/paths.json"
OUT_INC = f"{DATA}/inbounds.inc"

# tag -> (local port, path prefix)  — prefixes look like real web assets / APIs
SLOTS = {
    "JX-VLESS-WS-1":  (10001, "/assets/js/"),
    "JX-VLESS-WS-2":  (10002, "/cdn/static/"),
    "JX-TROJAN-WS":   (10003, "/media/live/"),
    "JX-VMESS-WS":    (10004, "/api/gateway/"),
    "JX-VLESS-HU":    (10005, "/v1/stream/"),
    "JX-VLESS-WS-3":  (10006, "/static/app/"),
    "JX-VLESS-WS-4":  (10007, "/gateway/v2/"),
    "JX-VLESS-HU-2":  (10008, "/edge/relay/"),
}

# legacy paths from older Gard/JinX versions (never break live users)
LEGACY = {
    "JX-VLESS-WS-1":  "/ws/7a5a21d9-60f9-4542-943e-7838b90169e1",
    "JX-VLESS-WS-2":  "/stream/4868e537-9fd8-46e9-b63a-f36459d18a81",
    "JX-TROJAN-WS":   "/live/b1dfa4cc-0ed6-4956-b330-8ccb51dc0828",
    "JX-VMESS-WS":    "/gw/3d801b12-a333-452c-b9d5-90ece1a8d68c",
    "JX-VLESS-HU":    "/cdn/cc046fa3-78ec-4619-ac8f-9d6c7a5d0755",
    "JX-VLESS-WS-3":  "/api/a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "JX-VLESS-WS-4":  "/connect/b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "JX-VLESS-HU-2":  "/gate/c3d4e5f6-a7b8-9012-cdef-123456789012",
}
OBSOLETE = ("JX-VLESS-XHTTP", "JX-TROJAN-HU", "JX-VMESS-HU")

def _rand_path(prefix):
    return prefix + str(uuid.UUID(bytes=secrets.token_bytes(16), version=4))

def load():
    try:
        with open(OUT_JSON) as f:
            p = json.load(f)
        if not isinstance(p, dict):
            return None
        changed = False
        existing = os.path.exists(f"{DATA}/.owner_initialized") or os.path.exists(f"{DATA}/db.sqlite3")
        for t, (_, pre) in SLOTS.items():
            if not (isinstance(p.get(t), str) and p[t].startswith("/")):
                p[t] = LEGACY.get(t) if existing else _rand_path(pre)
                changed = True
        for obsolete in OBSOLETE:
            if obsolete in p:
                del p[obsolete]
                changed = True
        if changed:
            tmp = OUT_JSON + ".tmp"
            with open(tmp, "w") as f:
                json.dump(p, f, indent=1)
            os.replace(tmp, OUT_JSON)
            print("[paths] paths updated (new slots / cleaned obsolete)")
        return p
    except Exception:
        return None

def main():
    os.makedirs(DATA, exist_ok=True)
    p = load()
    if p is None:
        if os.path.exists(f"{DATA}/.owner_initialized") or os.path.exists(f"{DATA}/db.sqlite3"):
            p = dict(LEGACY)
            print("[paths] existing panel detected, keeping old config paths")
        else:
            p = {t: _rand_path(pre) for t, (_, pre) in SLOTS.items()}
            print("[paths] new install: unique CDN-style paths generated")
        tmp = OUT_JSON + ".tmp"
        with open(tmp, "w") as f:
            json.dump(p, f, indent=1)
        os.replace(tmp, OUT_JSON)
    lines = [
        f"location = {p[t]} {{ proxy_pass http://127.0.0.1:{port}; include /etc/nginx/ws.inc; }}"
        for t, (port, _) in SLOTS.items() if t in p
    ]
    with open(OUT_INC, "w") as f:
        f.write("\n".join(lines) + "\n")

if __name__ == "__main__":
    main()
