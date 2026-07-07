#!/usr/bin/env python3
"""Onboard a fresh Home Assistant instance and create a long-lived access token.

Creates the admin/admin123 account, completes onboarding steps, and prints a
long-lived access token to stdout. Designed to work even when the onboarding
users endpoint hits a translation bug (falls back to the login flow).

Usage:
    python3 onboard_ha.py [HA_URL]

Prints the long-lived access token to stdout (all other output goes to stderr).
"""

import sys
import time
import urllib.request
import urllib.error
import json
import asyncio
import websockets

HA_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8123"
CLIENT_ID = HA_URL + "/"
USERNAME = "admin"
PASSWORD = "admin123"


def _post(path, payload, token=None, form=False):
    url = HA_URL + path
    data = (
        "&".join(f"{k}={urllib.parse.quote(v, safe='')}" for k, v in payload.items())
        if form
        else json.dumps(payload).encode()
    )
    headers = {"Content-Type": "application/x-www-form-urlencoded"} if form else {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data.encode() if form else data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def _get(path):
    try:
        with urllib.request.urlopen(HA_URL + path, timeout=10) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def wait_for_ha(timeout=120):
    for _ in range(timeout // 2):
        try:
            status, body = _get("/api/onboarding")
            if status == 200:
                return json.loads(body)
        except Exception:
            pass
        time.sleep(2)
    raise RuntimeError("HA did not become ready in time")


def onboarding_status():
    _, body = _get("/api/onboarding")
    return json.loads(body)


def create_user_via_onboarding():
    """Try the onboarding users endpoint. Returns auth_code or None on failure."""
    status, body = _post("/api/onboarding/users", {
        "name": "admin", "username": USERNAME, "password": PASSWORD,
        "client_id": CLIENT_ID, "language": "en",
    })
    if status == 200:
        return json.loads(body).get("auth_code")
    print(f"[onboard] users endpoint returned {status}, falling back to login flow", file=sys.stderr)
    return None


def login_flow_get_token():
    """Authenticate via the login flow (works if credentials already exist)."""
    status, body = _post("/auth/login_flow", {
        "client_id": CLIENT_ID, "handler": ["homeassistant", None], "redirect_uri": CLIENT_ID,
    })
    if status != 200:
        raise RuntimeError(f"login_flow init failed: {status} {body}")
    flow_id = json.loads(body)["flow_id"]

    status, body = _post(f"/auth/login_flow/{flow_id}", {
        "client_id": CLIENT_ID, "username": USERNAME, "password": PASSWORD,
    })
    if status != 200:
        raise RuntimeError(f"login_flow submit failed: {status} {body}")
    auth_code = json.loads(body).get("result")
    if not auth_code:
        raise RuntimeError(f"login_flow did not return a result: {body}")

    status, body = _post("/auth/token", {
        "grant_type": "authorization_code", "code": auth_code, "client_id": CLIENT_ID,
    }, form=True)
    if status != 200:
        raise RuntimeError(f"token exchange failed: {status} {body}")
    return json.loads(body)["access_token"]


def exchange_auth_code(auth_code):
    status, body = _post("/auth/token", {
        "grant_type": "authorization_code", "code": auth_code, "client_id": CLIENT_ID,
    }, form=True)
    if status != 200:
        raise RuntimeError(f"token exchange failed: {status} {body}")
    return json.loads(body)["access_token"]


def finish_remaining_onboarding(token):
    steps = onboarding_status()
    for step in (s["step"] for s in steps if not s["done"]):
        if step == "user":
            continue
        payload = {"client_id": CLIENT_ID, "redirect_uri": CLIENT_ID} if step == "integration" else {}
        _post(f"/api/onboarding/{step}", payload, token=token)


def create_long_lived_token(access_token):
    async def _ws():
        async with websockets.connect(f"{HA_URL.replace('http', 'ws')}/api/websocket") as ws:
            assert json.loads(await ws.recv())["type"] == "auth_required"
            await ws.send(json.dumps({"type": "auth", "access_token": access_token}))
            assert json.loads(await ws.recv())["type"] == "auth_ok"
            await ws.send(json.dumps({
                "id": 1, "type": "auth/long_lived_access_token",
                "client_name": "integration_tests", "lifespan": 365,
            }))
            msg = json.loads(await ws.recv())
            if not msg.get("success"):
                raise RuntimeError(f"LLT creation failed: {msg}")
            return msg["result"]
    return asyncio.run(_ws())


def main():
    print(f"[onboard] Waiting for HA at {HA_URL}...", file=sys.stderr)
    wait_for_ha()
    status = onboarding_status()
    user_done = next((s for s in status if s["step"] == "user"), None)["done"]

    auth_code = None
    if not user_done:
        auth_code = create_user_via_onboarding()

    if auth_code:
        print("[onboard] User created via onboarding endpoint", file=sys.stderr)
        access_token = exchange_auth_code(auth_code)
    else:
        print("[onboard] Logging in via login flow", file=sys.stderr)
        access_token = login_flow_get_token()

    print("[onboard] Finishing remaining onboarding steps...", file=sys.stderr)
    finish_remaining_onboarding(access_token)

    print("[onboard] Creating long-lived access token...", file=sys.stderr)
    llt = create_long_lived_token(access_token)

    print("[onboard] Done.", file=sys.stderr)
    print(llt)


if __name__ == "__main__":
    main()
