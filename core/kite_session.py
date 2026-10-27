"""Kite session with a once-a-day login.

The access token is cached in .kite_token.json for the day, so the login runs at most once.
Two ways to log in (keys in .env, see .env.example):
  * Standard Kite Connect flow (needs KITE_API_KEY + KITE_API_SECRET): open the printed URL,
    log in, and paste the request_token from the redirect URL.
  * Automatic: if brokers/kite_connect.py exists and KITE_USER_ID / KITE_PASSWORD /
    KITE_TOTP_SECRET are set, it logs in without prompting.
Only read-only data endpoints are used by this project - never orders.
"""
import json
from datetime import date

from dotenv import dotenv_values
from kiteconnect import KiteConnect
from kiteconnect.exceptions import TokenException

from core.paths import ROOT

ENV_FILE = ROOT / ".env"
TOKEN_FILE = ROOT / ".kite_token.json"
AUTO = ["KITE_USER_ID", "KITE_PASSWORD", "KITE_TOTP_SECRET"]


def _creds() -> dict:
    env = dotenv_values(ENV_FILE)
    missing = [k for k in ("KITE_API_KEY", "KITE_API_SECRET") if not env.get(k)]
    if missing:
        raise SystemExit(f"Missing in {ENV_FILE.name}: {', '.join(missing)} (see .env.example)")
    return env


def _cached_client(api_key: str):
    if not TOKEN_FILE.exists():
        return None
    cached = json.loads(TOKEN_FILE.read_text())
    if cached.get("date") != date.today().isoformat():
        return None
    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(cached["access_token"])
    try:
        kite.profile()
    except TokenException:
        return None
    return kite


def _login(env: dict) -> KiteConnect:
    if all(env.get(k) for k in AUTO) and (ROOT / "brokers" / "kite_connect.py").exists():
        from brokers.kite_connect import KiteConnect2

        return KiteConnect2(user_id=env["KITE_USER_ID"], api_secret=env["KITE_API_SECRET"], two_fa=env["KITE_TOTP_SECRET"],
                            password=env["KITE_PASSWORD"], api_key=env["KITE_API_KEY"])
    kite = KiteConnect(api_key=env["KITE_API_KEY"])
    print(f"Log in to Kite here, then copy request_token=... from the URL you land on:\n  {kite.login_url()}")
    token = input("request_token: ").strip()
    kite.set_access_token(kite.generate_session(token, api_secret=env["KITE_API_SECRET"])["access_token"])
    return kite


def get_kite() -> KiteConnect:
    env = _creds()
    kite = _cached_client(env["KITE_API_KEY"]) or _login(env)
    TOKEN_FILE.write_text(json.dumps({"date": date.today().isoformat(), "access_token": kite.access_token}))
    TOKEN_FILE.chmod(0o600)
    return kite
